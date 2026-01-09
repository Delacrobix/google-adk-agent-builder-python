import json
import os

import httpx
import requests
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

load_dotenv()

KIBANA_ENDPOINT = os.getenv("KIBANA_ENDPOINT")
ES_API_KEY = os.getenv("ES_API_KEY")
ES_ENDPOINT = os.getenv("ES_ENDPOINT")

es_client = Elasticsearch(ES_ENDPOINT, api_key=ES_API_KEY)

KIBANA_HEADERS = {
    "Authorization": f"ApiKey {ES_API_KEY}",
    "Content-Type": "application/json",
    "kbn-xsrf": "true",
}

INFERENCE_ID = "jina-embeddings"


async def create_kitchen_tool(tool_id, index_pattern, description=None):
    """
    Create an Elasticsearch kitchen tool in Agent Builder.

    Args:
        tool_id: Unique identifier for the tool
        index_pattern: Index pattern to search
        description: Optional description of the tool
    """
    url = f"{KIBANA_ENDPOINT}/api/agent_builder/tools"

    payload = {
        "id": tool_id,
        "type": "index_search",
        "configuration": {"pattern": index_pattern},
    }

    if description:
        payload["description"] = description

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers={
                "Authorization": f"ApiKey {ES_API_KEY}",
                "Content-Type": "application/json",
                "kbn-xsrf": "true",
            },
            json=payload,
        )
        response.raise_for_status()
        return response.json()


def create_inference_endpoint(inference_id=INFERENCE_ID):
    """
    Create an inference endpoint for Jina embeddings.

    Args:
        inference_id: Unique identifier for the inference endpoint
    """
    try:
        # Check if inference endpoint already exists
        try:
            es_client.inference.get(inference_id=inference_id)
            print(
                f"ℹ️  Inference endpoint '{inference_id}' already exists. Skipping creation."
            )
            return False
        except Exception:
            # Endpoint doesn't exist, continue with creation
            pass

        # Create inference endpoint with Jina embeddings v3
        inference_config = {
            "service": "elastic",
            "service_settings": {"model_id": "jina-embeddings-v3"},
        }

        es_client.inference.put(
            task_type="text_embedding", inference_id=inference_id, body=inference_config
        )
        print(f"✅ Inference endpoint '{inference_id}' created successfully")

    except Exception as e:
        print(f"❌ Error creating inference endpoint: {e}")
        raise


def create_index(index_name):
    """
    Create index with mappings if it doesn't exist.

    Args:
        index_name: Name of the index
        mappings: Mapping definition
    """

    if es_client.indices.exists(index=index_name):
        print(f"Index '{index_name}' already exists. Skipping creation.")
        return False

    mappings = {
        "properties": {
            "name": {"type": "text", "copy_to": "semantic_field"},
            "ingredients": {"type": "text", "copy_to": "semantic_field"},
            "allergens": {"type": "keyword", "copy_to": "semantic_field"},
            "procedure": {"type": "text", "copy_to": "semantic_field"},
            "prep_time_minutes": {"type": "integer"},
            "category": {"type": "keyword", "copy_to": "semantic_field"},
            "dietary": {"type": "keyword", "copy_to": "semantic_field"},
            "semantic_field": {
                "type": "semantic_text",
                "inference_id": INFERENCE_ID,
            },
        }
    }

    es_client.indices.create(index=index_name, body={"mappings": mappings})
    print(f"✅ Index '{index_name}' created successfully")
    return True


def build_bulk_actions(documents, index_name):
    """Generator for bulk actions."""
    for doc in documents:
        yield {"_index": index_name, "_source": doc}


def bulk_index_data(documents, index_name):
    """
    Index documents using bulk API.

    Args:
        documents: List of documents to index
        index_name: Name of the index
    """

    try:
        success, failed = bulk(
            es_client,
            build_bulk_actions(documents, index_name),
            refresh=True,
        )
        print(f"📥 {success} documents indexed successfully")
        return success, failed

    except Exception as e:
        print(f"❌ Error during bulk indexing: {str(e)}")
        raise


def create_recipe_search_tool(index_name="cooking-recipes"):
    """Create custom semantic search tool for recipes in Agent Builder."""
    recipe_search_tool = {
        "id": "recipe_semantic_search",
        "type": "index_search",
        "description": "Search kitchen recipes including ingredients, allergens, dietary restrictions, preparation procedures, and cooking times. Uses semantic search to find relevant recipes even without exact keyword matches.",
        "tags": ["semantic"],
        "configuration": {
            "pattern": index_name,
        },
    }

    try:
        response = requests.post(
            f"{KIBANA_ENDPOINT}/api/agent_builder/tools",
            headers=KIBANA_HEADERS,
            json=recipe_search_tool,
        )

        if response.status_code == 200:
            print("✅ Recipe semantic search tool created successfully")
        elif response.status_code == 400:
            # Check if it's because the tool already exists
            if "already exists" in response.text.lower():
                print("ℹ️  Recipe search tool already exists, continuing...")
            else:
                print(f"⚠️  Failed to create tool: {response.status_code}")
                print(f"Response: {response.text}")
        else:
            print(f"⚠️  Failed to create tool: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error creating tool: {e}")


def setup_recipes_index(index_name="cooking-recipes"):
    """
    Complete setup: create index, load recipe data, and create search tool.

    Args:
        index_name: Name of the index to create
    """
    create_inference_endpoint()

    # Default path: dataset.json in the same directory as this file
    dataset_path = "kitchen_agent/dataset.json"

    # Create index
    index_created = create_index(index_name)

    # Load and index data only if index was just created
    if index_created:
        print(f"Index created, loading data from {dataset_path}...")

        with open(dataset_path, "r") as f:
            recipes = json.load(f)
        bulk_index_data(recipes, index_name)

    # Create semantic search tool
    create_recipe_search_tool(index_name)


print("Setting up Elasticsearch index and data...")
setup_recipes_index()
