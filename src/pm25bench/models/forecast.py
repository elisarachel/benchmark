"""Previsão bruta do CAMS: usa a previsão emitida em t para t + lead, sem correção."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


class RawForecast:
    """Usa ``fc_pm2_5_l{k}`` da linha t (previsão do CAMS emitida em t para t + k).

    Baseline da trilha de previsão: mostra quanto a previsão do CAMS, sozinha, erra em
    relação à estação. Só funciona com as colunas ``fc_*`` (``data.cams_forecast_dir`` ou
    ``data.synthetic_forecast``).
    """

    name = "forecast_raw"

    def fit(self, train: pd.DataFrame, val: pd.DataFrame | None = None) -> None:
        # sem parâmetros a ajustar
        return None

    def predict(self, context: pd.DataFrame, leads: Sequence[int]) -> np.ndarray:
        # colunas necessárias, uma por lead
        cols = [f"fc_pm2_5_l{k}" for k in leads]
        # sem as previsões, o modelo não tem o que usar
        if any(c not in context.columns for c in cols):
            raise KeyError(
                "forecast_raw precisa das previsões do CAMS: informe data.cams_forecast_dir"
            )
        # última linha = previsões emitidas no dia t
        return context[cols].iloc[-1].to_numpy(dtype="float64")
