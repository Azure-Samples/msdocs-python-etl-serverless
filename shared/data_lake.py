# ./shared/data_lake.py
import logging
import os

from azure.storage.filedatalake import DataLakeServiceClient


# Upload the data to Azure Data Lake
# Required RBAC role - Storage Blob Data Owner
def upload_to_data_lake(
    azure_credential,
    data_lake_account_name,
    data_lake_container_name,
    data_lake_directory_name,
    file_name,
    data_str,
):

    # Get the client
    service_client = DataLakeServiceClient(
        account_url=f"https://{data_lake_account_name}.dfs.core.windows.net",
        credential=azure_credential,
    )

    # Get the file system client
    file_system_client = service_client.get_file_system_client(file_system=data_lake_container_name)

    # Get the directory client
    directory_client = file_system_client.get_directory_client(data_lake_directory_name)

    # Get the file client
    file_client = directory_client.get_file_client(file_name)

    # Upload the data
    file_client.upload_data(data_str, overwrite=True)

    return file_name
