# create service principal with azure cli
az ad sp create-for-rbac 
--name "YOUR_SERVICE_PRINCIPAL_NAME" 
--role contributor --scopes /subscriptions/YOUR_SUBSCRIPTION_ID


