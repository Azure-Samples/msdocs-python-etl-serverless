# Replace with your email you sign in to Azure
#user_email='YOUR-EMAIL-ACCOUNT'
alias='diberry5'
user_email="diberry@microsoft.com"
subscription_id="bb881e62-cf77-4d5d-89fb-29d71e930b66"
local_data_file="./data/segment-country.csv"
echo "subscription_id="$subscription_id

service_location='eastus'
resource_group_name="$alias-etl-resourcegroup"

# Set default subscription
az account set \
    --subscription $subscription_id

# Create an Azure Resource Group to organize the Azure services used in this series logically
az group create \
    --subscription $subscription_id \
    --location $service_location \
    --name $resource_group_name \
    --tags "alias=$alias"

echo "Resource group delete $resource_group_name"

storage_acct_name=$alias"storage"
echo "storage_acct_name = $storage_acct_name"

# Create a general-purpose storage account in your resource group and assign it an identity
az storage account create \
    --name $storage_acct_name \
    --resource-group $resource_group_name \
    --location $service_location \
    --sku Standard_LRS \
    --assign-identity

echo "Storage created $storage_acct_name"

# Assign the 'Storage Blob Data Contributor' role to your user
az role assignment create \
    --assignee $user_email \
    --role 'Storage Blob Data Contributor' \
    --resource-group  $resource_group_name   


echo 'Role assignment created Storage Blob Data Contributor'

abs_container_name='demo-cloudetl-data'
abs_archive_container_name='demo-cloudetl-archive'

# Create a storage container in a storage account.
az storage container create \
    --name $abs_container_name \
    --account-name $storage_acct_name \
    --auth-mode login

echo "Storage container created $abs_container_name"

az storage container create \
    --name $abs_archive_container_name \
    --account-name $storage_acct_name \
    --auth-mode login

echo "Storage archive container created "$abs_archive_container_name

storage_acct_id=$(az storage account show \
                    --name $storage_acct_name  \
                    --resource-group $resource_group_name \
                    --query 'id' \
                    --output tsv)    

# Capture storage account access key1
storage_acct_key1=$(az storage account keys list \
                        --resource-group $resource_group_name \
                        --account-name $storage_acct_name \
                        --query [0].value \
                        --output tsv)         

adls_acct_name=$alias"datalake"
fsys_name='processed-data-demo'
dir_name='finance_data'

# Create a ADLS Gen2 account
az storage account create \
    --name $adls_acct_name \
    --resource-group $resource_group_name \
    --kind StorageV2 \
    --hns \
    --location $service_location \
    --assign-identity  

echo "ADLS Gen2 created $adls_acct_name"


adls_acct_key1=$(az storage account keys list \
                    --resource-group $resource_group_name \
                    --account-name $adls_acct_name \
                    --query [0].value --output tsv)      

# Create a file system in ADLS Gen2
az storage fs create \
    --name $fsys_name \
    --account-name $adls_acct_name \
    --auth-mode login

echo "ADLS Gen2 file system created $fsys_name"

# Create a directory in ADLS Gen2 file system
az storage fs directory create \
    --name $dir_name \
    --file-system $fsys_name \
    --account-name $adls_acct_name \
    --auth-mode login

echo "ADLS Gen2 directory created $dir_name"

key_vault_name="keyvalut-etl-"$alias

# Provision new Azure Key Vault in our resource group
az keyvault create  \
    --location $service_location \
    --name $key_vault_name \
    --resource-group $resource_group_name    

echo "Key vault created $key_vault_name"

abs_secret_name='abs-access-key1'
adls_secret_name='adls-access-key1'

# Create Secret for Azure Blob Storage Account
az keyvault secret set \
    --vault-name $key_vault_name \
    --name $abs_secret_name \
    --value $storage_acct_key1

echo "Key vault storage secret created $abs_secret_name"

# Create Secret for Azure Data Lake Storage Account
az keyvault secret set \
    --vault-name $key_vault_name \
    --name $adls_secret_name \
    --value $adls_acct_key1    

echo "Key vault data lake secret created $adls_secret_name"

funcapp_name="etl-"$alias

# Create a serverless function app in the resource group.
az functionapp create \
    --name $funcapp_name \
    --storage-account $storage_acct_name \
    --consumption-plan-location $service_location \
    --resource-group $resource_group_name \
    --os-type Linux \
    --runtime python \
    --runtime-version 3.9 \
    --functions-version 4

# Update function app's settings to include Azure Key Vault environment variable.
az functionapp config appsettings set \
    --name $funcapp_name \
    --resource-group $resource_group_name \
    --settings "KEY_VAULT_NAME="$key_vault_name

# Update function app's settings to include Azure Blob Storage Access Key in Azure Key Vault secret environment variable.
az functionapp config appsettings set \
    --name $funcapp_name \
    --resource-group $resource_group_name \
    --settings  "ABS_SECRET_NAME="$abs_secret_name

# Update function app's settings to include Azure Data Lake Storage Gen 2 Access Key in Azure Key Vault secret environment variable.
az functionapp config appsettings set \
    --name $funcapp_name \
    --resource-group $resource_group_name \
    --settings  "ADLS_SECRET_NAME="$adls_secret_name

# Generate managed service identity for function app
az functionapp identity assign \
    --resource-group $resource_group_name \
    --name $funcapp_name

# Capture function app managed identity id
func_principal_id=$(az resource list \
            --name $funcapp_name \
            --query [*].identity.principalId \
            --output tsv)

# Capture key vault object/resource id
kv_scope=$(az resource list \
                --name $key_vault_name \
                --query [*].id \
                --output tsv)

# set permissions policy for function app to key vault - get list and set
az keyvault set-policy \
    --name $key_vault_name \
    --resource-group $resource_group_name \
    --object-id $func_principal_id \
    --secret-permission get list set

# Create a 'Key Vault Contributor' role assignment for function app managed identity
az role assignment create \
    --assignee $func_principal_id \
    --role 'Key Vault Contributor' \
    --scope $kv_scope

# Assign the 'Storage Blob Data Contributor' role to the function app managed identity
az role assignment create \
    --assignee $func_principal_id \
    --role 'Storage Blob Data Contributor' \
    --resource-group  $resource_group_name

# Assign the 'Storage Queue Data Contributor' role to the function app managed identity
az role assignment create \
    --assignee $func_principal_id \
    --role 'Storage Queue Data Contributor' \
    --resource-group  $resource_group_name

az storage blob upload \
    --account-name $storage_acct_name \
    --container-name $abs_container_name \
    --auth-mode login \
    --name $local_data_file \
    --file $local_data_file

echo "Storage file upload "$local_data_file

# Deploy local code to cloud app
func azure functionapp publish $funcapp_name