# Guida Docker BlenderAI

Questa guida spiega come containerizzare BlenderAI, eseguire l'API server e integrare un database Postgres opzionale.

## Prerequisiti
- Docker 24+
- Docker Compose V2
- API key per almeno un provider: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`

## Build dell'immagine
```bash
docker build -t blenderai .
```

## Esecuzione standalone
```bash
docker run --rm -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e BLENDER_AI_MODEL=auto \
  blenderai
```

### Volumi suggeriti
- `./config:/app/blenderAI/config` per configurazioni persistenti
- `./data:/app/blenderAI/data` per cache o asset
- `./logs:/app/blenderAI/logs` per i log applicativi

## Compose con Postgres
```bash
docker compose --profile postgres up -d
```
- API: http://localhost:8000
- Postgres: `postgresql://blenderai:blenderai@localhost:5432/blenderai`
- Variabili ambiente principali nel `docker-compose.yml` (override via `.env`)

> Senza profilo `postgres`, parte solo il servizio API.

## Verifica e health check
```bash
curl http://localhost:8000/health
```
Risposta attesa:
```json
{"status": "ok", "version": "4.2"}
```

## Troubleshooting
- **Errore API key mancante**: assicurati di settare almeno una chiave (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`).
- **Porta occupata**: modifica `BLENDER_AI_PORT` e la mappatura host (`-p 8080:8000`).
- **Postgres non disponibile**: controlla `docker compose logs db` e che `DATABASE_URL` punti al servizio corretto.
- **Dipendenze native**: l'immagine include gli header necessari per `psycopg2`; se aggiungi pacchetti extra, ricostruisci con `docker build --no-cache -t blenderai .`.
