"""Regressão linear: correção estatística simples da reanálise."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from pm25bench.data.dataset import TARGET
from pm25bench.data.sisam import REANALYSIS_FEATURES
from pm25bench.data.splits import make_samples


def _features(context: pd.DataFrame) -> np.ndarray:
    """Reanálise do dia t, última observação (t-1), média do contexto e sazonalidade."""
    rea_t = context[REANALYSIS_FEATURES].iloc[-1].to_numpy(dtype="float64")
    past = context[TARGET].iloc[:-1].to_numpy(dtype="float64")
    doy = context.index[-1].day_of_year
    season = [np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25)]
    return np.concatenate([[1.0], rea_t, [past[-1], past.mean()], season])


class LinearRegression:
    """Uma regressão linear (mínimos quadrados com penalização ridge) por lead.

    Parameters
    ----------
    n_context : int
        Dias de contexto usados para montar as amostras de treino.
    alpha : float
        Penalização ridge (0 = mínimos quadrados puros).
    leads : sequence of int
        Leads para os quais uma regressão é ajustada.
    """

    name = "linear_regression"

    def __init__(
        self, n_context: int = 7, alpha: float = 1.0, leads: Sequence[int] = (0, 1, 2, 3)
    ) -> None:
        self.n_context = n_context
        self.alpha = alpha
        self._coef: dict[int, np.ndarray] = {}
        self._leads: tuple[int, ...] = tuple(leads)

    def fit(self, train: pd.DataFrame, val: pd.DataFrame | None = None) -> None:
        samples = list(make_samples(train, self.n_context, self._leads))
        if not samples:
            raise ValueError("treino sem amostras válidas")
        x = np.stack([_features(s.context) for s in samples])
        y = np.stack([s.target for s in samples])
        mu, sd = x[:, 1:].mean(0), x[:, 1:].std(0) + 1e-9
        self._mu, self._sd = mu, sd
        xs = np.column_stack([x[:, 0], (x[:, 1:] - mu) / sd])
        reg = self.alpha * np.eye(xs.shape[1])
        reg[0, 0] = 0.0
        for j, lead in enumerate(self._leads):
            self._coef[lead] = np.linalg.solve(xs.T @ xs + reg, xs.T @ y[:, j])

    def predict(self, context: pd.DataFrame, leads: Sequence[int]) -> np.ndarray:
        if not self._coef:
            raise RuntimeError("chame fit antes de predict")
        x = _features(context)
        xs = np.concatenate([[1.0], (x[1:] - self._mu) / self._sd])
        out = []
        for lead in leads:
            coef = self._coef.get(lead, self._coef[max(self._coef)])
            out.append(max(float(xs @ coef), 0.0))
        return np.array(out)
