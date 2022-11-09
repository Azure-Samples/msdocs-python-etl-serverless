# Provision new Azure Key Vault in our resource group
az keyvault create  \
    --location 'eastus' \
    --name 'msdocs-python-etl-kv' \
    --resource-group 'msdocs-python-cloud-etl-rg'

# Create Secret for Bing Search subscription key
az keyvault secret set \
    --vault-name 'msdocs-python-etl-kv' \
    --name 'bing-search-resource-key1' \
    --value '<YOUR BING SEARCH SUBSCRIPTION KEY>'