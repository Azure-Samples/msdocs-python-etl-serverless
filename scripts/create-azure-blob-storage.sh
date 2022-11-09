# Use the same resource group you create the web app in.
az storage account create \
    --name 'msdocspythoncloudetlabs' \
    --resource-group 'msdocs-python-cloud-etl-rg' \
    --location 'eastus' \ 
    --sku Standard_LRS \
    --assign-identity

# Assign the 'Storage Blob Data Contributor' role to your user
az role assignment create \
    --role "Storage Blob Data Contributor" \
    --assignee <YOUR USER PRINCIPAL NAME> \
    --scope "/subscriptions/<YOUR-SUBSCRIPTION-ID>/resourceGroups/msdocs-python-cloud-etl-rg/providers/Microsoft.Storage/storageAccounts/msdocspythoncloudetlabs"    

az storage container create \
    --name 'msdocs-python-cloud-etl-news-source' \
    --public-access blob \
    --account-name 'msdocspythoncloudetlabs' \
    --auth-mode login