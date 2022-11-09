import logging
import os
import uuid

from azure.storage.blob import BlobServiceClient


def upload_to_blob(azure_credential, data, container_name, blob_name):  # as string?

    account_name = os.environ.get("BLOB_STORAGE_RESOURCE_NAME")
    logging.info("upload_to_blob account_name=%s", account_name)

    account_url = f"https://{account_name}.blob.core.windows.net"
    logging.info("account_url=%s", account_url)

    blob_service_client = BlobServiceClient(account_url, credential=azure_credential)

    blob_client = blob_service_client.get_container_client(container_name).upload_blob(
        blob_name, data
    )

    return blob_client.url
