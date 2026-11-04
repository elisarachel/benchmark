"""Métricas contínuas. Entradas em µg/m³; pares com NaN são ignorados."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def _pair(obs: ArrayLike, fcst: ArrayLike) -> tuple[np.ndarray, np.ndarray]:
    o = np.asarray(obs, dtype="float64").ravel()
    f = np.asarray(fcst, dtype="float64").ravel()
    if o.shape != f.shape:
        raise ValueError(f"formatos diferentes: {o.shape} e {f.shape}")
    ok = ~(np.isnan(o) | np.isnan(f))
    return o[ok], f[ok]


def mae(obs: ArrayLike, fcst: ArrayLike) -> float:
    """Erro absoluto médio, ``mean(|F - O|)``."""
    o, f = _pair(obs, fcst)
    return float(np.mean(np.abs(f - o))) if o.size else float("nan")


def rmse(obs: ArrayLike, fcst: ArrayLike) -> float:
    """Raiz do erro quadrático médio, ``sqrt(mean((F - O)²))``."""
    o, f = _pair(obs, fcst)
    return float(np.sqrt(np.mean((f - o) ** 2))) if o.size else float("nan")


def bias(obs: ArrayLike, fcst: ArrayLike) -> float:
    """Viés médio, ``mean(F - O)``. Positivo = superestima."""
    o, f = _pair(obs, fcst)
    return float(np.mean(f - o)) if o.size else float("nan")


def pearson_r(obs: ArrayLike, fcst: ArrayLike) -> float:
    """Correlação de Pearson. ``NaN`` se uma das séries for constante."""
    o, f = _pair(obs, fcst)
    if o.size < 2 or np.std(o) == 0 or np.std(f) == 0:
        return float("nan")
    return float(np.corrcoef(o, f)[0, 1])
