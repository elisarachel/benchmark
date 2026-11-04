"""Linha de comando: ``pm25bench run | models | fetch | stations``."""

from __future__ import annotations

import argparse
from collections.abc import Sequence


def _run(args: argparse.Namespace) -> int:
    from pm25bench.benchmark import load_config, run_benchmark, write_report

    cfg = load_config(args.config)
    if args.output:
        cfg.output_dir = args.output
    result = run_benchmark(cfg)
    board = write_report(result, cfg.output_dir)
    print(board.read_text(encoding="utf-8"))
    print(f"resultados em {cfg.output_dir}/")
    return 0


def _models(args: argparse.Namespace) -> int:
    from pm25bench.models import available

    print("\n".join(available()))
    return 0


def _fetch(args: argparse.Namespace) -> int:
    from pm25bench.data.fetch import fetch_data

    sisam, cetesb = fetch_data(args.station, args.dest)
    print(f"SISAM:  {sisam}\nCETESB: {cetesb}")
    return 0


def _stations(args: argparse.Namespace) -> int:
    from pm25bench.data import stations

    table = stations()
    if not args.all:
        table = table[table["mp25"] == "ativo"]
    print(table[["estacao", "municipio", "cd_mun"]].to_string())
    return 0


def build_parser() -> argparse.ArgumentParser:
    from pm25bench import __version__

    p = argparse.ArgumentParser(prog="pm25bench", description=__doc__)
    p.add_argument("--version", action="version", version=f"pm25bench {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="roda o benchmark descrito num YAML")
    run.add_argument("config")
    run.add_argument("-o", "--output", help="pasta de saída (sobrescreve o YAML)")
    run.set_defaults(func=_run)

    models = sub.add_parser("models", help="lista os modelos instalados")
    models.set_defaults(func=_models)

    fetch = sub.add_parser("fetch", help="baixa os dados para o cache local")
    fetch.add_argument("--station", type=int, default=73)
    fetch.add_argument("--dest", default=None)
    fetch.set_defaults(func=_fetch)

    st = sub.add_parser("stations", help="lista as estações da CETESB com MP2,5")
    st.add_argument("--all", action="store_true", help="inclui estações sem MP2,5 ativo")
    st.set_defaults(func=_stations)
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
