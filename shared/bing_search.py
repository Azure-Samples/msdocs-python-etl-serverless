import json
import logging
import os

import azure.functions as func
from news_search_client import NewsSearchClient
from azure.core.credentials import AzureKeyCredential


def get_news(
    bing_key,
    bing_endpoint="https://api.bing.microsoft.com/v7.0/",
    search_term="Quantum computing",
    count=10,
    market="en-us",
):

    client = NewsSearchClient(
        endpoint=bing_endpoint, credential=AzureKeyCredential(bing_key)
    )

    news_result = client.news.search(query=search_term, market=market, count=count)

    return news_result
