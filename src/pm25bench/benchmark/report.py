"""Grava os resultados: CSVs, leaderboard em Markdown, metadados e figuras."""

from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

import pandas as pd

from pm25bench.benchmark.runner import BenchmarkResult


def leaderboard_markdown(scores: pd.DataFrame, thresholds: list[float]) -> str:
    """Tabela Markdown: uma linha por modelo e lead."""
    thr_mid = f"{thresholds[len(thresholds) // 2]:g}" if thresholds else None
    header = ["modelo", "lead (d)", "n", "MAE", "IC 95% MAE", "RMSE", "viés", "r"]
    if thr_mid:
        header += [f"CSI@{thr_mid}", f"POD@{thr_mid}", f"FAR@{thr_mid}"]
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for _, r in scores.sort_values(["lead", "mae"]).iterrows():
        ci = f"[{r['mae_lo']:.2f}, {r['mae_hi']:.2f}]" if "mae_lo" in r else "–"
        cells = [
            str(r["model"]),
            str(r["lead"]),
            str(r["n"]),
            f"{r['mae']:.2f}",
            ci,
            f"{r['rmse']:.2f}",
            f"{r['bias']:+.2f}",
            f"{r['r']:.2f}",
        ]
        if thr_mid:
            cells += [f"{r[f'{m}_{thr_mid}']:.2f}" for m in ("csi", "pod", "far")]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def plot_by_lead(scores: pd.DataFrame, column: str, path: Path, ylabel: str) -> None:
    """Uma curva por modelo da métrica ``column`` em função do lead."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 4))
    for name, g in scores.groupby("model", sort=False):
        g = g.sort_values("lead")
        ax.plot(g["lead"], g[column], marker="o", label=str(name))
        lo, hi = f"{column}_lo", f"{column}_hi"
        if lo in g and hi in g:
            ax.fill_between(g["lead"], g[lo], g[hi], alpha=0.15)
    ax.set_xlabel("lead (dias)")
    ax.set_ylabel(ylabel)
    ax.set_xticks(sorted(scores["lead"].unique()))
    ax.grid(alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def write_report(result: BenchmarkResult, output_dir: str | Path) -> Path:
    """Grava tudo em ``output_dir`` e devolve o caminho do leaderboard."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    result.predictions.to_csv(out / "predictions.csv", index=False)
    result.scores.to_csv(out / "scores.csv", index=False)
    meta = dict(result.metadata)
    meta["python"] = sys.version.split()[0]
    meta["platform"] = platform.platform()
    (out / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    thresholds = list(meta.get("config", {}).get("thresholds", []))
    md = ["# Leaderboard pm25bench", ""]
    md.append(
        f"Estação {meta.get('station')} · teste {' a '.join(meta.get('test_period', []))} · "
        f"{meta.get('n_test_samples')} amostras · pm25bench {meta.get('pm25bench_version')}"
    )
    # aviso de trilha: resultados com previsão do CAMS não se comparam com o padrão
    if meta.get("forecast"):
        md += ["", "Trilha: previsão do CAMS (não comparável com o leaderboard padrão)"]
    md += ["", f"Dados: `{meta.get('dataset_hash')}`", ""]
    md.append(leaderboard_markdown(result.scores, thresholds))
    board = out / "leaderboard.md"
    board.write_text("\n".join(md), encoding="utf-8")
    plot_by_lead(result.scores, "mae", out / "mae_by_lead.png", "MAE (µg/m³)")
    for thr in thresholds:
        t = f"{thr:g}"
        plot_by_lead(result.scores, f"csi_{t}", out / f"csi_{t}_by_lead.png", f"CSI @ {t} µg/m³")
    return board
