"""Dados sintéticos com o mesmo formato dos reais, para testes e demonstrações."""

from __future__ import annotations

import numpy as np
import pandas as pd

from pm25bench.data.dataset import TARGET
from pm25bench.data.sisam import REANALYSIS_FEATURES


def make_synthetic(
    start: str = "2015-01-01",
    end: str = "2018-12-31",
    seed: int = 0,
    missing_fraction: float = 0.05,
) -> pd.DataFrame:
    """Gera uma tabela diária sintética.

    O MP2,5 "observado" tem sazonalidade (pico no inverno), autocorrelação AR(1) e é ligado à
    reanálise por um viés multiplicativo, como acontece entre o SISAM e as estações.
    """
    rng = np.random.default_rng(seed)
    index = pd.date_range(start, end, freq="D", name="date")
    n = len(index)
    doy = index.day_of_year.to_numpy()
    season = 18 + 10 * np.cos(2 * np.pi * (doy - 200) / 365.25)
    noise = np.zeros(n)
    for i in range(1, n):
        noise[i] = 0.7 * noise[i - 1] + rng.normal(0, 4)
    obs = np.clip(season + noise, 1, None)
    rea_pm25 = np.clip(0.6 * obs + rng.normal(0, 3, n), 0.5, None)
    data = {
        TARGET: obs,
        "rea_pm2_5": rea_pm25,
        "rea_pm10": rea_pm25 * 1.4 + rng.normal(0, 2, n),
        "rea_o3": 50 + 15 * np.sin(2 * np.pi * doy / 365.25) + rng.normal(0, 5, n),
        "rea_no2": 0.3 * obs + rng.normal(0, 1, n),
        "rea_co": 0.01 * obs + rng.normal(0, 0.02, n),
        "rea_so2": 2 + rng.normal(0, 0.5, n),
    }
    df = pd.DataFrame(data, index=index)[[TARGET, *REANALYSIS_FEATURES]]
    missing = rng.random(n) < missing_fraction
    df.loc[missing, TARGET] = np.nan
    df.attrs["station"] = 0
    return df
