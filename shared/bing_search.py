from news_search_client import NewsSearchClient


def get_news(
    azure_credential,
    bing_endpoint="https://api.bing.microsoft.com/v7.0/news/search",
    search_term="Quantum computing",
    count=10,
    market="en-us",
):

    client = NewsSearchClient(endpoint=bing_endpoint, credential=azure_credential)

    news_result = client.news.search(query=search_term, market=market, count=count)

    return news_result
