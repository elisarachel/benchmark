# pm25bench-meumodelo (template de plugin)

Modelo de exemplo para o pm25bench. Use como ponto de partida para o seu.

```bash
cp -r examples/plugin-template ../pm25bench-<seu-modelo>
cd ../pm25bench-<seu-modelo>
# renomeie src/pm25bench_meumodelo, a classe, o `name` e o entry point no pyproject.toml
uv sync
uv run pytest
```

Para rodar no benchmark, instale o plugin no mesmo ambiente do pm25bench e adicione o modelo
ao YAML:

```yaml
models:
  - name: persistence
  - name: meumodelo
```
