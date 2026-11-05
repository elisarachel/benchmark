import json

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from pm25bench.benchmark import BenchmarkConfig, load_config, run_benchmark, write_report
from pm25bench.cli import main
from pm25bench.data import make_samples, make_synthetic, split_by_time
from pm25bench.models import (
    Climatology,
    Forecaster,
    LinearRegression,
    Persistence,
    RawForecast,
    RawReanalysis,
    available,
    check_prediction,
    load_model,
)

LEADS = [0, 1, 2, 3]


@pytest.fixture(scope="module")
def data():
    df = make_synthetic()
    return split_by_time(df, "2016-12-31", "2017-06-30")


@pytest.mark.parametrize(
    "cls", [Persistence, Climatology, RawReanalysis, LinearRegression], ids=lambda c: c.__name__
)
def test_baselines_cumprem_o_protocolo(cls, data):
    train, val, test = data
    model = cls()
    assert isinstance(model, Forecaster)
    model.fit(train, val)
    sample = next(make_samples(test, 7, LEADS))
    pred = check_prediction(model.predict(sample.context, LEADS), LEADS, model.name)
    assert pred.shape == (4,)
    assert (pred >= 0).all()


def test_persistencia_usa_t_menos_1(data):
    _, _, test = data
    s = next(make_samples(test, 7, LEADS))
    assert np.all(Persistence().predict(s.context, LEADS) == s.context["obs"].iloc[-2])


def test_modelos_sem_fit_falham():
    s = next(make_samples(make_synthetic().iloc[:30], 7, LEADS))
    with pytest.raises(RuntimeError):
        Climatology().predict(s.context, LEADS)
    with pytest.raises(RuntimeError):
        LinearRegression().predict(s.context, LEADS)


def test_registro_de_plugins():
    names = available()
    for n in ("persistence", "climatology", "reanalysis_raw", "linear_regression"):
        assert n in names
    assert isinstance(load_model("climatology", window=5), Climatology)
    with pytest.raises(KeyError):
        load_model("nao_existe")


def test_check_prediction():
    with pytest.raises(ValueError):
        check_prediction(np.zeros(3), LEADS, "x")
    with pytest.raises(ValueError):
        check_prediction(np.array([1, 2, np.nan, 4]), LEADS, "x")


def _cfg(tmp_path, **kw):
    raw = {
        "data": {"source": "synthetic", "train_end": "2016-12-31", "val_end": "2017-06-30"},
        "models": [{"name": "persistence"}, {"name": "linear_regression"}],
        "n_boot": 20,
        "output_dir": str(tmp_path / "out"),
    }
    raw.update(kw)
    return BenchmarkConfig.model_validate(raw)


def test_runner_e_relatorio(tmp_path):
    cfg = _cfg(tmp_path)
    result = run_benchmark(cfg)
    assert set(result.scores["model"]) == {"persistence", "linear_regression"}
    assert len(result.scores) == 2 * len(LEADS)
    # todos os modelos avaliados nas mesmas amostras
    counts = result.predictions.groupby("model").size()
    assert counts.nunique() == 1
    lr = result.scores.query("model == 'linear_regression' and lead == 0")["mae"].item()
    pe = result.scores.query("model == 'persistence' and lead == 0")["mae"].item()
    assert lr < pe
    board = write_report(result, cfg.output_dir)
    assert "linear_regression" in board.read_text(encoding="utf-8")
    meta = json.loads((tmp_path / "out" / "metadata.json").read_text())
    assert meta["dataset_hash"].startswith("sha256:")
    assert (tmp_path / "out" / "mae_by_lead.png").exists()


def test_teste_nunca_entra_no_fit(tmp_path):
    seen = {}

    class Spy(Persistence):
        def fit(self, train, val=None):
            seen["max"] = max(train.index.max(), val.index.max())

    cfg = _cfg(tmp_path)
    df = make_synthetic()
    _, _, test = split_by_time(df, "2016-12-31", "2017-06-30")
    import pm25bench.benchmark.runner as runner

    orig = runner.load_model
    runner.load_model = lambda name, **kw: Spy()
    try:
        run_benchmark(cfg, df)
    finally:
        runner.load_model = orig
    assert seen["max"] < test.index.min()


def test_config_invalida():
    with pytest.raises(ValidationError):
        BenchmarkConfig.model_validate({"models": [], "campo_errado": 1})
    with pytest.raises(ValidationError):
        BenchmarkConfig.model_validate({"models": [], "leads": [-1]})


def test_config_yaml_e_cli(tmp_path, capsys):
    yml = tmp_path / "b.yaml"
    yml.write_text(
        "data: {source: synthetic, train_end: 2016-12-31, val_end: 2017-06-30}\n"
        "models: [{name: persistence}]\nn_boot: 0\n"
        f"output_dir: {tmp_path / 'res'}\n"
    )
    cfg = load_config(yml)
    assert cfg.models[0].name == "persistence"
    assert main(["run", str(yml)]) == 0
    assert "persistence" in capsys.readouterr().out
    assert main(["models"]) == 0
    assert main(["stations"]) == 0
    assert "Congonhas" in capsys.readouterr().out


def test_local_sem_caminhos():
    cfg = BenchmarkConfig.model_validate({"data": {"source": "local"}, "models": []})
    with pytest.raises(ValueError):
        cfg.data.load()


def test_resultado_tem_datas_alvo(tmp_path):
    res = run_benchmark(_cfg(tmp_path, n_boot=0))
    p = res.predictions
    assert (p["target_date"] - p["issue_date"] == pd.to_timedelta(p["lead"], unit="D")).all()


# ---------------------------------------------------------------- trilha opcional de previsão


def test_forecast_raw_cumpre_o_protocolo():
    train, val, test = split_by_time(make_synthetic(forecast=True), "2016-12-31", "2017-06-30")
    model = load_model("forecast_raw")
    assert isinstance(model, RawForecast) and isinstance(model, Forecaster)
    model.fit(train, val)
    s = next(make_samples(test, 7, LEADS))
    pred = check_prediction(model.predict(s.context, LEADS), LEADS, model.name)
    esperado = [s.context[f"fc_pm2_5_l{k}"].iloc[-1] for k in LEADS]
    assert np.allclose(pred, esperado)


def test_forecast_raw_sem_previsao_falha(data):
    _, _, test = data
    s = next(make_samples(test, 7, LEADS))
    with pytest.raises(KeyError, match="informe data.cams_forecast_dir"):
        RawForecast().predict(s.context, LEADS)


def test_runner_trilha_previsao(tmp_path):
    cfg = _cfg(
        tmp_path,
        data={
            "source": "synthetic",
            "train_end": "2016-12-31",
            "val_end": "2017-06-30",
            "synthetic_forecast": True,
        },
        models=[{"name": "persistence"}, {"name": "forecast_raw"}],
    )
    result = run_benchmark(cfg)
    assert result.metadata["forecast"] is True
    board = write_report(result, cfg.output_dir).read_text(encoding="utf-8")
    assert "Trilha: previsão do CAMS" in board
    meta = json.loads((tmp_path / "out" / "metadata.json").read_text())
    assert meta["forecast"] is True


def test_runner_padrao_sem_trilha(tmp_path):
    result = run_benchmark(_cfg(tmp_path, n_boot=0))
    assert result.metadata["forecast"] is False
    board = write_report(result, tmp_path / "out").read_text(encoding="utf-8")
    assert "Trilha" not in board
