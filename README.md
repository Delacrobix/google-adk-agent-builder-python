# Kitchen Assistant Agent

An AI agent built with Google Agent Development Kit (ADK) that assists chefs by providing quick information about recipes, ingredients, allergens, and dietary restrictions through semantic search in Elasticsearch.

## Installation

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### 1. Environment Variables

Create a `.env` file in the `agent/` directory by copying the following template:

```bash
# Elasticsearch Configuration
ES_API_KEY="your_elasticsearch_api_key"
ES_ENDPOINT="https://your-elasticsearch-endpoint:9200"
KIBANA_ENDPOINT="https://your-kibana-endpoint:5601"

# Google Gemini API
GOOGLE_API_KEY="your_google_api_key"
```

### 2. Elasticsearch Setup

Run the setup script to create the index, load the recipe dataset, and configure the search tool in Agent Builder:

```bash
python elasticsearch_setup.py
```

## Usage

### Run the Agent with Web Interface

Start the agent with the development web interface:

```bash
adk web --port 8000
```

The interface will be available at: **http://localhost:8000**

### Example Queries

Once the web interface is running, you can ask questions like:

- "Does this recipe contain shellfish?"
- "Give me vegetarian recipes with pasta"
- "Recipes I can prepare with chicken and rice"
- "Recipes from the Mediterranean category"
