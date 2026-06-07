# Deploy no Render

Este projeto esta preparado para deploy como Web Service Python no Render.

## 1. Antes de subir para o GitHub

Confira que o arquivo `.env` nao sera versionado. Ele ja esta no `.gitignore`.

Variaveis necessarias no ambiente de producao:

- `APP_ENV=production`
- `SECRET_KEY`: chave secreta Flask. No `render.yaml`, o Render pode gerar automaticamente.
- `DEMO_ROUTE_LIMIT`: limite de consultas por usuario na demo. O padrao e `4`.
- `GOOGLE_MAPS_API_KEY`: chave server-side usada pela Google Routes API.
- `GOOGLE_MAPS_JS_API_KEY`: chave publica usada pelo Google Maps JavaScript API.

## 2. Configuracao no Render

Crie um novo Blueprint ou Web Service apontando para este repositorio.

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
gunicorn run:app --bind 0.0.0.0:$PORT
```

Health Check Path:

```text
/healthz
```

## 3. Banco SQLite

Por padrao, a aplicacao usa SQLite em `instance/distance_api.sqlite`.

Em planos sem disco persistente, cadastros e historico podem ser perdidos em reinicios ou redeploys. Para uma demo simples no LinkedIn isso funciona, mas para um portifolio permanente prefira:

- adicionar um disco persistente e configurar `DATABASE_PATH`, ou
- migrar para PostgreSQL.

Exemplo com disco persistente:

```text
DATABASE_PATH=/var/data/distance_api.sqlite
```

## Python

A versao do Python esta fixada em `.python-version` como `3.12` para evitar mudancas de runtime entre deploys.

## 4. Chaves Google

Ative as APIs:

- Google Maps JavaScript API
- Google Routes API

Depois que o Render gerar o dominio publico, restrinja a chave `GOOGLE_MAPS_JS_API_KEY` para esse dominio.

## 5. Testes rapidos apos deploy

- Acesse `/healthz`.
- Acesse `/`.
- Crie uma conta.
- Teste uma rota simples.
- Teste itinerario com destino fixo.
- Teste itinerario com destino automatico.
