```mermaid
graph TB
    subgraph Google["Google ADK"]
        VA[Voice Agent]
        Live[Gemini LiveAPI]
    end

    subgraph Gemini["Gemini Models"]
        G3[Gemini 3]
    end

    subgraph Elastic["Elastic Stack"]
        AB[Agent Builder]
        Tool[tools]
        ES[Elasticsearch<br/>cooking-recipes index]
    end

    VA -->|uses| Live
    Live -->|powered by| G3
    VA -->|MCP| AB
    AB -->|powered by| G3
    AB -->|uses| Tool
    Tool -->|queries| ES

    style VA fill:#fff4e6
    style Live fill:#fff4e6
    style G3 fill:#e3f2fd
    style AB fill:#f3e5f5
    style Tool fill:#f3e5f5
    style ES fill:#e8f5e9
```
