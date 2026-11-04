# Guia rápido

## Instalação

```bash
git clone https://github.com/<usuario>/pm25bench
cd pm25bench
uv sync
```

Ou, depois da primeira release:

```bash
uvx --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    --from pm25bench pm25bench --help
```

## Rodar o benchmark

```bash
uv run pm25bench run configs/benchmark_synthetic.yaml   # dados sintéticos, segundos
uv run pm25bench fetch                                   # baixa os dados (~95 MB)
uv run pm25bench run configs/benchmark.yaml              # benchmark oficial
```

Saídas em `results/`:

| Arquivo | Conteúdo |
|---|---|
| `leaderboard.md` | Tabela por modelo e lead |
| `scores.csv` | Todas as métricas, todos os limiares, com IC 95% |
| `predictions.csv` | Uma linha por modelo, amostra e lead (obs e previsão) |
| `metadata.json` | Versão do pm25bench, hash dos dados, configuração, Python |
| `mae_by_lead.png`, `csi_<limiar>_by_lead.png` | Curvas por lead |

## Usar como biblioteca

```python
from pm25bench import load_config, run_benchmark
from pm25bench.metrics import csi, mae

cfg = load_config("configs/benchmark.yaml")
result = run_benchmark(cfg)
print(result.scores[["model", "lead", "mae", "csi_25"]])
```
