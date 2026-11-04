"""Métricas: funções puras NumPy, sem conhecer modelos nem dados."""

from pm25bench.metrics.categorical import contingency, csi, ets, far, frequency_bias, pod
from pm25bench.metrics.continuous import bias, mae, pearson_r, rmse
from pm25bench.metrics.uncertainty import block_bootstrap_ci

__all__ = [
    "bias",
    "block_bootstrap_ci",
    "contingency",
    "csi",
    "ets",
    "far",
    "frequency_bias",
    "mae",
    "pearson_r",
    "pod",
    "rmse",
]
