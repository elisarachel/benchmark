import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from pm25bench.metrics import (
    bias,
    block_bootstrap_ci,
    contingency,
    csi,
    ets,
    far,
    frequency_bias,
    mae,
    pearson_r,
    pod,
    rmse,
)

# Grade 4 x 4 do exemplo guiado da aula (limiar 2): a=3, b=2, c=2, d=9.
OBS = np.array(
    [[0.0, 3.2, 6.8, 0.4], [0.1, 2.5, 8.9, 0.0], [0.0, 0.6, 4.1, 0.3], [0.0, 0.0, 0.2, 0.0]]
)
FC = np.array(
    [[0.0, 0.9, 4.4, 2.6], [0.0, 1.2, 7.5, 3.0], [0.0, 0.3, 2.2, 0.5], [0.0, 0.0, 0.0, 0.0]]
)


def test_contingencia_do_exemplo():
    assert contingency(OBS, FC, 2.0) == (3, 2, 2, 9)


def test_categoricas_do_exemplo():
    assert pod(OBS, FC, 2.0) == pytest.approx(3 / 5)
    assert far(OBS, FC, 2.0) == pytest.approx(2 / 5)
    assert csi(OBS, FC, 2.0) == pytest.approx(3 / 7)
    assert frequency_bias(OBS, FC, 2.0) == pytest.approx(1.0)
    ar = 5 * 5 / 16
    assert ets(OBS, FC, 2.0) == pytest.approx((3 - ar) / (7 - ar))


def test_previsao_perfeita():
    assert csi(OBS, OBS, 2.0) == 1.0
    assert far(OBS, OBS, 2.0) == 0.0
    assert mae(OBS, OBS) == 0.0
    assert rmse(OBS, OBS) == 0.0


def test_sem_eventos_da_nan():
    zeros = np.zeros(10)
    assert np.isnan(csi(zeros, zeros, 15))
    assert np.isnan(pod(zeros, zeros, 15))


def test_continuas_valores_conhecidos():
    o = np.array([10.0, 20.0, 30.0])
    f = np.array([12.0, 18.0, 36.0])
    assert mae(o, f) == pytest.approx(10 / 3)
    assert rmse(o, f) == pytest.approx(np.sqrt((4 + 4 + 36) / 3))
    assert bias(o, f) == pytest.approx(2.0)
    assert pearson_r(o, o * 2 + 1) == pytest.approx(1.0)


def test_nan_e_ignorado():
    o = np.array([1.0, np.nan, 3.0])
    f = np.array([2.0, 5.0, np.nan])
    assert mae(o, f) == pytest.approx(1.0)


def test_formatos_diferentes():
    with pytest.raises(ValueError):
        mae([1, 2], [1, 2, 3])


campos = arrays(np.float64, 30, elements=st.floats(0, 200))


@given(campos, campos)
def test_csi_simetrico_e_limitado(o, f):
    v = csi(o, f, 25.0)
    assert np.isnan(v) or 0.0 <= v <= 1.0
    w = csi(f, o, 25.0)
    assert (np.isnan(v) and np.isnan(w)) or v == pytest.approx(w)


@given(campos, campos)
def test_mae_menor_ou_igual_rmse(o, f):
    assert mae(o, f) <= rmse(o, f) + 1e-9


def test_bootstrap_contem_estimativa():
    rng = np.random.default_rng(0)
    o = rng.gamma(4, 4, 400)
    f = o + rng.normal(0, 3, 400)
    blocks = np.arange(400) // 7
    lo, hi = block_bootstrap_ci(o, f, blocks, mae, n_boot=300)
    assert lo < mae(o, f) < hi


def test_bootstrap_um_bloco_da_nan():
    lo, hi = block_bootstrap_ci([1.0, 2.0], [1.0, 2.0], [0, 0], mae, n_boot=10)
    assert np.isnan(lo) and np.isnan(hi)
