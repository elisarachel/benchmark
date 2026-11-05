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
    forecast: bool = False,
) -> pd.DataFrame:
    """Gera uma tabela diária sintética.

    O MP2,5 "observado" tem sazonalidade (pico no inverno), autocorrelação AR(1) e é ligado à
    reanálise por um viés multiplicativo, como acontece entre o SISAM e as estações.

    Com ``forecast=True``, acrescenta ``fc_pm2_5_l{k}`` (k = 0 a 3): a previsão emitida em t
    para t + k, ``0,6·obs(t+k) + N(0, 2 + 1,5k)`` truncada em 0,5, com ruído que cresce com o
    lead e ``NaN`` quando t + k passa do fim da série. Os números da previsão vêm de um
    gerador separado, então com ``forecast=False`` a saída é idêntica à de antes.
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
    # trilha opcional de previsão
    if forecast:
        # gerador separado: não altera a sequência aleatória usada acima
        rng_fc = np.random.default_rng([seed, 1])
        # uma coluna por lead
        for k in range(4):
            # obs verdadeira (antes das lacunas) do dia alvo t + k; NaN depois do fim da série
            alvo = np.concatenate([obs[k:], np.full(k, np.nan)])
            # viés multiplicativo e ruído que cresce com o lead
            fc = 0.6 * alvo + rng_fc.normal(0, 2 + 1.5 * k, n)
            # trunca em 0,5 (np.clip preserva o NaN do fim da série)
            df[f"fc_pm2_5_l{k}"] = np.clip(fc, 0.5, None)
        # marca a tabela como da trilha de previsão
        df.attrs["forecast"] = True
    df.attrs["station"] = 0
    return df
