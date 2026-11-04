"""Monta a tabela diária do benchmark: observação da estação + reanálise do município."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

from pm25bench.data.cetesb import daily_mean, read_station_hourly, station_cd_mun
from pm25bench.data.sisam import REANALYSIS_FEATURES, read_sisam, sisam_files

#: Nome da coluna alvo (MP2,5 diário observado na estação, µg/m³).
TARGET = "obs"


def build_dataset(
    sisam_dir: str | Path,
    cetesb_dir: str | Path,
    station: int = 73,
    min_hours: int = 18,
) -> pd.DataFrame:
    """Tabela diária com a coluna ``obs`` e as colunas ``rea_*``.

    O período é o da reanálise; dias sem observação válida ficam com ``obs = NaN``.
    """
    rea = read_sisam(sisam_files(sisam_dir), station_cd_mun(station))
    obs = daily_mean(read_station_hourly(cetesb_dir, station), min_hours=min_hours)
    full_index = pd.date_range(rea.index.min(), rea.index.max(), freq="D", name="date")
    df = rea.reindex(full_index)
    df.insert(0, TARGET, obs.reindex(full_index))
    df.attrs["station"] = station
    return df


def dataset_hash(df: pd.DataFrame) -> str:
    """SHA-256 do conteúdo da tabela (para registrar no resultado de cada execução)."""
    cols = [TARGET, *REANALYSIS_FEATURES]
    arr = np.ascontiguousarray(df[cols].to_numpy(dtype="float64"))
    h = hashlib.sha256()
    h.update(np.asarray(pd.DatetimeIndex(df.index).asi8).tobytes())
    h.update(arr.tobytes())
    return "sha256:" + h.hexdigest()
