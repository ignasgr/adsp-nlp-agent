# ADSP NLP TA Agent

This repository contains a local demo of a teaching-assistant chatbot for the University of Chicago course **ADSP-32018: Next-Gen NLP: Transformers, LLMs, and Agentic AI in Practice**.

The system can help with:

- lecture slides
- the syllabus
- lecture notebooks and code
- student absence requests
- saved response-style preferences

## High-Level Architecture

There are two runtime services:

- `app`: the Chainlit chat application and agent runtime
- `ingest`: a batch job that rebuilds the Chroma collections from local course files

The chat system is a small multi-agent architecture:

- **TA Agent**: the only agent that speaks directly to the student
- **Attendance Agent**: handles absence requests and attendance records
- **Lecture Agent**: handles slide and syllabus questions through Chroma
- **Notebook Agent**: handles notebook and code questions through GitHub

The current agent graph is available at [artifacts/agent_graph.png](/Users/ignasg/projects/adsp-nlp-agent/artifacts/agent_graph.png). You can regenerate it with `just visualize`.

## Main Pieces

### App

The app lives under [services/app/src](/Users/ignasg/projects/adsp-nlp-agent/services/app/src).

- [app.py](/Users/ignasg/projects/adsp-nlp-agent/services/app/src/app.py): Chainlit entrypoint, auth, session setup, and streaming responses
- [course_agents/](/Users/ignasg/projects/adsp-nlp-agent/services/app/src/course_agents): TA agent plus delegated agents and their instructions
- [mcp_servers/](/Users/ignasg/projects/adsp-nlp-agent/services/app/src/mcp_servers): active MCP integrations
- [tools/](/Users/ignasg/projects/adsp-nlp-agent/services/app/src/tools): local `function_tool`s for authenticated user memory

### Ingest

The ingestion job lives under [services/ingest/src](/Users/ignasg/projects/adsp-nlp-agent/services/ingest/src).

It loads course documents from [data/](/Users/ignasg/projects/adsp-nlp-agent/data) and writes them to the local Chroma store in [chroma_data/](/Users/ignasg/projects/adsp-nlp-agent/chroma_data).

Current Chroma collections:

- `slides`
- `syllabus`

Each ingest run destroys and recreates the target collection.

## Resources And Storage

### MCP resources

The active MCP servers are:

- **GitHub MCP** for notebook and code access
- **Chroma MCP** for lecture slide and syllabus retrieval

### Local user memory

Some user-specific state is stored locally rather than through MCP:

- [attendance_data/](/Users/ignasg/projects/adsp-nlp-agent/attendance_data): SQLite attendance records
- [preference_data/](/Users/ignasg/projects/adsp-nlp-agent/preference_data): SQLite response-style preferences

The local tools in [tools/user_memory.py](/Users/ignasg/projects/adsp-nlp-agent/services/app/src/tools/user_memory.py) use authenticated user context, so identity comes from the app rather than from model guesses.

## Getting Started

### 1. Put course files in the expected data folders

Place your source materials here:

- slides PDFs in [data/slides](/Users/ignasg/projects/adsp-nlp-agent/data/slides)
- syllabus files in [data/syllabus](/Users/ignasg/projects/adsp-nlp-agent/data/syllabus)

### 2. Create your local environment file

Use [.env.example](/Users/ignasg/projects/adsp-nlp-agent/.env.example) as the template for your local [.env](/Users/ignasg/projects/adsp-nlp-agent/.env).

### 3. Build the services

```bash
just build
```

### 4. Ingest the course materials

```bash
just ingest
```

### 5. Start the app

```bash
just start
```

Then open `http://localhost:8000`.
