# Instructions:
# Login to Azure CLI before running this script
# Run this script from the same terminal or command prompt where you logged in
# Set the variables below to match your needs

# If runing on windows - set this environment variable
export MSYS_NO_PATHCONV=1

# Troubleshooting
# If you get the error when running script such as "InvalidSchema: No connection adapters were found for 'C:/Program Files/Git/subscriptions/"
# then you need to set the environment variable MSYS_NO_PATHCONV=1 - displayed at top of script"

let "randomIdentifier=$RANDOM*$RANDOM"
echo $randomIdentifier

## Variables you need to set
region="westus" # region where resources will be created
alias="" # alias of the user such as jsmith
domain="microsoft.com" # domain of the user such as microsoft.com
user=$alias$domain
subscriptionid="" # subscription id of the user

# Create a resource group.
resourcegroupname="py-etl-$randomIdentifier-$alias"
echo "Creating resource group $resourcegroupname in $region"

az group create --name $resourcegroupname --location $region --tags "alias"=$alias

# Create Bing Search v7 account
bingsearchname="bingsearch$randomIdentifier"
bingsearchurl="https://api.bing.microsoft.com/v7.0/"
echo "Creating Bing Search v7 account $bingsearchname in $region"
az search service create \
    --resource-group $resourcegroupname 
    --name $bingsearchname 
    --sku free 
    --location $region

# Get Bing Search v7 key
bingsearchkey=$(az search admin-key show --resource-group $resourcegroupname --service-name $bingsearchname --query "primaryKey" -o tsv)

# Provision new Azure Key Vault in our resource group
keyvaultname=kv$randomIdentifier
echo "Creating key vault $keyvaultname in $region"

az keyvault create  \
    --location $region \
    --name $keyvaultname \
    --resource-group $resourcegroupname

# Assign the 'Key Vault Secrets User' role to your user
echo "Assigning Key Vault Secrets User role to $user"

az role assignment create \
    --role "Key Vault Secrets User" \
    --assignee $user \
    --scope "/subscriptions/$subscriptionid/resourceGroups/$resourcegroupname/providers/Microsoft.KeyVault/vaults/$keyvaultname"

# Add secret to Key Vault
bingsearchkeysecretname=bing-search-resource-key1
echo "Adding secret to key vault $keyvaultname with secret named $bingsearchkeysecretname"

az keyvault secret set \
    --vault-name $keyvaultname \
    --name $bingsearchkeysecretname \
    --value $bingsearchkey

# Create azure storage account
storageaccountname=blobstore$randomIdentifier
echo "Creating storage account $storageaccountname in $region"

az storage account create \
    --name $storageaccountname \
    --resource-group $resourcegroupname \
    --allow-blob-public-access false \
    --location $region \ 
    --sku "Standard_LRS"

# Assign the 'Storage Blob Data Contributor' role to your user
echo "Assigning Storage Blob Data Contributor role to $user on storage account $storageaccountname"

az role assignment create \
    --role "Storage Blob Data Contributor" \
    --assignee $user \
    --scope "/subscriptions/$subscriptionid/resourceGroups/$resourcegroupname/providers/Microsoft.Storage/storageAccounts/$storageaccountname"

# Get connection string for storage account
echo "Get connection string for storage account"

# Capture connection string in variable
connectionstring=$(az storage account show-connection-string \
    --resource-group $resourcegroupname \
    --name $storageaccountname \
    --query "connectionString")

# Create container for Azure Blob Storage
containername="msdocs-python-cloud-etl-news-source"
echo "Create container for Azure Blob Storage"

az storage container create \
    --account-name $storageaccountname \
    --name $containername 

# Enable last access tracking on the container
echo "Enable last access tracking on $storageaccountname"

az storage account blob-service-properties update \
    --resource-group $resourcegroupname \
    --account-name $storageaccountname \
    --enable-last-access-tracking true


# Create Data Lake Storage Gen2 account
datalakeaccountname=datalake$randomIdentifier
echo "Create Data Lake Storage Gen2 account"

az storage account create \
    --name $datalakeaccountname \
    --resource-group $resourcegroupname \
    --kind StorageV2 \
    --hns \
    --allow-blob-public-access false
    --location $region

# Assign the 'Storage Blob Data Contributor' role to your user
echo "Assigning Storage Blob Data Contributor role to $user on data lake account $datalakeaccountname"

az role assignment create \
    --role "Storage Blob Data Contributor" \
    --assignee $user \
    --scope "/subscriptions/$subscriptionid/resourceGroups/$resourcegroupname/providers/providers/Microsoft.Storage/storageAccounts/$datalakeaccountname"

# Create a file system (container) in Data Lake
filesystem="msdocs-python-cloud-etl-processed"
echo "Create a file system in Data Lake"

az storage fs create \
    --name $filesystem \
    --account-name $datalakeaccountname

# Create a directory in Data Lake file system
directory="news"
echo "Create a directory $directory in Data Lake file system $filesystem on account $datalakeaccountname"

az storage fs directory create \
    --account-name $datalakeaccountname 
    --name $directory \
    --file-system $filesystem 

# Create storage account used by Functions app
functionstorageaccountname=storfn$randomIdentifier
echo "Create storage account used by Functions app $functionstorageaccountname"

az storage account create \
    --resource-group $resourcegroupname \
    --name $functionstorageaccountname \
    --sku Standard_LRS

# Create Azure Function app
functionappname=fn$randomIdentifier
echo "Create Azure Function app $functionappname"

az functionapp create \
    --resource-group $resourcegroupname \
    --storage-account $functionstorageaccountname
    --name $functionappname \ 
    --consumption-plan-location $region \ 
    --runtime python \
    --runtime-version 3.9 \
    --functions-version 4 \
    --os-type linux \
    --assign-identity [system] \

# Add system assigned managed identity to Azure Function
echo "Add system assigned managed identity to Azure Function"

identityprincipal=$(az functionapp identity assign \
    --resource-group $resourcegroupname \
    --name fn$randomIdentifier \
    --identities [system] \
    --query "identity.principalId" -o tsv) 

# Create new host key
hostkeyname=hostkey$randomIdentifier
echo "Create new host key $hostkeyname"

hostkeyvalue=$(az functionapp keys set \
    --resource-group $resourcegroupname \
    --name $functionappname \
    --key-type functionKeys 
    --key-name $hostkeyname)

# Add environment variables to Azure Function
echo "Add environment variables to Azure Function"

az functionapp config appsettings set \
    --resource-group $resourcegroupname \
    --name $functionappname \
    --settings "BLOB_STORAGE_RESOURCE_NAME=$storageaccountname BLOB_STORAGE_CONTAINER_NAME=$containername KEY_VAULT_RESOURCE_NAME=$keyvaultname KEY_VAULT_SECRET_NAME=$bingsearchkeysecretname DATALAKE_GEN_2_RESOURCE_NAME=$datalakeaccountname DATALAKE_GEN_2_CONTAINER_NAME=$filesystem DATALAKE_GEN_2_DIRECTORY_NAME=$directory BING_SEARCH_URL=$bingsearchurl"

# Add Fn identity to Key Vault
keyvaultsecretrole="Key Vault Secrets User"
echo "Assigning Key Vault Secrets User role to system assigned identity $identitypricipal on Key Vault $keyvaultname"
az role assignment create \
    --role $keyvaultsecretrole \
    --assignee $identityprincipal \
    --scope "/subscriptions/$subscriptionid/resourceGroups/$resourcegroupname/providers/Microsoft.KeyVault/vaults/$keyvaultname"

# Add Fn identity to Storage
storageblobdatacontributor="Storage Blob Data Contributor"
echo "Assigning Storage Blob Data Contributor role to system assigned identity $identityprincipal on storage account $storageaccountname"

az role assignment create \
    --role storageblobdatacontributor \
    --assignee $identityprincipal \
    --scope "/subscriptions/$subscriptionid/resourceGroups/$resourcegroupname/providers/Microsoft.Storage/storageAccounts/$storageaccountname"

# Add Fn identity to Data Lake
datalakedatacontributor="Storage Blob Data Contributor"
echo "Assigning Storage Blob Data Contributor role to system assigned identity $identityprincipal on data lake account $datalakeaccountname"

az role assignment create \
    --role $datalakedatacontributor \
    --assignee $identityprincipal \
    --scope "/subscriptions/$subscriptionid/resourceGroups/$resourcegroupname/providers/Microsoft.Storage/storageAccounts/$datalakeaccountname"

# Final output
echo "Resource group: $resourcegroupname"
echo "Key vault: $keyvaultname with secret $bingsearchkeysecretname"
echo "Bing Search v7 account: $bingsearchname and key $bingsearchkey and search url $bingsearchurl"
echo "Storage account: $storageaccountname and container name $containername connection string $connectionstring"
echo "Data Lake Storage Gen2 account: $datalakeaccountname with file system $filesystem and directory $directory"
echo "Azure Function app: $functionappname with host key named $hostkeyname and value $hostkeyvalue"
