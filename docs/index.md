# pm25bench

Benchmark aberto de previsão de **MP2,5 diário** em estações da CETESB, usando a reanálise do
SISAM como entrada.

O pm25bench entrega:

- **data**: lê a reanálise do SISAM e as observações da CETESB e monta uma tabela diária única;
- **models**: o protocolo `Forecaster`, um registro de plugins e quatro baselines;
- **metrics**: MAE, RMSE, viés, correlação, POD, FAR, CSI, ETS e IC por bootstrap em blocos;
- **benchmark**: roda tudo a partir de um YAML e gera tabela, CSVs e figuras;
- **cli**: `pm25bench run | models | fetch | stations`.

Comece pelo [guia rápido](quickstart.md) e leia o [protocolo](protocol.md) antes de
comparar resultados.
