# Protocolo do benchmark (v0.1)

Sete decisões, escritas e iguais para todos os modelos.

## 1. Tarefa

Na data de emissão *t*, o modelo recebe um **contexto** de 7 dias (*t*−6 … *t*) com:

- `obs`: MP2,5 diário observado na estação, de *t*−6 a *t*−1. Em *t* é `NaN` (o dia ainda
  não terminou);
- `rea_pm2_5`, `rea_pm10`, `rea_o3`, `rea_no2`, `rea_co`, `rea_so2`: reanálise do SISAM para o
  município da estação, de *t*−6 a *t*.

E prevê o MP2,5 diário em *t* + lead, para os leads 0, 1, 2 e 3 dias. O lead 0 corresponde
a estimar o dia corrente a partir da reanálise (correção de viés / *downscaling*).

## 2. Dados

| | Alvo | Entrada |
|---|---|---|
| Fonte | CETESB, estação 73 (Congonhas) | SISAM, reanálise por município |
| Resolução | horária → média diária | diária |
| Período usado | 2011–2024 | 2010–2024 |
| Repositório | elisarachel/benchmark_pm2_5 | RyanAlvesQ/benchmark_cap_408 |

A média diária usa o dia CETESB (01:00 até 24:00, registrada como 00:00 do dia seguinte) e
exige pelo menos 18 horas válidas.

## 3. Divisão

Blocos contínuos, **nunca aleatórios**: dias vizinhos de MP2,5 são muito parecidos.

- treino: até 31/12/2019;
- validação: 08/01/2020 a 31/12/2021 (atenção: inclui o período de pandemia);
- teste: a partir de 08/01/2022.

## 4. Baselines

| Modelo | Ideia |
|---|---|
| `persistence` | amanhã = último dia medido (*t*−1) |
| `climatology` | média do treino para aquela época do ano (±15 dias) |
| `reanalysis_raw` | MP2,5 da reanálise em *t*, sem correção |
| `linear_regression` | regressão ridge por lead com reanálise, persistência e sazonalidade |

## 5. Métricas

Contínuas: MAE, RMSE, viés (`mean(F − O)`) e correlação de Pearson.

Categóricas, para cada limiar (dia é evento se MP2,5 ≥ limiar): POD, FAR, CSI, ETS e viés
de frequência. Limiares: 15 µg/m³ (diretriz diária da OMS, 2021), 25 µg/m³ (padrão final da
CONAMA 491/2018) e 50 µg/m³ (padrão intermediário PI-2).

## 6. Regras

- `fit` recebe só treino e validação. Consultar o teste para ajustar o modelo invalida o resultado.
- Todos os modelos são avaliados nas mesmas amostras de teste.
- O resultado só vale com `metadata.json` (versão do pm25bench e hash dos dados).

## 7. Relatório

Sempre **por lead e por limiar**: nenhum número único decide. O IC 95% vem de bootstrap
reamostrando semanas inteiras (blocos de 7 dias), não dias isolados.
