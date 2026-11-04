"""O contrato que todo modelo do pm25bench precisa cumprir."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

import numpy as np
import pandas as pd


@runtime_checkable
class Forecaster(Protocol):
    """Contrato de todo modelo do pm25bench.

    Qualquer classe com ``name``, ``fit`` e ``predict`` compatíveis já é um ``Forecaster``,
    sem precisar herdar de nada (tipagem estrutural).

    Regras do protocolo
    -------------------
    - ``fit`` recebe apenas os conjuntos de treino e validação. O teste nunca é visto.
    - ``predict`` recebe o contexto de uma amostra: ``n_context`` dias (t-n+1 ... t) com a
      coluna ``obs`` (MP2,5 diário da estação, ``NaN`` no dia t) e as colunas ``rea_*``
      (reanálise do município, disponível até o dia t).
    - ``predict`` devolve um array com uma previsão de MP2,5 diário (µg/m³) por lead,
      na mesma ordem de ``leads``. O lead 0 é o próprio dia t.
    """

    name: str

    def fit(self, train: pd.DataFrame, val: pd.DataFrame | None = None) -> None:
        """Ajusta o modelo. Modelos sem parâmetros podem não fazer nada."""
        ...

    def predict(self, context: pd.DataFrame, leads: Sequence[int]) -> np.ndarray:
        """Prevê o MP2,5 diário em t + lead para cada lead."""
        ...


def check_prediction(pred: np.ndarray, leads: Sequence[int], name: str) -> np.ndarray:
    """Valida a saída de ``predict`` (formato e valores finitos)."""
    arr = np.asarray(pred, dtype="float64").reshape(-1)
    if arr.shape != (len(leads),):
        raise ValueError(f"{name}: predict devolveu {arr.shape}, esperado ({len(leads)},)")
    if not np.isfinite(arr).all():
        raise ValueError(f"{name}: predict devolveu NaN ou infinito")
    return arr
