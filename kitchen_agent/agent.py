import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp.client.stdio import StdioServerParameters

load_dotenv()

KIBANA_ENDPOINT = os.getenv("KIBANA_ENDPOINT")
ELASTIC_API_KEY = os.getenv("ES_API_KEY")

# Elastic Agent Builder MCP connection
AUTH_HEADER = f"ApiKey {ELASTIC_API_KEY}"

root_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="kitchen_assistant_agent",
    instruction="""You are a kitchen assistant that helps chefs during busy dinner service.
    You can answer questions about recipes.

    Use the Elasticsearch tools to search the cooking-recipes index and provide quick answers like:
    - Does a dish contain specific allergens (e.g., shellfish)?
    - Recipes that can be prepared with given ingredients
    - I would like to prepare a seafood dish
    - Find recipes by category or dietary restrictions

    Always be concise and practical - chefs need quick answers!""",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y", 
                        "mcp-remote",
                        f"{KIBANA_ENDPOINT}/api/agent_builder/mcp",
                        "--header",
                        f"Authorization:{AUTH_HEADER}",
                    ],
                ),
            ),
            tool_filter=["recipe_semantic_search"],
        )
    ],
)
