# ./api_search/__init__.py
import json
import logging
import os

import azure.functions as func

from shared.azure_credential import (
    get_azure_default_credential,
    get_azure_key_credential,
)
from shared.bing_search import get_news
from shared.blob_storage import upload_to_blob
from shared.hash import get_random_hash
from shared.key_vault_secret import get_key_vault_secret


# http://localhost:7071/api/search
def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info("Python http trigger function")

    # Get the query parameters
    search_term = req.params.get("search_term", "Quantum Computing")
    count = req.params.get("count", 10)

    # Get environment variables
    key_vault_resource_name = os.environ["KEY_VAULT_RESOURCE_NAME"]
    bing_secret_name = os.environ["KEY_VAULT_SECRET_NAME"]
    bing_news_search_url = os.environ["BING_SEARCH_URL"]
    blob_account_name = os.environ.get("BLOB_STORAGE_RESOURCE_NAME")
    blob_container_name = os.environ["BLOB_STORAGE_CONTAINER_NAME"]

    # Get authentication to Key Vault with environment variables
    azure_default_credential = get_azure_default_credential()

    # Get the secret from Key Vault
    bing_key = get_key_vault_secret(
        azure_default_credential, key_vault_resource_name, bing_secret_name
    )

    # Get authentication to Bing Search with Key
    azure_key_credential = get_azure_key_credential(bing_key)

    # Clean up file name
    random_hash = get_random_hash()
    filename = f"search_results_{search_term}_{random_hash}.json".replace(" ", "_").replace(
        "-", "_"
    )

    # Get the search results
    news_search_results = get_news(azure_key_credential, bing_news_search_url, search_term, count)

    # Convert the result to JSON and save it to Azure Blob Storage
    if news_search_results.value:
        news_item_count = len(news_search_results.value)
        logging.info("news item count: %d", news_item_count)
        json_items = json.dumps([news.as_dict() for news in news_search_results.value])

        blob_url = upload_to_blob(
            azure_default_credential,
            blob_account_name,
            blob_container_name,
            filename,
            json_items,
        )
        logging.info("news uploaded: %s", blob_url)

    return filename
