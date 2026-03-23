# Architecture

This diagram shows how the Chainlit app, top-level TA agent, delegated agents,
custom tools, MCP servers, and local data stores fit together.

```mermaid
flowchart TD
    U[Student in Chainlit UI] --> A[TA Agent]

    subgraph Session["Per-chat session setup"]
        G1[GitHub MCP Server]
        C1[Chroma MCP Server]
        CTX[AppContext + SQLiteSession]
    end

    A --> PT[get_response_style]
    A --> PU[update_response_style]

    A --> AS[Attendance Agent]
    A --> LS[Lecture Agent]
    A --> NS[Code Agent]

    AS --> T1[get_student_record]
    AS --> T2[request_absence]

    LS --> C1
    NS --> G1

    C1 --> C2[Local Chroma DB]
    C2 --> S1[slides collection]
    C2 --> S2[syllabus collection]

    G1 --> GH[GitHub content access]

    T1 --> DB1[(attendance.sqlite3)]
    T2 --> DB1
    PT --> DB2[(preferences.sqlite3)]
    PU --> DB2

    CTX -. passed into .-> A
```

## Notes

- The `TA Agent` is the only agent that speaks directly to the user.
- Response-style tools are attached directly to the `TA Agent`.
- Attendance tools are attached to the `Attendance Agent`.
- The `Lecture Agent` uses the Chroma MCP server.
- The `Code Agent` uses the GitHub MCP server.
