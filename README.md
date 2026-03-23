# About

This project is a local-only teaching assistant demo for the University of Chicago course `ADSP-32018: Next-Gen NLP: Transformers, LLMs, and Agentic AI in Practice`.

It provides a chat interface that combines course document retrieval, code reference lookup, and a small amount of authenticated user-specific storage.

## What the project does

The app supports a few main categories of student help:

- answers questions about lecture slides
- answers questions about the syllabus
- explains lecture notebooks and course code
- records and reviews student absence requests
- stores a user's saved response-style preference

All of this is exposed through a single Chainlit chat experience.

## How it works

The project runs locally with two main services:

- `app`: the Chainlit application and agent runtime
- `ingest`: a batch process that indexes local course documents into Chroma

At runtime, the chat experience is organized around a top-level `TA Agent` that can delegate to three narrower agents:

- `Attendance Agent`
- `Lecture Agent`
- `Code Agent`

The `Lecture Agent` uses a local Chroma-backed MCP server to retrieve indexed slide and syllabus content.

The `Code Agent` uses a GitHub MCP integration to read course code and notebook-related files.

The `Attendance Agent` uses local tools for absence history and absence submission.

The top-level `TA Agent` also has direct access to response-style preference tools so it can read or update a user's saved formatting preference.

## Data and storage

Course materials are loaded from local folders:

- `data/slides`
- `data/syllabus`

The ingest pipeline currently requires PDF files for indexed course materials.

Indexed course content is stored in a local Chroma database under `chroma_data/`.

User-specific state is stored locally in SQLite:

- attendance records under `attendance_data/`
- response-style preferences under `preference_data/`

## Important constraints

- This is a local-only project intended to run on a developer machine.
- Course materials are sourced from local files rather than a remote content system.
- Slide and syllabus indexing currently depends on PDF inputs.
- GitHub access is used for notebook and code reference tasks.
- Authentication is controlled by `CHAINLIT_AUTH_USERS_JSON` in the local `.env` file.

## Related docs

- Setup instructions: [startup.md](docs/startup.md)
- Architecture diagram: [architecture.md](docs/architecture.md)
