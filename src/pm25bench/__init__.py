"""pm25bench: benchmark aberto de previsão de MP2,5 diário em estações da CETESB.

API pública mínima::

    from pm25bench import load_config, run_benchmark, load_model, metrics
"""

from importlib.metadata import PackageNotFoundError, version

from pm25bench import metrics
from pm25bench.benchmark import BenchmarkConfig, load_config, run_benchmark, write_report
from pm25bench.data import build_dataset, make_samples, make_synthetic, split_by_time
from pm25bench.models import Forecaster, available, load_model

try:
    __version__ = version("pm25bench")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = [
    "BenchmarkConfig",
    "Forecaster",
    "__version__",
    "available",
    "build_dataset",
    "load_config",
    "load_model",
    "make_samples",
    "make_synthetic",
    "metrics",
    "run_benchmark",
    "split_by_time",
    "write_report",
]
