"""Reanálise bruta: usa o MP2,5 do SISAM sem nenhuma correção."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


class RawReanalysis:
    """Usa o ``rea_pm2_5`` do dia t como previsão para todos os leads.

    Mostra quanto a reanálise, sozinha, erra em relação à estação (viés, escala).
    Qualquer modelo que use a reanálise deveria superá-lo.
    """

    name = "reanalysis_raw"

    def fit(self, train: pd.DataFrame, val: pd.DataFrame | None = None) -> None:
        return None

    def predict(self, context: pd.DataFrame, leads: Sequence[int]) -> np.ndarray:
        return np.full(len(leads), float(context["rea_pm2_5"].iloc[-1]))
