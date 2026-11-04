from pm25bench import Forecaster, load_model, make_samples, make_synthetic, split_by_time


def test_plugin_registrado_e_cumpre_o_protocolo():
    model = load_model("meumodelo")
    assert isinstance(model, Forecaster)
    train, val, test = split_by_time(make_synthetic(), "2016-12-31", "2017-06-30")
    model.fit(train, val)
    s = next(make_samples(test, 7, [0, 1, 2, 3]))
    pred = model.predict(s.context, [0, 1, 2, 3])
    assert pred.shape == (4,)
    assert (pred >= 0).all()
