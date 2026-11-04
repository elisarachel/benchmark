# pm25bench

Benchmark aberto de **previsão de MP2,5 diário** em estações da CETESB, usando a
**reanálise do SISAM** como entrada. Uma biblioteca Python instalável que padroniza
dados, modelos, métricas e execução, para que todos os trabalhos da turma possam ser comparados.

```bash
uv sync                                       # instala o ambiente exato do uv.lock
uv run pm25bench models                       # modelos instalados
uv run pm25bench run configs/benchmark.yaml   # baixa os dados e roda o benchmark
```

## Concepção

**Quem usa?** Quem quer comparar um modelo novo de MP2,5 com as referências sem reescrever
leitura de dados nem avaliação.

**API pública mínima:** `load_config`, `run_benchmark`, `load_model`, `Forecaster`,
`make_samples`, `split_by_time`, `pm25bench.metrics.*`. O resto é interno.

**Fora do escopo:** framework de treino, visualização sofisticada, operação em tempo real
(Docker foi retirado desta versão).

## O contrato do pm25bench v0.1

Igual para todos os modelos. Mudar qualquer item é uma *breaking change* (nova versão MINOR).

| Item | Definição |
|---|---|
| Alvo | MP2,5 **diário** (média das 24 h, mínimo de 18 h válidas) na estação CETESB 73 – Congonhas, µg/m³ ([dados](https://github.com/elisarachel/benchmark_pm2_5)) |
| Entrada | Reanálise SISAM do município da estação (MP2,5, MP10, O₃, NO₂, CO, SO₂), médias diárias ([dados](https://github.com/RyanAlvesQ/benchmark_cap_408)), e o MP2,5 observado nos dias anteriores |
| Tarefa | Emitida no dia *t*, com contexto de 7 dias (*t*−6 … *t*): reanálise até *t*, observação até *t*−1. Prever o MP2,5 em *t* + lead, leads 0, 1, 2 e 3 dias |
| Divisão | Blocos de tempo: treino 2011–2019, validação 2020–2021, teste 2022–2024, com 7 dias de intervalo entre blocos |
| Amostras | Só entram amostras com contexto e alvos completos: todos os modelos são avaliados nas mesmas amostras |
| Baselines | Persistência, climatologia, reanálise bruta, regressão linear |
| Métricas | MAE, RMSE, viés, correlação; POD, FAR, CSI, ETS e viés de frequência nos limiares 15, 25 e 50 µg/m³ |
| Relatório | Por modelo e lead, com IC 95% por bootstrap em blocos de 7 dias |

Os limiares seguem a diretriz diária da OMS (15 µg/m³, 2021), o padrão final da Resolução
CONAMA 491/2018 (25 µg/m³) e o padrão intermediário PI-2 (50 µg/m³).

**Regras do protocolo:** `fit` só vê treino e validação; o teste nunca entra no ajuste
nem na escolha de hiperparâmetros. A observação do dia *t* nunca está no contexto.

## Estrutura

```
pm25bench/
├── pyproject.toml  uv.lock  .python-version
├── configs/           # benchmark.yaml, benchmark_local.yaml, benchmark_synthetic.yaml
├── src/pm25bench/
│   ├── data/          # sisam, cetesb, dataset, splits, synthetic, fetch
│   ├── models/        # base (Protocol), registry (plugins) e baselines
│   ├── metrics/       # continuous, categorical, uncertainty
│   ├── benchmark/     # config (pydantic), runner, report
│   └── cli.py
├── tests/
├── examples/plugin-template/   # ponto de partida para o modelo de cada dupla
├── docs/  mkdocs.yml
└── .github/workflows/          # ci, release (TestPyPI), docs (GitHub Pages)
```

As setas de dependência só descem: `metrics` e `data` não sabem que modelos existem;
só `benchmark` orquestra tudo.

## Dados

Os dados **não vão no pacote**. Há duas formas de usá-los:

- `source: download` (padrão): `pm25bench fetch` baixa os arquivos dos repositórios da turma
  num commit fixado e confere o SHA-256 de cada um (pooch). Ficam em cache em `~/.cache/pm25bench`.
- `source: local`: aponte `sisam_dir` e `cetesb_dir` para clones locais
  (veja `configs/benchmark_local.yaml`).

Os dois caminhos geram a mesma tabela; o hash dela vai para `metadata.json` de cada execução.

## Adicionando o seu modelo

Cada modelo é um plugin: um pacote separado que se registra no grupo `pm25bench.models`.
Copie `examples/plugin-template`, implemente `fit` e `predict` e declare:

```toml
[project.entry-points."pm25bench.models"]
meumodelo = "pm25bench_meumodelo:MeuModelo"
```

Qualquer classe com `name`, `fit(train, val)` e `predict(context, leads)` cumpre o protocolo
`Forecaster`. Veja `docs/plugins.md`.

## Desenvolvimento

```bash
uv sync
uv run pytest                  # testes + cobertura
uv run ruff check . && uv run ruff format --check . && uv run mypy
uv run pre-commit install      # roda o ruff antes de cada commit
uv run --group docs mkdocs serve
```

Commits convencionais (`feat:`, `fix:`, `docs:`, `test:`…), uma branch curta por assunto e PR
para a `main`. Uma tag `v*` publica no TestPyPI.

## Licença e citação

MIT. Para citar, veja `CITATION.cff`.
