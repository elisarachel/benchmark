# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/); versões
seguem o [SemVer](https://semver.org/lang/pt-BR/).

## [0.1.0] - 2026-11-04

### Adicionado

- Leitura da reanálise do SISAM (CSV ou ZIP) e das observações horárias da CETESB.
- Média diária no dia CETESB (hora 24 = 00:00 do dia seguinte), mínimo de 18 h válidas.
- Download com cache e verificação SHA-256 (pooch), em commits fixados.
- Divisão temporal em blocos com intervalo e geração de amostras sem vazamento.
- Protocolo `Forecaster`, registro de plugins por entry points e quatro baselines.
- Métricas contínuas, categóricas e IC por bootstrap em blocos.
- Runner configurado por YAML (pydantic), relatório em Markdown/CSV/PNG e CLI.
- Template de plugin, CI, release para o TestPyPI e documentação MkDocs.
