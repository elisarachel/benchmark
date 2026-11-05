import numpy as np
import pandas as pd
import pytest

from pm25bench.data import (
    REANALYSIS_FEATURES,
    TARGET,
    build_dataset,
    daily_mean,
    dataset_hash,
    forecast_columns,
    make_samples,
    make_synthetic,
    read_cams_forecast,
    read_sisam,
    sisam_files,
    split_by_time,
    station_cd_mun,
    stations,
)


def test_daily_mean_trata_hora_24():
    # 01:00 ... 23:00 do dia 1 e 00:00 do dia 2 (= hora 24 do dia 1): 24 horas do dia 1.
    idx = pd.date_range("2020-01-01 01:00", periods=24, freq="h")
    s = pd.Series(10.0, index=idx)
    out = daily_mean(s, min_hours=18)
    assert list(out.index) == [pd.Timestamp("2020-01-01")]
    assert out.iloc[0] == 10.0


def test_daily_mean_poucas_horas_vira_nan():
    idx = pd.date_range("2020-01-01 01:00", periods=10, freq="h")
    out = daily_mean(pd.Series(5.0, index=idx), min_hours=18)
    assert np.isnan(out.iloc[0])


def test_split_sem_sobreposicao():
    df = make_synthetic()
    train, val, test = split_by_time(df, "2016-12-31", "2017-12-31", gap_days=7)
    assert train.index.max() < val.index.min() - pd.Timedelta(days=6)
    assert val.index.max() < test.index.min() - pd.Timedelta(days=6)
    with pytest.raises(ValueError):
        split_by_time(df, "2018-01-01", "2017-01-01")


def test_amostras_sem_vazamento():
    df = make_synthetic(missing_fraction=0.0)
    samples = list(make_samples(df.iloc[:40], n_context=7, leads=[0, 1, 2]))
    assert len(samples) == 40 - 6 - 2
    s = samples[0]
    assert len(s.context) == 7
    assert s.context.index[-1] == s.issue_date
    assert np.isnan(s.context[TARGET].iloc[-1])  # obs de t escondida
    assert s.context[REANALYSIS_FEATURES].notna().all().all()
    t = df.index.get_loc(s.issue_date)
    assert np.allclose(s.target, df[TARGET].iloc[[t, t + 1, t + 2]].to_numpy())
    # a tabela original não é alterada
    assert not np.isnan(df[TARGET].iloc[t])


def test_amostras_pulam_lacunas():
    df = make_synthetic(missing_fraction=0.0).iloc[:30].copy()
    df.iloc[15, 0] = np.nan
    for s in make_samples(df, n_context=5, leads=[0, 1]):
        window = df.loc[s.context.index[0] : s.issue_date + pd.Timedelta(days=1), TARGET]
        assert window.drop(s.issue_date).notna().all()


def test_estacoes():
    assert station_cd_mun(73) == 3550308
    assert "Congonhas" in stations().loc[73, "estacao"]
    with pytest.raises(KeyError):
        station_cd_mun(999999)


def test_hash_estavel_e_sensivel():
    df = make_synthetic()
    assert dataset_hash(df) == dataset_hash(df.copy())
    df2 = df.copy()
    df2.iloc[0, 1] += 1
    assert dataset_hash(df) != dataset_hash(df2)


def _write_fake_repos(tmp_path):
    sisam = tmp_path / "sisam"
    sisam.mkdir()
    days = pd.date_range("2020-01-01", "2020-01-10")
    rows = []
    for d in days:
        for cd in (3550308, 3500105):
            rows.append(
                {
                    "CD_MUN": cd,
                    "municipio": "X",
                    "estado": "SÃO PAULO",
                    "data": d.strftime("%d/%m/%Y"),
                    "pm10_reanalise": 1.0,
                    "pm2_5_reanalise": float(d.day),
                    "o3_reanalise": 1.0,
                    "no2_reanalise": 1.0,
                    "co_reanalise": 1.0,
                    "so2_reanalise": 1.0,
                }
            )
    name = "sisam_municipio_reanalise_diario_2020-01-01_2020-12-31.csv"
    pd.DataFrame(rows).to_csv(sisam / name, index=False, encoding="utf-8-sig")
    cetesb = tmp_path / "cetesb" / "73"
    cetesb.mkdir(parents=True)
    hours = pd.date_range("2020-01-02 01:00", "2020-01-04 00:00", freq="h")
    pd.DataFrame({"datetime": hours, "value": 20.0}).to_csv(cetesb / "2020.csv", index=False)
    return sisam, tmp_path / "cetesb"


def test_build_dataset(tmp_path):
    sisam, cetesb = _write_fake_repos(tmp_path)
    df = build_dataset(sisam, cetesb, station=73)
    assert list(df.columns) == [TARGET, *REANALYSIS_FEATURES]
    assert len(df) == 10
    assert df.loc["2020-01-05", "rea_pm2_5"] == 5.0
    assert df[TARGET].notna().sum() == 2
    assert df.loc["2020-01-02", TARGET] == 20.0


def test_sisam_municipio_inexistente(tmp_path):
    sisam, _ = _write_fake_repos(tmp_path)
    with pytest.raises(ValueError):
        read_sisam(sisam_files(sisam), 1234567)
    with pytest.raises(FileNotFoundError):
        sisam_files(tmp_path / "vazio")


# ---------------------------------------------------------------- trilha opcional de previsão

#: Hash de make_synthetic() na main (edce5eb), antes da trilha de previsão existir.
HASH_SINTETICO_V01 = "sha256:a68692cd5a4044ed405a11d10dc7080880c9f5edc881bbb3009ee0ee4ce1d5d9"
#: Colunas de previsão geradas pelo make_synthetic(forecast=True).
FC_COLS = [f"fc_pm2_5_l{k}" for k in range(4)]


def test_regressao_hash_padrao_inalterado():
    # Garante que a trilha de previsão não mudou nada para quem usa o contrato padrão.
    assert dataset_hash(make_synthetic()) == HASH_SINTETICO_V01


def test_sintetico_com_previsao_tem_colunas_fc():
    df = make_synthetic(forecast=True)
    assert forecast_columns(df) == FC_COLS
    assert df.attrs["forecast"] is True
    # as colunas antigas são as mesmas, com os mesmos valores
    pd.testing.assert_frame_equal(df[[TARGET, *REANALYSIS_FEATURES]], make_synthetic())
    # previsão para além do fim da série é NaN
    assert df["fc_pm2_5_l3"].iloc[-3:].isna().all()


def test_amostras_com_previsao():
    df = make_synthetic(forecast=True, missing_fraction=0.0).iloc[:60].copy()
    samples = list(make_samples(df, n_context=7, leads=[0, 1, 2, 3]))
    s = samples[0]
    # o contexto traz as colunas fc_* e a obs de t continua escondida
    assert set(FC_COLS) <= set(s.context.columns)
    assert np.isnan(s.context[TARGET].iloc[-1])
    # amostras com fc_* faltando em algum dia do contexto são descartadas
    buraco = df.index[20]
    df.loc[buraco, "fc_pm2_5_l2"] = np.nan
    datas = {a.issue_date for a in make_samples(df, n_context=7, leads=[0, 1, 2, 3])}
    afetadas = {buraco + pd.Timedelta(days=d) for d in range(7)}
    assert not (datas & afetadas)
    assert len(datas) == len(samples) - len(afetadas)


def test_hash_muda_com_previsao():
    assert dataset_hash(make_synthetic(forecast=True)) != dataset_hash(make_synthetic())


def test_read_cams_forecast(tmp_path):
    pasta = tmp_path / "73"
    pasta.mkdir()
    pd.DataFrame(
        {"date": ["2020-01-02", "2020-01-01"], "fc_pm2_5_l0": [2.0, 1.0], "outra": [9, 9]}
    ).to_csv(pasta / "2020.csv", index=False)
    fc = read_cams_forecast(tmp_path, 73)
    assert list(fc.columns) == ["fc_pm2_5_l0"]
    assert list(fc.index) == [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-02")]
    assert fc["fc_pm2_5_l0"].dtype == "float64"
    with pytest.raises(FileNotFoundError):
        read_cams_forecast(tmp_path, 99)


def test_build_dataset_com_previsao(tmp_path):
    sisam, cetesb = _write_fake_repos(tmp_path)
    pasta = tmp_path / "fc" / "73"
    pasta.mkdir(parents=True)
    pd.DataFrame({"date": ["2020-01-03"], "fc_pm2_5_l0": [7.0]}).to_csv(
        pasta / "2020.csv", index=False
    )
    df = build_dataset(sisam, cetesb, station=73, cams_forecast_dir=tmp_path / "fc")
    assert list(df.columns) == [TARGET, *REANALYSIS_FEATURES, "fc_pm2_5_l0"]
    assert df.attrs["forecast"] is True
    assert df.loc["2020-01-03", "fc_pm2_5_l0"] == 7.0
    assert df["fc_pm2_5_l0"].notna().sum() == 1
    # sem a pasta, a tabela é a do contrato padrão
    padrao = build_dataset(sisam, cetesb, station=73)
    pd.testing.assert_frame_equal(df[[TARGET, *REANALYSIS_FEATURES]], padrao)
    assert "forecast" not in padrao.attrs
