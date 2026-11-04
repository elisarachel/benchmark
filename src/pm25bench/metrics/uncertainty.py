"""Intervalos de confiança por bootstrap em blocos."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from numpy.typing import ArrayLike

Metric = Callable[[np.ndarray, np.ndarray], float]


def block_bootstrap_ci(
    obs: ArrayLike,
    fcst: ArrayLike,
    blocks: ArrayLike,
    metric: Metric,
    n_boot: int = 1000,
    level: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    """Intervalo de confiança de uma métrica reamostrando blocos inteiros.

    Dias vizinhos de MP2,5 são correlacionados; reamostrar dia a dia daria um intervalo
    estreito demais. Por isso reamostramos blocos (por exemplo, semanas) com reposição.

    Parameters
    ----------
    obs, fcst : array_like
        Observação e previsão.
    blocks : array_like
        Rótulo do bloco de cada amostra (mesmo tamanho de ``obs``).
    metric : callable
        Função ``metric(obs, fcst) -> float``.

    Returns
    -------
    tuple of float
        Limites inferior e superior do intervalo.
    """
    o = np.asarray(obs, dtype="float64")
    f = np.asarray(fcst, dtype="float64")
    labels, inverse = np.unique(np.asarray(blocks), return_inverse=True)
    groups = [np.flatnonzero(inverse == i) for i in range(len(labels))]
    if len(groups) < 2:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    stats = np.empty(n_boot)
    for i in range(n_boot):
        pick = rng.integers(0, len(groups), len(groups))
        idx = np.concatenate([groups[j] for j in pick])
        stats[i] = metric(o[idx], f[idx])
    if np.isnan(stats).all():
        return float("nan"), float("nan")
    alpha = (1 - level) / 2
    lo, hi = np.nanquantile(stats, [alpha, 1 - alpha])
    return float(lo), float(hi)
