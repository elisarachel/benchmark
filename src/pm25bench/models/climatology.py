"""Climatologia: a média histórica (do treino) para aquela época do ano."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from pm25bench.data.dataset import TARGET


class Climatology:
    """Média do MP2,5 observado no treino por dia do ano, suavizada em ±``window`` dias.

    Parameters
    ----------
    window : int
        Meia largura da janela de suavização, em dias.
    """

    name = "climatology"

    def __init__(self, window: int = 15) -> None:
        self.window = window
        self._clim: np.ndarray | None = None

    def fit(self, train: pd.DataFrame, val: pd.DataFrame | None = None) -> None:
        obs = train[TARGET].dropna()
        doy = np.minimum(pd.DatetimeIndex(obs.index).day_of_year.to_numpy(), 365) - 1
        sums = np.bincount(doy, weights=obs.to_numpy(), minlength=365)
        counts = np.bincount(doy, minlength=365).astype("float64")
        w = self.window
        kernel = np.ones(2 * w + 1)
        sums_s = np.convolve(np.concatenate([sums[-w:], sums, sums[:w]]), kernel, "valid")
        counts_s = np.convolve(np.concatenate([counts[-w:], counts, counts[:w]]), kernel, "valid")
        fallback = float(obs.mean()) if len(obs) else 0.0
        with np.errstate(invalid="ignore", divide="ignore"):
            clim = np.where(counts_s > 0, sums_s / counts_s, fallback)
        self._clim = clim

    def predict(self, context: pd.DataFrame, leads: Sequence[int]) -> np.ndarray:
        if self._clim is None:
            raise RuntimeError("chame fit antes de predict")
        t = context.index[-1]
        dates = pd.DatetimeIndex([t + pd.Timedelta(days=k) for k in leads])
        doy = np.minimum(dates.day_of_year.to_numpy(), 365) - 1
        return np.asarray(self._clim[doy], dtype="float64")
