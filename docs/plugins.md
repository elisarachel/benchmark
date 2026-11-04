# Seu modelo como plugin

O pm25bench é fechado para modificação e aberto para extensão: você não precisa mexer no
código dele para adicionar um modelo.

## 1. O contrato

```python
class Forecaster(Protocol):
    name: str

    def fit(self, train: pd.DataFrame, val: pd.DataFrame | None = None) -> None: ...

    def predict(self, context: pd.DataFrame, leads: Sequence[int]) -> np.ndarray: ...
```

- `train` e `val` são tabelas diárias com as colunas `obs` e `rea_*` (índice = data).
  Use `pm25bench.make_samples(train, n_context, leads)` para montar amostras de treino no
  mesmo formato do teste.
- `predict` recebe um contexto (7 linhas) e devolve um array com uma previsão por lead,
  em µg/m³, sem `NaN`.

## 2. O pacote

Copie `examples/plugin-template` e registre a sua classe:

```toml
[project]
name = "pm25bench-meumodelo"
dependencies = ["pm25bench>=0.1,<0.2"]

[project.entry-points."pm25bench.models"]
meumodelo = "pm25bench_meumodelo:MeuModelo"
```

Dependências pesadas (PyTorch, scikit-learn, XGBoost) ficam no **seu** pacote, não no núcleo.

## 3. Rodar

```bash
uv pip install -e ../pm25bench-meumodelo   # no ambiente do pm25bench
uv run pm25bench models                    # deve listar "meumodelo"
```

```yaml
models:
  - name: persistence
  - name: linear_regression
  - name: meumodelo
    kwargs: {hidden: 64}   # argumentos do construtor
```

## 4. Enviar o resultado

PR no repositório central com `leaderboard.md`, `scores.csv` e `metadata.json`. O
`dataset_hash` precisa ser igual ao do benchmark oficial.
