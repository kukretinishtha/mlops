# Create resource group
az group create --name pythonwebapp --location westus
# Create service plan
az appservice plan create --resource-group  pythonwebapp --name pythonwebappplan --is-linux --sku F1
# Create a service where we will be deploying
az webapp create --resource-group pythonwebapp --plan pythonwebappplan --name pythonwebapptest --runtime "Python|3.7"