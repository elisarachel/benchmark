"""Persistência: o MP2,5 de amanhã é igual ao do último dia medido."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from pm25bench.data.dataset import TARGET


class Persistence:
    """Repete a última observação disponível (dia t-1) para todos os leads.

    Baseline obrigatório: é difícil de vencer nos primeiros dias por causa da autocorrelação.
    """

    name = "persistence"

    def fit(self, train: pd.DataFrame, val: pd.DataFrame | None = None) -> None:
        return None

    def predict(self, context: pd.DataFrame, leads: Sequence[int]) -> np.ndarray:
        last = float(context[TARGET].iloc[-2])
        return np.full(len(leads), last)
