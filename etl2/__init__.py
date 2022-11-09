import logging
import html
import os
import re
import json
import requests
from bs4 import BeautifulSoup
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient, DataLakeFileClient

from shared.transform import clean_documents
from shared.data_lake import upload_to_data_lake

import azure.functions as func


def main(myblob: func.InputStream):

    logging.info(
        f"Python blob trigger function processed blob \n"
        f"Name: {myblob.name}\n"
        f"Blob Size: {myblob.length} bytes"
    )

    logging.info(f"Start processing Bing News Search results for '{myblob.name}'.")

    # read the blob content as a string.
    search_results_blob_str = myblob.read()

    # decode the string to Unicode, then replace single quotes with double quotes.
    blob_json = search_results_blob_str.decode("utf-8")

    logging.info(f"Successfully read the blob content as a string.")
    logging.info(blob_json)

    # parse a valid JSON string and convert it into a Python Dictionary
    try:
        data = json.loads(blob_json)
        logging.info(f"Successfully converted to python list. {(type(data))}")
        logging.info(data)

        new_data_dictionary = clean_documents(data)
        logging.info(
            f"Successfully processed Bing News Search results for '{myblob.name}'."
        )

        new_json_str = str(json.dumps(new_data_dictionary))

        file_name = myblob.name.split("/")[1]
        new_file_name = f"processed-{file_name}"

        upload_to_data_lake(new_file_name, new_json_str)
        logging.info(
            f"Successfully uploaded to data lake, old: {myblob.name}, new: {new_file_name}"
        )

    except ValueError as e:
        logging.info(f"Error converting {myblob.name} to python dictionary: {e}")
