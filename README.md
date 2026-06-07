# Distance API

Aplicacao demo para calculo de rotas, validacao de enderecos por CEP e roteirizacao com multiplos pontos. O projeto usa Flask no backend, SQLite para persistencia local e uma interface web em HTML, CSS e JavaScript puro integrada ao Google Maps.

## Funcionalidades

- Cadastro e login de usuarios.
- Calculo de rota simples entre origem e destino.
- Validacao de CEP antes do calculo da rota, com numero opcional.
- Exibicao da rota no mapa com marcadores de origem e destino.
- Resumo com endereco, distancia e tempo estimado.
- Roteirizacao com multiplos pontos.
- Modo com destino fixo.
- Modo com destino automatico, que testa possiveis finais e escolhe a melhor rota.
- Historico de rotas por usuario.
- Endpoint de saude para deploy: `/healthz`.

## Tecnologias

- Python
- Flask
- SQLite
- Requests
- Gunicorn
- HTML
- CSS
- JavaScript puro
- Google Maps JavaScript API
- Google Routes API
- ViaCEP

## Estrutura Principal

```text
app/
  api/routes/        Rotas HTTP da aplicacao
  core/              Configuracoes e excecoes
  providers/         Integracoes externas
  schemas/           Validacoes de entrada
  services/          Regras de negocio
  templates/         Paginas HTML
  utils/             Funcoes auxiliares
static/
  css/               Estilos do frontend
  js/                Codigo JavaScript modularizado
render.yaml          Configuracao para deploy no Render
Procfile             Comando de start para plataformas Python
requirements.txt     Dependencias Python
run.py               Entrada da aplicacao Flask
```

## Como Rodar Localmente

Crie e ative um ambiente virtual:

```bash
python3 -m venv env
source env/bin/activate
```

Instale as dependencias:

```bash
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz do projeto com as variaveis abaixo:

```env
FLASK_APP=run.py
FLASK_DEBUG=True
SECRET_KEY=sua-chave-local
GOOGLE_MAPS_API_KEY=sua-chave-google-routes
GOOGLE_MAPS_JS_API_KEY=sua-chave-google-maps-js
```

Inicie a aplicacao:

```bash
python run.py
```

Acesse no navegador:

```text
http://127.0.0.1:5000
```

## Variaveis de Ambiente

- `SECRET_KEY`: chave usada pelo Flask para sessoes.
- `GOOGLE_MAPS_API_KEY`: chave server-side usada pela Google Routes API.
- `GOOGLE_MAPS_JS_API_KEY`: chave publica usada pelo mapa no frontend.
- `APP_ENV`: use `production` no ambiente de deploy.
- `DATABASE_PATH`: opcional, permite definir um caminho customizado para o SQLite.
- `DEMO_ROUTE_LIMIT`: limite de consultas por usuario na demo. O padrao e `4`.

Nunca envie o arquivo `.env` para o GitHub. Ele ja esta protegido pelo `.gitignore`.

## Deploy

O projeto esta preparado para deploy no Render.

Configurar no ambiente de producao:

```text
APP_ENV=production
SECRET_KEY=<gerada-pelo-render-ou-manual>
DEMO_ROUTE_LIMIT=4
GOOGLE_MAPS_API_KEY=<sua-chave-server-side>
GOOGLE_MAPS_JS_API_KEY=<sua-chave-publica-js>
```

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
gunicorn run:app --bind 0.0.0.0:$PORT
```

Health check:

```text
/healthz
```

Mais detalhes estao em [DEPLOY.md](DEPLOY.md).

## Observacao Sobre SQLite

Para uma demo simples, SQLite atende bem. Em plataformas sem disco persistente, os dados podem ser perdidos em reinicios ou redeploys. Para uma versao publica permanente, configure disco persistente ou migre para PostgreSQL.

## Checklist de Teste

Depois de subir a aplicacao:

1. Acesse `/healthz` e confirme que retorna status ok.
2. Abra a tela inicial.
3. Crie um usuario.
4. Faca login.
5. Calcule uma rota simples.
6. Teste itinerario com destino fixo.
7. Teste itinerario com destino automatico usando 4 ou mais enderecos.
8. Confirme se a rota aparece no mapa e se o resumo mostra distancia e tempo estimado.

## Status

Versao demo preparada para apresentacao e publicacao em portifolio.
