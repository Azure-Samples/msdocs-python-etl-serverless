import logging
import os
import uuid

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient


def upload_to_blob(data, container_name, blob_name):  # as string?

    account_name = os.environ.get("BLOB_STORAGE_RESOURCE_NAME")
    logging.info(f"upload_to_blob account_name={account_name}")
    unique_id = uuid.uuid4()
    unique_file_name = f"{unique_id}_{blob_name}"
    account_url = f"https://{account_name}.blob.core.windows.net"
    logging.info(f"account_url={account_url}")

    default_credential = DefaultAzureCredential()

    blob_service_client = BlobServiceClient(account_url, credential=default_credential)

    blob_client = blob_service_client.get_container_client(container_name).upload_blob(
        unique_file_name, data
    )

    return blob_client.url
