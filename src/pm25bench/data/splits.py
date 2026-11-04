"""Divisão temporal (por blocos) e geração das amostras do benchmark."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from pm25bench.data.dataset import TARGET
from pm25bench.data.sisam import REANALYSIS_FEATURES


def split_by_time(
    df: pd.DataFrame,
    train_end: str | date | pd.Timestamp,
    val_end: str | date | pd.Timestamp,
    gap_days: int = 7,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Divide em treino, validação e teste por blocos contínuos de tempo.

    ``train``: datas ``<= train_end``; ``val``: de ``train_end + gap`` até ``val_end``;
    ``test``: a partir de ``val_end + gap``. Os dias do intervalo ficam de fora, para que
    a autocorrelação do MP2,5 não vaze informação entre os conjuntos.
    """
    t = df.index
    te, ve = pd.Timestamp(train_end), pd.Timestamp(val_end)
    gap = pd.Timedelta(days=gap_days)
    if not te < ve:
        raise ValueError("train_end precisa ser anterior a val_end")
    train = df[t <= te]
    val = df[(t > te + gap) & (t <= ve)]
    test = df[t > ve + gap]
    return train, val, test


@dataclass(frozen=True)
class Sample:
    """Uma amostra do benchmark.

    Attributes
    ----------
    issue_date : pandas.Timestamp
        Dia t em que a previsão é emitida.
    context : pandas.DataFrame
        ``n_context`` dias (t-n+1 ... t) com ``obs`` e ``rea_*``. A ``obs`` do dia t é ``NaN``
        (ainda não foi medida); a reanálise do dia t está disponível.
    target : numpy.ndarray
        ``obs`` nos dias t + lead, para cada lead.
    """

    issue_date: pd.Timestamp
    context: pd.DataFrame
    target: np.ndarray


def make_samples(
    df: pd.DataFrame,
    n_context: int = 7,
    leads: Sequence[int] = (0, 1, 2, 3),
) -> Iterator[Sample]:
    """Gera as amostras válidas de um conjunto.

    Uma amostra só entra se o contexto estiver completo (reanálise em todos os dias e ``obs``
    em todos os dias antes de t) e se houver observação para todos os leads. Assim, todos os
    modelos são avaliados exatamente nas mesmas amostras.
    """
    if n_context < 2:
        raise ValueError("n_context precisa ser >= 2")
    leads = list(leads)
    obs = df[TARGET].to_numpy()
    rea_ok = df[REANALYSIS_FEATURES].notna().all(axis=1).to_numpy()
    obs_ok = ~np.isnan(obs)
    max_lead = max(leads)
    cols = [TARGET, *REANALYSIS_FEATURES]
    for t in range(n_context - 1, len(df) - max_lead):
        lo = t - n_context + 1
        if not (rea_ok[lo : t + 1].all() and obs_ok[lo:t].all()):
            continue
        target = obs[[t + k for k in leads]]
        if np.isnan(target).any():
            continue
        context = df.iloc[lo : t + 1][cols].copy()
        context.iloc[-1, 0] = np.nan
        yield Sample(issue_date=df.index[t], context=context, target=target.astype("float64"))
