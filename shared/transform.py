import html
import json
import logging
import re

import requests
from bs4 import BeautifulSoup


def get_content_from_url(url):
    return requests.get(url).content


# clean metadata
def clean_metadata(jsonitem):

    # get news article URL.
    article_url = jsonitem["url"]

    # get and remove any html tags in the name of the news article.
    article_title = remove_html_tags(jsonitem["name"])

    # get and remove any html tags in the short description of the news article.
    article_descr = remove_html_tags(jsonitem["description"])

    # get the new article contents and store text.
    article_text = get_html_text(requests.get(article_url).content)

    return article_url, article_title, article_descr, article_text


# strip HTML tags from a string.
def remove_html_tags(html_text):
    return html.escape(re.compile(r"<[^>]+>").sub("", str(html_text)))


# get all text of a news article, with the assumption that most of the
# article text will use the <p> (paragraph) HTML tag.
def get_html_text(page_html):

    logging.info("get_html_text begin: %s", page_html)

    soup = BeautifulSoup(page_html, "html.parser")
    text = soup.find_all("p", text=True)
    text = remove_html_tags(str(text))

    return text


def normalize_text(text_string):
    # case conversion: Convert all letters of the string in the column to one case(lowercase).
    lower_string = text_string.lower()

    # remove numbers: If numbers are essential to convert to words else remove all numbers
    no_number_string = re.sub(r"\d+", "", lower_string)

    # remove all punctuation except words and space
    no_punc_string = re.sub(
        r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?",
        "",
        no_number_string,
    )

    # remove white spaces: Returns a copy of the string with both leading and trailing characters removed
    no_wspace_string = no_punc_string.strip()

    # decode unicode to properly handle special characters
    json_bytes = no_wspace_string.encode()
    json_str_decoded = json.dumps(json_bytes.decode("utf-8", errors="ignore"))

    return json_str_decoded


def clean_documents(data_dictionary):

    # loop through and process each search result.
    for item in data_dictionary:

        # get news article URL.
        article_url = item["url"]
        logging.info("article_url: %s", article_url)

        # get and remove any html tags in the name of the news article.
        item["name"] = remove_html_tags(item["name"])

        # get and remove any html tags in the short description of the news article.
        item["description"] = remove_html_tags(item["description"])
        logging.info("description: %s", article_url)

        # get the new article contents and store text.
        article_text = get_html_text(requests.get(article_url).content)
        logging.info("article text returned")

        # remove any html tags in the news article's text.
        article_text = remove_html_tags(article_text)
        logging.info("remove_html_tags returned")

        # preprocess/normalize new article's text to make it easier to
        # consume by analytic applications.
        article_text_norm = normalize_text(article_text)
        logging.info("normalize_text returned")

        # add new data to dictionary
        item["article_text"] = article_text_norm

    logging.info("clean_documents: %s", data_dictionary)

    return data_dictionary
