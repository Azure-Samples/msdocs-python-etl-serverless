import json
import logging

import azure.functions as func

from shared.azure_credential import get_azure_default_credential
from shared.data_lake import upload_to_data_lake
from shared.transform import clean_documents


def main(myblob: func.InputStream):

    logging.info(
        "Python blob trigger function processed blob \nName: %s \nBlob Size: %s bytes",
        myblob.name,
        myblob.length,
    )

    logging.info("Start processing Bing News Search results for '%s'.", myblob.name)

    # read the blob content as a string.
    search_results_blob_str = myblob.read()

    # decode the string to Unicode
    blob_json = search_results_blob_str.decode("utf-8")

    logging.info("Successfully read the blob content as a string.")
    logging.info(blob_json)

    # parse a valid JSON string and convert it into a Python dict
    try:
        data = json.loads(blob_json)
        logging.info("Successfully converted to python list.")
        logging.info(data)

        new_data_dictionary = clean_documents(data)
        logging.info(
            "Successfully processed Bing News Search results for '%s'.", myblob.name
        )

        new_json_str = json.dumps(new_data_dictionary)

        file_name = myblob.name.split("/")[1]
        new_file_name = f"processed_{file_name}"

        azure_default_credential = get_azure_default_credential()

        upload_to_data_lake(azure_default_credential, new_file_name, new_json_str)
        logging.info(
            "Successfully uploaded to data lake, old: %s, new: %s",
            myblob.name,
            new_file_name,
        )

    except ValueError as err:
        logging.info("Error converting %s to python dictionary: %s", myblob.name, err)
