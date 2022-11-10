---
page_type: sample
languages:
- python
name: "Azure Functions ETL application with Python"
description: "The server application demonstrates how to use Azure Functions as part of an ETL (extract-transform-load) pipe line. Search Bing news, clean the results, and store in Azure Data Lake."
products:
- azure
- azure-functions
- azure-blob-storage
- azure-data-lake
- azure-data-lake-gen2
- azure-data-lake-storage
- azure-key-vault
- vs-code
- bing-search-services
---

# Azure Functions ETL application with Python

The server application demonstrates how to use Azure Functions as part of an ETL (extract-transform-load) pipe line. 

## Architecture

* Search news with Bing News search service
* Save search results to Azure Blob Storage service
* Clean search results 
* Store in Azure Data Lake service

## Azure Services

This project uses the following:

* [Azure Functions](https://learn.microsoft.com/azure/azure-functions/)
    * [HTTP Trigger](https://learn.microsoft.com/azure/azure-functions/functions-bindings-http-webhook): http://localhost:7071/api/search?search_term=seattle&count=5
        * Search
            * Get Bing news **authentication** key from Azure Key vault
            * Query Bing news search for top 5 results for `seattle`
            * Get results as JSON
        * Save
            * Get Blob Storage **authentication** with DefaultAzureCredential from environment
            * Save JSON results into Blob storage with name _like_ `search_results_seattle_OmD9AQrCJvjieqd.json`
        * Success in debug console looks _like_ `Executed 'Functions.api_search' (Succeeded, Id=989f1745-e1a8-4d31-845b-293c8de2601b, Duration=3810ms)`
    * [Blob Trigger](https://learn.microsoft.com/azure/azure-functions/functions-bindings-storage-blob): triggered on file upload to container listed in `function.json`
        * Get Blob 
            * Get Blob Storage **authentication** with connection string named in `function.json`
            * Read blob contents passed in to function
        * Clean data for each article
        * Send JSON to Azure Data lake
            * Get Data lake **authentication** with DefaultAzureCredential from environment
            * Save JSON to Data lake with name _like_ `processed_search_results_seattle_OmD9AQrCJvjieqd.json`
        * Success in debug console looks _like_ `Executed 'Functions.api_blob_trigger' (Succeeded, Id=9f8e23e9-d61f-41e2-af2f-4898ce4562f4, Duration=5594ms)`
* [Azure Blob Storage](https://learn.microsoft.com/azure/storage/blobs/storage-blobs-overview)
    * Store initial search results as JSON file
* [Azure Data Lake Gen 2](https://learn.microsoft.com/azure/storage/blobs/data-lake-storage-introduction)
    * Store final process search results
* [Azure Key Vault](https://learn.microsoft.com/azure/key-vault/secrets/about-secrets)
    * Securely store Bing Search key
* [Bing Search](https://learn.microsoft.com/bing/search-apis/bing-news-search/overview) 
    * Search Bing News

## Getting Started

### Prerequisites

- Python 3.9 
- Node.js LTS and [azure functions core tools 4](https://www.npmjs.com/package/azure-functions-core-tools)
- Azure resources
    - [Azure service principal](./scripts/create-service-principal.sh) for local development
        - Save service principal information to local.settings.json

            ```
            "AZURE_CLIENT_ID":"",
            "AZURE_TENANT_ID":"",
            "AZURE_CLIENT_SECRET":"",
            "AZURE_SERVICE_PRINCIPAL_NAME":""         
            ```
    - Key Vault
        - Save Key Vault information to local.settings.json

            ```
            "KEY_VAULT_RESOURCE_NAME": "",
            ```
        - You don't need to change these settings in local.settings.json

            ```
            "KEY_VAULT_SECRET_NAME": "bing-search-sub-key1",
            ```

    - Bing Search
        - Save Bing Search v7 key to Key Vault secret with name `bing-search-sub-key1`

        - You don't need to change these settings in local.settings.json

            ```
            "BING_SEARCH_URL": "https://api.bing.microsoft.com/v7.0/news/search",
            "BING_SEARCH_KIND": "Bing.Search.v7",
            "BING_SEARCH_KIND_NAME": "Bing Search",            
            ```

    - Azure Blob Storage
        - You can use a single Blob Storage resource as long as hierarchical directories is enabled. This sample assumes Gen 2 Data Lake.
        - Save Blob Storage for search results to local.settings.json

            ```
            "BLOB_STORAGE_RESOURCE_NAME": "",
            "BLOB_STORAGE_CONTAINER_NAME": "",
            "BLOB_STORAGE_CONNECTION_STRING": "",
            ```

            The **BLOB_STORAGE_CONNECTION_STRING** is used by the Function Blob Trigger to access Blob Storage.

    - Azure Data Lake
        - Set Data Lake resource values in local.settings.json

            ```
            "DATALAKE_GEN_2_RESOURCE_NAME": "",
            "DATALAKE_GEN_2_CONTAINER_NAME": "",
            "DATALAKE_GEN_2_DIRECTORY_NAME": "",            
            ```
### Installation

* Install Azure Functions core tools for local development
    ```
    npm i -g azure-functions-core-tools@4 --unsafe-perm true
    ```
* Install Python packages

    ```
    pip -r requirements.txt
    ```

### Quickstart

1. Clone this repository

    ```
    git clone https://github.com/Azure-Samples/msdocs-python-etl-serverless.git
    ```

2. Start function

    ```
    func start
    ```

## Troubleshooting

* Extraneous names: The service principal name and the Bing Search service name and kind aren't necessary in the `local.settings.json` for this sample application to work. These values are helpful when you need to:
    * Assign the service principal in the IAM of a resource
    * Verify the correct Bing Search service was created
* Logging: logging is disabled in the `./host.json` file with the `logging.logLevel.default` property set to error. To see verbose logs, change the value to `Information`.