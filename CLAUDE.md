# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Kitchen Assistant Agent built with Google Agent Development Kit (ADK) that assists chefs during busy dinner service. The agent uses Elasticsearch semantic search to provide quick information about recipes, ingredients, allergens, and dietary restrictions via MCP (Model Context Protocol).

## Architecture

The system uses a multi-component architecture:

1. **Google ADK Agent** (`kitchen_agent/agent.py`):
   - Core agent using Google's Gemini 2.0 Flash model
   - Configured as an LlmAgent with custom instructions for kitchen assistance
   - Connects to Elasticsearch via MCP protocol using the `mcp-remote` NPX package

2. **Elasticsearch Integration** (`kitchen_agent/elasticsearch_setup.py`):
   - Sets up a `cooking-recipes` index with semantic search capabilities
   - Uses `semantic_text` field type that aggregates recipe data (name, ingredients, allergens, procedure, category, dietary info)
   - Creates an Agent Builder tool (`recipe_semantic_search`) for querying recipes
   - Communicates with Kibana API to register the search tool

3. **MCP Connection Flow**:
   - Agent → Google ADK MCP Toolset → mcp-remote NPX package → Kibana Agent Builder API → Elasticsearch
   - Authentication uses Elasticsearch API key passed via Authorization header

## Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration
Before running, create a `.env` file in the `kitchen_agent/` directory with:
- `ES_API_KEY`: Elasticsearch API key
- `ES_ENDPOINT`: Elasticsearch endpoint URL
- `KIBANA_ENDPOINT`: Kibana endpoint URL
- `GOOGLE_API_KEY`: Google Gemini API key

### Data Setup
```bash
# Initialize Elasticsearch index, load recipe data, and register search tool
# Must be run from the kitchen_agent/ directory
cd kitchen_agent
python elasticsearch_setup.py
```

### Running the Agent
```bash
# Start the web interface from the project root
adk web --port 8000
```
The interface will be available at http://localhost:8000

Note: The `adk` command must be run from the parent directory containing `kitchen_agent/`, not from within the `kitchen_agent/` directory itself.

## Working Directory Context

- **Development files**: Located in `kitchen_agent/` subdirectory
- **Dataset**: `kitchen_agent/dataset.json` contains recipe data
- **ADK session data**: Stored in `kitchen_agent/.adk/session.db`
- **Environment config**: `.env` file should be in `kitchen_agent/` directory

## Key Implementation Details

### Elasticsearch Schema
The `cooking-recipes` index uses these fields:
- `name`, `ingredients`, `procedure` (text fields)
- `allergens`, `category`, `dietary` (keyword fields)
- `prep_time_minutes` (integer)
- `semantic_field` (semantic_text type) - aggregates multiple fields for semantic search

### MCP Tool Configuration
The agent connects to Elasticsearch via:
```python
McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "mcp-remote",
                  f"{KIBANA_ENDPOINT}/api/agent_builder/mcp",
                  "--header", f"Authorization:{AUTH_HEADER}"]
        )
    ),
    tool_filter=["recipe_semantic_search"]
)
```

The `tool_filter` ensures only the `recipe_semantic_search` tool is exposed to the agent.

### Agent Instructions
The agent is instructed to be concise and practical, understanding that chefs need quick answers during busy service. It can answer questions about allergens, ingredients, recipes by category, and dietary restrictions.
