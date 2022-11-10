# ./shared/blob_storage.py
import logging
import os

from azure.storage.blob import BlobServiceClient


# Upload the data to Azure Blob Storage
def upload_to_blob(azure_credential, account_name, container_name, blob_name, data):  # as string?

    logging.info("upload_to_blob account_name=%s", account_name)

    # Get the account URL
    account_url = f"https://{account_name}.blob.core.windows.net"

    # Create a client
    blob_service_client = BlobServiceClient(account_url, credential=azure_credential)

    # Get the container, and upload the data
    blob_client = blob_service_client.get_container_client(container_name).upload_blob(
        blob_name, data
    )

    return blob_client.url
