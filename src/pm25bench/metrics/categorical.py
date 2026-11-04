"""Métricas categóricas de ultrapassagem de limiar (episódios de poluição).

Um dia é "evento" quando o MP2,5 diário é ``>= threshold``. Com a tabela de contingência
(a = acertos, b = falsos alarmes, c = perdas, d = negativos corretos) calculamos POD, FAR,
CSI, ETS e viés de frequência.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def contingency(obs: ArrayLike, fcst: ArrayLike, threshold: float) -> tuple[int, int, int, int]:
    """Tabela de contingência ``(a, b, c, d)`` para o limiar dado (pares com NaN ignorados)."""
    o_arr = np.asarray(obs, dtype="float64").ravel()
    f_arr = np.asarray(fcst, dtype="float64").ravel()
    ok = ~(np.isnan(o_arr) | np.isnan(f_arr))
    o, f = o_arr[ok] >= threshold, f_arr[ok] >= threshold
    return (
        int(np.sum(f & o)),
        int(np.sum(f & ~o)),
        int(np.sum(~f & o)),
        int(np.sum(~f & ~o)),
    )


def pod(obs: ArrayLike, fcst: ArrayLike, threshold: float) -> float:
    """Probabilidade de detecção, ``a / (a + c)``. 1 = ideal."""
    a, _, c, _ = contingency(obs, fcst, threshold)
    return a / (a + c) if a + c else float("nan")


def far(obs: ArrayLike, fcst: ArrayLike, threshold: float) -> float:
    """Razão de falsos alarmes, ``b / (a + b)``. 0 = ideal."""
    a, b, _, _ = contingency(obs, fcst, threshold)
    return b / (a + b) if a + b else float("nan")


def csi(obs: ArrayLike, fcst: ArrayLike, threshold: float) -> float:
    """Índice de sucesso crítico, ``a / (a + b + c)``. 1 = ideal."""
    a, b, c, _ = contingency(obs, fcst, threshold)
    return a / (a + b + c) if a + b + c else float("nan")


def frequency_bias(obs: ArrayLike, fcst: ArrayLike, threshold: float) -> float:
    """Viés de frequência, ``(a + b) / (a + c)``. > 1 = prevê eventos demais."""
    a, b, c, _ = contingency(obs, fcst, threshold)
    return (a + b) / (a + c) if a + c else float("nan")


def ets(obs: ArrayLike, fcst: ArrayLike, threshold: float) -> float:
    """Equitable Threat Score: CSI descontando os acertos ao acaso. 0 = sem habilidade."""
    a, b, c, d = contingency(obs, fcst, threshold)
    n = a + b + c + d
    if n == 0:
        return float("nan")
    ar = (a + b) * (a + c) / n
    den = a + b + c - ar
    return (a - ar) / den if den else float("nan")
