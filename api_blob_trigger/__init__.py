import json
import logging

import azure.functions as func

from shared.data_lake import upload_to_data_lake
from shared.transform import clean_documents
from shared.azure_credential import get_azure_default_credential

def main(myblob: func.InputStream):

    logging.info(
        f"Python blob trigger function processed blob \n"
        f"Name: {myblob.name}\n"
        f"Blob Size: {myblob.length} bytes"
    )

    logging.info("Start processing Bing News Search results for '%s'.", {myblob.name})

    # read the blob content as a string.
    search_results_blob_str = myblob.read()

    # decode the string to Unicode, then replace single quotes with double quotes.
    blob_json = search_results_blob_str.decode("utf-8")

    logging.info("Successfully read the blob content as a string.")
    logging.info(blob_json)

    # parse a valid JSON string and convert it into a Python Dictionary
    try:
        data = json.loads(blob_json)
        logging.info("Successfully converted to python list.")
        logging.info(data)

        new_data_dictionary = clean_documents(data)
        logging.info(
            "Successfully processed Bing News Search results for '%s'.", myblob.name
        )

        new_json_str = str(json.dumps(new_data_dictionary))

        file_name = myblob.name.split("/")[1]
        new_file_name = f"processed-{file_name}"

        azure_default_credential = get_azure_default_credential()

        upload_to_data_lake(azure_default_credential, new_file_name, new_json_str)
        logging.info(
            "Successfully uploaded to data lake, old: %s, new: %s", myblob.name, new_file_name
        )

    except ValueError as e:
        logging.info("Error converting %s to python dictionary: %s", myblob.name, e)
