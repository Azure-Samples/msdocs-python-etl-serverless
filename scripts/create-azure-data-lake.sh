# Use 'az account list-locations --output table' to list locations.
# Use the same resource group you create previously.
# Create a ADLS Gen2 account
az storage account create \
    --name msdocspythonetladls \
    --resource-group msdocs-cloud-python-etl-rg \
    --kind StorageV2 \
    --hns \
    --location eastus \
    --assign-identity

# Assign the 'Storage Blob Data Contributor' role to your user
az role assignment create \
    --role "Storage Blob Data Contributor" \
    --assignee <YOUR USER PRINCIPAL NAME> \
    --scope "/subscriptions/<YOUR-SUBSCRIPTION-ID>/resourceGroups/msdocs-python-cloud-etl-rg/providers/Microsoft.Storage/storageAccounts/msdocspythoncloudetladls"

# Create a file system in ADLS Gen2
az storage fs create \
    --name msdocs-python-cloud-etl-processed \
    --account-name msdocspythonetladls

# Create a directory in ADLS Gen2 file system
az storage fs directory create \
    --name news-data \
    --file-system msdocs-python-cloud-etl-processed \
    --account-name msdocspythonetladls