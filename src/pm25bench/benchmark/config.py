"""Configuração declarativa do benchmark (YAML validado com pydantic)."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Literal

import pandas as pd
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator


class DataConfig(BaseModel):
    """De onde vêm os dados e como são divididos."""

    model_config = ConfigDict(extra="forbid")

    source: Literal["local", "download", "synthetic"] = "download"
    #: Pasta com os CSV/ZIP anuais do SISAM (``source: local``).
    sisam_dir: Path | None = None
    #: Pasta ``data/`` do repositório da CETESB, com uma subpasta por estação (``source: local``).
    cetesb_dir: Path | None = None
    station: int = 73
    min_hours: int = Field(18, ge=1, le=24)
    train_end: date = date(2019, 12, 31)
    val_end: date = date(2021, 12, 31)
    gap_days: int = Field(7, ge=0)

    def load(self) -> pd.DataFrame:
        """Carrega a tabela diária conforme ``source``."""
        from pm25bench.data import build_dataset, fetch_data, make_synthetic

        if self.source == "synthetic":
            return make_synthetic()
        if self.source == "download":
            sisam_dir, cetesb_dir = fetch_data(self.station)
        else:
            if self.sisam_dir is None or self.cetesb_dir is None:
                raise ValueError("source: local exige sisam_dir e cetesb_dir")
            sisam_dir, cetesb_dir = self.sisam_dir, self.cetesb_dir
        return build_dataset(sisam_dir, cetesb_dir, self.station, self.min_hours)


class ModelSpec(BaseModel):
    """Um modelo a avaliar: nome registrado e argumentos do construtor."""

    model_config = ConfigDict(extra="forbid")

    name: str
    kwargs: dict[str, Any] = {}


class BenchmarkConfig(BaseModel):
    """O contrato do benchmark. Igual para todos os modelos."""

    model_config = ConfigDict(extra="forbid")

    data: DataConfig = DataConfig()
    models: list[ModelSpec]
    n_context: int = Field(7, ge=2)
    leads: list[int] = [0, 1, 2, 3]
    #: Limiares de MP2,5 diário (µg/m³) para as métricas categóricas.
    thresholds: list[float] = [15.0, 25.0, 50.0]
    #: Tamanho dos blocos (em dias) do bootstrap.
    block_days: int = Field(7, ge=1)
    n_boot: int = Field(1000, ge=0)
    seed: int = 42
    output_dir: Path = Path("results")

    @field_validator("leads")
    @classmethod
    def _leads_ok(cls, v: list[int]) -> list[int]:
        if not v or any(k < 0 for k in v) or len(set(v)) != len(v):
            raise ValueError("leads precisa ser uma lista de inteiros >= 0, sem repetição")
        return sorted(v)


def load_config(path: str | Path) -> BenchmarkConfig:
    """Lê e valida um YAML de benchmark."""
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return BenchmarkConfig.model_validate(raw)
