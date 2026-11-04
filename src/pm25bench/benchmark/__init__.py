"""Orquestração do benchmark: configuração, execução e relatório."""

from pm25bench.benchmark.config import BenchmarkConfig, DataConfig, ModelSpec, load_config
from pm25bench.benchmark.report import write_report
from pm25bench.benchmark.runner import (
    BenchmarkResult,
    predict_samples,
    run_benchmark,
    score_predictions,
)

__all__ = [
    "BenchmarkConfig",
    "BenchmarkResult",
    "DataConfig",
    "ModelSpec",
    "load_config",
    "predict_samples",
    "run_benchmark",
    "score_predictions",
    "write_report",
]
