"""Descoberta de modelos por entry points (plugins)."""

from __future__ import annotations

from importlib.metadata import entry_points
from typing import Any

from pm25bench.models.base import Forecaster

GROUP = "pm25bench.models"


def available() -> list[str]:
    """Nomes de todos os modelos instalados (do pm25bench e de plugins)."""
    return sorted(ep.name for ep in entry_points(group=GROUP))


def load_model(name: str, **kwargs: Any) -> Forecaster:
    """Instancia um modelo pelo nome registrado em ``pm25bench.models``."""
    eps = entry_points(group=GROUP)
    if name not in eps.names:
        raise KeyError(f"modelo desconhecido {name!r}; instalados: {available()}")
    model = eps[name].load()(**kwargs)
    if not isinstance(model, Forecaster):
        raise TypeError(f"{name}: não implementa o protocolo Forecaster")
    return model
