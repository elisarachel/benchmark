"""Modelos: o protocolo Forecaster, o registro de plugins e os baselines."""

from pm25bench.models.base import Forecaster, check_prediction
from pm25bench.models.climatology import Climatology
from pm25bench.models.linear import LinearRegression
from pm25bench.models.persistence import Persistence
from pm25bench.models.reanalysis import RawReanalysis
from pm25bench.models.registry import available, load_model

__all__ = [
    "Climatology",
    "Forecaster",
    "LinearRegression",
    "Persistence",
    "RawReanalysis",
    "available",
    "check_prediction",
    "load_model",
]
