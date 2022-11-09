import json
import logging
import os

import azure.functions as func
from azure.identity import DefaultAzureCredential

from shared.bing_search import get_news
from shared.blob_storage import upload_to_blob
from shared.hash import get_random_hash
from shared.key_vault_secret import get_key_vault_secret


# http://localhost:7071/api/etl1
def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info("/api/news")

    search_term = req.params.get("search_term") or "Quantum Computing"
    count = req.params.get("count") or 10

    key_vault_resource_name = os.environ["KEY_VAULT_RESOURCE_NAME"]
    secret_name = os.environ["KEY_VAULT_SECRET_NAME"]

    bing_key = get_key_vault_secret(key_vault_resource_name, secret_name)

    blob_storage_container_name = os.environ["BLOB_STORAGE_CONTAINER_NAME"]
    bing_news_search_URL = "https://api.bing.microsoft.com/v7.0/news/search"
    hash1 = get_random_hash()

    # Clean up file name
    filename = f"search_results_{search_term}_{hash1}.json".replace(" ", "_").replace(
        "-", "_"
    )

    news_search_results = get_news(bing_key, bing_news_search_URL, search_term, count)

    # Convert the result to JSON and return it
    if news_search_results.value:

        news_item_count = len(news_search_results.value)
        logging.info("news item count: " + str(news_item_count))

        jsonItems = json.dumps([news.as_dict() for news in news_search_results.value])

    blob_url = upload_to_blob(jsonItems, blob_storage_container_name, filename)
    logging.info(f"news uploaded: {blob_url}")

    return filename
