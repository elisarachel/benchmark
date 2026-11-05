"""Leitura das previsões do CAMS (trilha opcional), já em médias diárias na estação.

Cada linha é uma data de emissão t. A coluna ``fc_<var>_l{k}`` é a média diária (dia CETESB)
da previsão de ``<var>`` emitida na rodada 00 UTC de t para o dia t + k, em µg/m³.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

#: Prefixo de toda coluna de previsão.
FORECAST_PREFIX = "fc_"


def forecast_columns(df: pd.DataFrame) -> list[str]:
    """Nomes das colunas de previsão (``fc_*``) de uma tabela, em ordem alfabética."""
    # filtra pelo prefixo e ordena para que a ordem não dependa do arquivo de origem
    return sorted(str(c) for c in df.columns if str(c).startswith(FORECAST_PREFIX))


def read_cams_forecast(directory: str | Path, station: int) -> pd.DataFrame:
    """Lê as previsões diárias de uma estação: ``<directory>/<station>/*.csv``.

    Parameters
    ----------
    directory : path
        Pasta ``data/`` do repositório de previsões, com uma subpasta por estação.
    station : int
        Código CETESB da estação.

    Returns
    -------
    pandas.DataFrame
        Índice diário ``date`` (data de emissão), só as colunas ``fc_*`` em ``float64``,
        sem datas duplicadas e ordenado.

    Raises
    ------
    FileNotFoundError
        Se a pasta da estação não tiver nenhum CSV.
    """
    # pasta da estação
    folder = Path(directory) / str(station)
    # arquivos anuais, em ordem
    files = sorted(folder.glob("*.csv"))
    # sem arquivos, a trilha de previsão não pode ser montada
    if not files:
        raise FileNotFoundError(
            f"nenhum CSV de previsão do CAMS da estação {station} em {folder}; "
            "confira data.cams_forecast_dir"
        )
    # lê cada ano
    parts = [pd.read_csv(f) for f in files]
    # junta os anos, ignorando arquivos vazios
    df = pd.concat([p for p in parts if not p.empty], ignore_index=True)
    # data de emissão como datetime
    df["date"] = pd.to_datetime(df["date"])
    # uma linha por data de emissão, indexada pela data
    df = df.drop_duplicates("date").set_index("date").sort_index()
    # só as colunas de previsão, em float64
    out = df[forecast_columns(df)].astype("float64")
    # nome do índice igual ao das demais tabelas do benchmark
    out.index.name = "date"
    # devolve a tabela
    return out
