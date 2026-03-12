# Startup

This document covers the minimum setup required to run the repo locally.

## Prerequisites

- Docker must be installed and running.
- A local `.env` file is required.
- `just` is optional. You can run the underlying `docker compose` commands directly.

## 1. Create the environment file

Copy `.env.example ` to a `.env` and fill in the required values.

Required keys from `.env.example`:

- `OPENAI_API_KEY`
- `OPENAI_CHAT_MODEL`
- `GITHUB_MCP_URL`
- `GITHUB_PAT`
- `CHAINLIT_AUTH_USERS_JSON`
- `CHAINLIT_AUTH_SECRET`

Authentication note:

- `CHAINLIT_AUTH_USERS_JSON` defines the acceptable app logins. Each entry provides the username, password, and display name for a user who can sign in to the Chainlit app.

## 2. Add course materials

Place your local course files here:

- class slide PDFs in `data/slides`
- syllabus PDFs in `data/syllabus`

The ingest pipeline only scans for `*.pdf` files in those folders. PowerPoint files such as `.ppt` or `.pptx` will not be indexed so convert non-PDF course materials to PDF before running ingestion.

## 3. Build the containers

With `just`:

```bash
just build
```

Without `just`:

```bash
docker compose build
```

## 4. Ingest the course materials

With `just`:

```bash
just ingest
```

Without `just`:

```bash
docker compose run --rm ingest
```

This loads documents from `data/` into the local Chroma store under `chroma_data/`.

## 5. Start the app

With `just`:

```bash
just start
```

Without `just`:

```bash
docker compose up -d --build app
```

Then open `http://localhost:8000`.

## 6. Stop the app

With `just`:

```bash
just stop
```

Without `just`:

```bash
docker compose down
```
