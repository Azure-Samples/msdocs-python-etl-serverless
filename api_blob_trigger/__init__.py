# ./api_blob_trigger/__init__.py
import os
import json
import logging

import azure.functions as func

from shared.azure_credential import get_azure_default_credential
from shared.data_lake import upload_to_data_lake
from shared.transform import clean_documents


def main(myblob: func.InputStream):

    logging.info("Python blob trigger function processed blob \nName: %s \nBlob Size: %s bytes", myblob.name, myblob.length)

    # read the blob content as a string.
    search_results_blob_str = myblob.read()

    # decode the string to Unicode
    blob_json = search_results_blob_str.decode("utf-8")

    # parse a valid JSON string and convert it into a Python dict
    try:

        # Get environment variables
        data_lake_account_name = os.environ.get("DATALAKE_GEN_2_RESOURCE_NAME")
        data_lake_container_name = os.environ.get("DATALAKE_GEN_2_CONTAINER_NAME")
        data_lake_directory_name = os.environ.get("DATALAKE_GEN_2_DIRECTORY_NAME")

        # Get Data
        data = json.loads(blob_json)

        # Clean Data
        new_data_dictionary = clean_documents(data)

        # Prepare to upload
        json_str = json.dumps(new_data_dictionary)
        file_name = myblob.name.split("/")[1]
        new_file_name = f"processed_{file_name}"

        # Get authentication to Azure
        azure_default_credential = get_azure_default_credential()

        # Upload to Data Lake
        upload_to_data_lake(azure_default_credential, data_lake_account_name, data_lake_container_name, data_lake_directory_name, new_file_name, json_str)
        logging.info(
            "Successfully uploaded to data lake, old: %s, new: %s", myblob.name, new_file_name
        )

    except ValueError as err:
        logging.info("Error converting %s to python dictionary: %s", myblob.name, err)
