"""Exemplo de plugin: reanálise corrigida por um fator de escala + suavização com a persistência.

Copie esta pasta, troque o nome do pacote e do modelo e implemente o seu ``fit``/``predict``.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


class MeuModelo:
    """``pred = w * escala * reanálise(t) + (1 - w) * obs(t-1)``.

    ``escala`` é a razão média obs/reanálise no treino; ``w`` é escolhido na validação.
    """

    name = "meumodelo"

    def __init__(self) -> None:
        self.scale = 1.0
        self.w = 0.5

    def fit(self, train: pd.DataFrame, val: pd.DataFrame | None = None) -> None:
        ok = train[["obs", "rea_pm2_5"]].dropna()
        self.scale = float(ok["obs"].sum() / ok["rea_pm2_5"].sum())
        if val is None or val.empty:
            return
        v = val[["obs", "rea_pm2_5"]].copy()
        v["prev"] = v["obs"].shift(1)
        v = v.dropna()
        best = min(
            np.linspace(0, 1, 11),
            key=lambda w: np.mean(
                np.abs(w * self.scale * v["rea_pm2_5"] + (1 - w) * v["prev"] - v["obs"])
            ),
        )
        self.w = float(best)

    def predict(self, context: pd.DataFrame, leads: Sequence[int]) -> np.ndarray:
        rea = float(context["rea_pm2_5"].iloc[-1])
        prev = float(context["obs"].iloc[-2])
        value = self.w * self.scale * rea + (1 - self.w) * prev
        return np.full(len(leads), max(value, 0.0))
