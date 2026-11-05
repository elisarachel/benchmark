"""Executa o benchmark: para cada modelo e cada amostra de teste, prever e medir."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from pm25bench.benchmark.config import BenchmarkConfig
from pm25bench.data import Sample, dataset_hash, make_samples, split_by_time
from pm25bench.metrics import (
    bias,
    block_bootstrap_ci,
    csi,
    ets,
    far,
    frequency_bias,
    mae,
    pearson_r,
    pod,
    rmse,
)
from pm25bench.models import Forecaster, check_prediction, load_model


@dataclass
class BenchmarkResult:
    """Resultado de uma execução."""

    predictions: pd.DataFrame
    scores: pd.DataFrame
    metadata: dict[str, Any] = field(default_factory=dict)


def predict_samples(model: Forecaster, samples: list[Sample], leads: list[int]) -> pd.DataFrame:
    """Roda ``model.predict`` em todas as amostras e devolve uma tabela longa."""
    rows = []
    for s in samples:
        pred = check_prediction(model.predict(s.context, leads), leads, model.name)
        for j, lead in enumerate(leads):
            rows.append(
                {
                    "model": model.name,
                    "issue_date": s.issue_date,
                    "lead": lead,
                    "target_date": s.issue_date + pd.Timedelta(days=lead),
                    "obs": s.target[j],
                    "pred": pred[j],
                }
            )
    return pd.DataFrame(rows)


def score_predictions(
    predictions: pd.DataFrame,
    thresholds: list[float],
    block_days: int = 7,
    n_boot: int = 1000,
    seed: int = 42,
) -> pd.DataFrame:
    """Calcula as métricas por modelo e lead, com IC 95% por bootstrap em blocos."""
    rows = []
    for (name, lead), g in predictions.groupby(["model", "lead"], sort=False):
        o, f = g["obs"].to_numpy(), g["pred"].to_numpy()
        days = (g["issue_date"] - pd.Timestamp("1970-01-01")).dt.days.to_numpy()
        blocks = days // block_days
        row: dict[str, Any] = {
            "model": name,
            "lead": lead,
            "n": len(g),
            "mae": mae(o, f),
            "rmse": rmse(o, f),
            "bias": bias(o, f),
            "r": pearson_r(o, f),
        }
        if n_boot:
            row["mae_lo"], row["mae_hi"] = block_bootstrap_ci(o, f, blocks, mae, n_boot, seed=seed)
        for thr in thresholds:
            t = f"{thr:g}"
            row[f"pod_{t}"] = pod(o, f, thr)
            row[f"far_{t}"] = far(o, f, thr)
            row[f"csi_{t}"] = csi(o, f, thr)
            row[f"ets_{t}"] = ets(o, f, thr)
            row[f"fbias_{t}"] = frequency_bias(o, f, thr)
            if n_boot:

                def metric(a: np.ndarray, b: np.ndarray, thr: float = thr) -> float:
                    return csi(a, b, thr)

                lo, hi = block_bootstrap_ci(o, f, blocks, metric, n_boot, seed=seed)
                row[f"csi_{t}_lo"], row[f"csi_{t}_hi"] = lo, hi
        rows.append(row)
    return pd.DataFrame(rows)


def run_benchmark(cfg: BenchmarkConfig, df: pd.DataFrame | None = None) -> BenchmarkResult:
    """Executa o benchmark descrito em ``cfg``.

    Parameters
    ----------
    cfg : BenchmarkConfig
        Configuração validada.
    df : pandas.DataFrame, optional
        Tabela diária já carregada; se omitida, é carregada a partir de ``cfg.data``.
    """
    from pm25bench import __version__

    if df is None:
        df = cfg.data.load()
    d = cfg.data
    train, val, test = split_by_time(df, d.train_end, d.val_end, d.gap_days)
    samples = list(make_samples(test, cfg.n_context, cfg.leads))
    if not samples:
        raise ValueError("o conjunto de teste não tem amostras válidas")
    parts = []
    for spec in cfg.models:
        model = load_model(spec.name, **spec.kwargs)
        model.fit(train, val)
        parts.append(predict_samples(model, samples, cfg.leads))
    predictions = pd.concat(parts, ignore_index=True)
    scores = score_predictions(predictions, cfg.thresholds, cfg.block_days, cfg.n_boot, cfg.seed)
    metadata = {
        "pm25bench_version": __version__,
        "dataset_hash": dataset_hash(df),
        "station": int(df.attrs.get("station", d.station)),
        "n_test_samples": len(samples),
        "test_period": [str(test.index.min().date()), str(test.index.max().date())],
        "config": cfg.model_dump(mode="json"),
        # trilha de previsão do CAMS (False no contrato padrão)
        "forecast": bool(df.attrs.get("forecast", False)),
    }
    return BenchmarkResult(predictions=predictions, scores=scores, metadata=metadata)
