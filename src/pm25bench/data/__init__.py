"""Dados: reanálise do SISAM (entrada) e MP2,5 das estações da CETESB (alvo)."""

from pm25bench.data.cams import FORECAST_PREFIX, forecast_columns, read_cams_forecast
from pm25bench.data.cetesb import daily_mean, read_station_hourly, station_cd_mun, stations
from pm25bench.data.dataset import TARGET, build_dataset, dataset_hash
from pm25bench.data.fetch import fetch_data
from pm25bench.data.sisam import REANALYSIS_FEATURES, read_sisam, sisam_files
from pm25bench.data.splits import Sample, make_samples, split_by_time
from pm25bench.data.synthetic import make_synthetic

__all__ = [
    "FORECAST_PREFIX",
    "REANALYSIS_FEATURES",
    "TARGET",
    "Sample",
    "build_dataset",
    "daily_mean",
    "dataset_hash",
    "fetch_data",
    "forecast_columns",
    "make_samples",
    "make_synthetic",
    "read_cams_forecast",
    "read_sisam",
    "read_station_hourly",
    "sisam_files",
    "split_by_time",
    "station_cd_mun",
    "stations",
]
