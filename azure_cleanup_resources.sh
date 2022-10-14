# Replace with your email you sign in to Azure
#user_email='YOUR-EMAIL-ACCOUNT'
alias='diberry'
user_email="diberry@microsoft.com"
subscription_id="bb881e62-cf77-4d5d-89fb-29d71e930b66"

echo "subscription_id="$subscription_id

service_location='eastus'
resource_group_name="$alias-etl-resourcegroup"

# Set default subscription
az account set \
    --subscription $subscription_id

# Delete resource group
az group delete \
    --subscription $subscription_id \
    --name $resource_group_name -y

echo "Resource group deleted $resource_group_name"
