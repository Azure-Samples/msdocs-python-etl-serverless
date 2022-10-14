import logging
import os
from io import StringIO
import pandas as pd
from datetime import datetime, timedelta

import azure.functions as func
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

def return_blob_files(container_client, arg_date, std_date_format):
    start_date = datetime.strptime(arg_date, std_date_format).date() - timedelta(days=1)

    blob_files = [blob for blob in container_client.list_blobs() if blob.creation_time.date() >= start_date]

    return blob_files

def read_csv_to_dataframe(container_client, filename, file_delimiter= ','):
    blob_client = container_client.get_blob_client(blob=filename)

    # Retrieve extract blob file
    blob_download = blob_client.download_blob()

    # Read blob file into DataFrame
    blob_data = StringIO(blob_download.content_as_text())
    df = pd.read_csv(blob_data,delimiter=file_delimiter)
    return df

def ingest_relational_data(container_client, blob_file_list):
    df = pd.concat([read_csv_to_dataframe(container_client=container_client, filename=blob_name.name) for blob_name in blob_file_list], ignore_index=True)

    return df

def run_cloud_etl(source_container_client, blob_file_list):
    df = ingest_relational_data(source_container_client, blob_file_list)

    # Check the blob file data
    logging.info(df.head(5))

    return True

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Parameters/Configurations
    arg_date = '2014-07-01'
    std_date_format = '%Y-%m-%d'

    abs_acct_name='stcloudetldemodata'
    abs_acct_url=f'https://{abs_acct_name}.blob.core.windows.net/'
    abs_container_name='demo-cloudetl-data'

    try:
        # Set variables from appsettings configurations/Environment Variables.
        key_vault_name = os.environ["KEY_VAULT_NAME"]
        key_vault_Uri = f"https://{key_vault_name}.vault.azure.net"
        blob_secret_name = os.environ["ABS_SECRET_NAME"]

        # Authenticate and securely retrieve Key Vault secret for access key value.
        az_credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=key_vault_Uri, credential= az_credential)
        access_key_secret = secret_client.get_secret(blob_secret_name)

        # Initialize Azure Service SDK Clients
        abs_service_client = BlobServiceClient(
            account_url = abs_acct_url,
            credential = az_credential
        )

        abs_container_client = abs_service_client.get_container_client(container=abs_container_name)

        # Run ETL Application
        process_file_list = return_blob_files(
            container_client = abs_container_client,
            arg_date = arg_date,
            std_date_format = std_date_format
        )

        run_cloud_etl(
            source_container_client = abs_container_client,
            blob_file_list= process_file_list
        )

    except Exception as e:
        logging.info(e)

        return func.HttpResponse(
                f"!! This HTTP triggered function executed unsuccessfully. \n\t {e} ",
                status_code=200
        )

    return func.HttpResponse("This HTTP triggered function executed successfully.")