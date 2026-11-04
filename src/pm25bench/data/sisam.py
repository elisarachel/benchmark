"""Leitura da reanálise do SISAM (médias diárias por município)."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pandas as pd

#: Colunas de poluentes no arquivo original -> nome usado no pm25bench.
SISAM_COLUMNS: dict[str, str] = {
    "pm2_5_reanalise": "rea_pm2_5",
    "pm10_reanalise": "rea_pm10",
    "o3_reanalise": "rea_o3",
    "no2_reanalise": "rea_no2",
    "co_reanalise": "rea_co",
    "so2_reanalise": "rea_so2",
}

#: Nomes das variáveis de reanálise entregues aos modelos, na ordem fixa.
REANALYSIS_FEATURES: list[str] = list(SISAM_COLUMNS.values())


def sisam_files(directory: str | Path) -> list[Path]:
    """Lista os arquivos anuais (``.csv`` ou ``.zip``) de um diretório do SISAM.

    Se houver ``.csv`` e ``.zip`` do mesmo ano, o ``.csv`` é usado.
    """
    directory = Path(directory)
    by_stem: dict[str, Path] = {}
    for path in sorted(directory.glob("sisam_municipio_reanalise_diario_*")):
        if path.suffix not in {".csv", ".zip"}:
            continue
        if path.stem not in by_stem or path.suffix == ".csv":
            by_stem[path.stem] = path
    if not by_stem:
        raise FileNotFoundError(f"nenhum arquivo do SISAM encontrado em {directory}")
    return [by_stem[k] for k in sorted(by_stem)]


def read_sisam(files: Iterable[str | Path], cd_mun: int) -> pd.DataFrame:
    """Lê a reanálise de um município.

    Parameters
    ----------
    files : iterable of path
        Arquivos anuais do SISAM (CSV ou ZIP com um CSV dentro).
    cd_mun : int
        Código IBGE do município (7 dígitos), por exemplo 3550308 para São Paulo.

    Returns
    -------
    pandas.DataFrame
        Índice diário ``date`` e uma coluna por poluente (``rea_pm2_5``, ``rea_pm10``, ...),
        em µg/m³ (CO em ppm, como no produto original).
    """
    usecols = ["CD_MUN", "data", *SISAM_COLUMNS]
    parts = []
    for path in files:
        df = pd.read_csv(path, usecols=usecols, encoding="utf-8-sig")
        df = df[df["CD_MUN"] == cd_mun]
        parts.append(df)
    if not parts:
        raise ValueError("nenhum arquivo informado")
    out = pd.concat(parts, ignore_index=True)
    if out.empty:
        raise ValueError(f"município {cd_mun} não encontrado nos arquivos do SISAM")
    out["date"] = pd.to_datetime(out["data"], format="%d/%m/%Y")
    out = out.drop(columns=["CD_MUN", "data"]).rename(columns=SISAM_COLUMNS)
    out = out.drop_duplicates("date").set_index("date").sort_index()
    return out[REANALYSIS_FEATURES].astype("float64")
