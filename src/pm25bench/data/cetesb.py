"""Leitura das observações horárias de MP2,5 das estações da CETESB."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

import pandas as pd


def stations() -> pd.DataFrame:
    """Tabela de estações da CETESB (código, nome, município, ``cd_mun``, lat, lon)."""
    with resources.files("pm25bench.data").joinpath("stations.csv").open(encoding="utf-8") as f:
        return pd.read_csv(f).set_index("codigo")


def station_cd_mun(station: int) -> int:
    """Código IBGE do município onde fica a estação."""
    table = stations()
    if station not in table.index:
        raise KeyError(f"estação {station} não está na tabela da CETESB")
    return int(table["cd_mun"].to_dict()[station])


def read_station_hourly(directory: str | Path, station: int) -> pd.Series:
    """Lê todos os anos de uma estação: ``<directory>/<station>/<ano>.csv``.

    Returns
    -------
    pandas.Series
        MP2,5 horário em µg/m³, indexado pelo horário original da CETESB.
    """
    folder = Path(directory) / str(station)
    files = sorted(folder.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"nenhum CSV da estação {station} em {folder}")
    parts = [pd.read_csv(f) for f in files]
    df = pd.concat([p for p in parts if not p.empty], ignore_index=True)
    df["datetime"] = pd.to_datetime(df["datetime"])
    s = df.drop_duplicates("datetime").set_index("datetime")["value"].astype("float64")
    s.name = "obs"
    return s.sort_index()


def daily_mean(hourly: pd.Series, min_hours: int = 18) -> pd.Series:
    """Média diária a partir dos dados horários.

    A CETESB registra a última hora do dia como 00:00 do dia seguinte (hora 24). Por isso os
    horários são deslocados em 1 h antes de agrupar: o dia D cobre de 01:00 de D até 00:00 de D+1.

    Parameters
    ----------
    hourly : pandas.Series
        Série horária em µg/m³.
    min_hours : int
        Mínimo de horas válidas para o dia contar (padrão 18, ou 75% do dia).

    Returns
    -------
    pandas.Series
        Média diária, ``NaN`` nos dias com menos de ``min_hours`` horas válidas.
    """
    shifted = hourly.dropna()
    shifted.index = (pd.DatetimeIndex(shifted.index) - pd.Timedelta(hours=1)).normalize()
    grouped = shifted.groupby(level=0)
    mean = grouped.mean()
    mean[grouped.count() < min_hours] = float("nan")
    mean.index.name = "date"
    mean.name = "obs"
    return mean
