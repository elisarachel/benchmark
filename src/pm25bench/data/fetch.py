"""Download dos dados sob demanda, com cache local e verificação de hash (pooch).

Os dados não vão dentro do pacote: são baixados dos repositórios da turma, num commit fixado,
para que todos usem exatamente os mesmos arquivos.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import pooch

from pm25bench.data._registry import CETESB_REGISTRY, SISAM_REGISTRY

SISAM_REPO = "RyanAlvesQ/benchmark_cap_408"
SISAM_REF = "342d88a0d3f34b2a0e8da55403cefc8e1ce70388"
SISAM_FOLDER = "dados_sisam_zip_reanalise_2010_2024"

CETESB_REPO = "elisarachel/benchmark_pm2_5"
CETESB_REF = "056189ca445feaa6ebeb516d8a6a425676001d11"
CETESB_YEARS = range(2008, 2027)


def _raw(repo: str, ref: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{repo}/{ref}/{path}"


def default_cache() -> Path:
    """Diretório de cache (``~/.cache/pm25bench`` no Linux)."""
    return Path(pooch.os_cache("pm25bench"))


def fetch_sisam(dest: str | Path | None = None) -> Path:
    """Baixa os ZIPs anuais do SISAM e devolve o diretório onde ficaram."""
    folder = Path(dest or default_cache()) / "sisam"
    for name, known_hash in SISAM_REGISTRY.items():
        pooch.retrieve(
            _raw(SISAM_REPO, SISAM_REF, f"{SISAM_FOLDER}/{name}"),
            known_hash=known_hash,
            fname=name,
            path=folder,
            progressbar=False,
        )
    return folder


def fetch_cetesb(station: int = 73, dest: str | Path | None = None) -> Path:
    """Baixa os CSVs anuais de uma estação e devolve o diretório-raiz (``<raiz>/<estação>/``).

    Só a estação 73 tem hashes registrados; para as outras o download é feito sem verificação
    e um aviso é emitido.
    """
    root = Path(dest or default_cache()) / "cetesb"
    unchecked = False
    for year in CETESB_YEARS:
        rel = f"{station}/{year}.csv"
        known = CETESB_REGISTRY.get(rel)
        if station != 73:
            unchecked = True
        elif known is None:
            continue
        try:
            pooch.retrieve(
                _raw(CETESB_REPO, CETESB_REF, f"data/{rel}"),
                known_hash=known,
                fname=f"{year}.csv",
                path=root / str(station),
                progressbar=False,
            )
        except Exception:  # noqa: BLE001 - ano inexistente para a estação
            if known is not None:
                raise
    if unchecked:
        warnings.warn(
            f"estação {station}: arquivos baixados sem verificação de hash",
            stacklevel=2,
        )
    return root


def fetch_data(station: int = 73, dest: str | Path | None = None) -> tuple[Path, Path]:
    """Baixa tudo o que o benchmark precisa. Devolve ``(sisam_dir, cetesb_dir)``."""
    return fetch_sisam(dest), fetch_cetesb(station, dest)
