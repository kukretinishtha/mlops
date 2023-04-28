# Mlops
Mlops with Azure <br/>

## Set Up Resources<br/>
1. Create a resource<br/>
az group create --name <resource-group> --location <location> <br/>

2. Create ML Workspace <br/>
az ml workspace create -w <workspace-name> -g <resource-group> <br/>

3. Create Azure account and define the SKU <br/>
az storage account create --name <storage-account-name> \ <br/>
    --resource-group <resource-group> \ <br/>
    --location <location> \ <br/>
    --sku Standard_ZRS \ <br/>
    --encryption-services blob <br/>

4. Get the kwy for this storage account <br/>
az storage account keys list --account-name <storage-account-name> --resource-group <resource-group> <br/>

5. Create Service Principal with password authentication <br/>
az ad sp create-for-rbac --name <spn-name> <br/>

6. Create an Azure KeyVault <br/>
az keyvault create --name <keyvault-name> \ <br/>
    --resource-group <resource-group> \ <br/>
    --location <location> <br/>

6. Store Secret Key in Azure Key Vault <br/>
az keyvault secret set --vault-name <keyvault-name> --name "StorageAccountKey" --value <storage-account-key> <br/>
az keyvault secret set --vault-name <keyvault-name> --name "SpnPassword" --value <service-principle-password> <br/>

7. Give Service Principle Access to key vault <br/>
az keyvault set-policy -n <keyvault-name> \ <br/>
    --spn <service-principle-app-id> \ <br/>
    --secret-permissions get list set delete \ <br/>
    --key-permissions create decrypt delete encrypt get list unwrapKey wrapKey <br/>

8. az account show <br/>

## Set up keys and password in Azure Devops Organization
1. Add keyVault to your library as below <br/>
![Screenshot](KeyVault.png)

2. Add ProductionEnvironmentVariables to your libarary as below <br/>
![Screenshot](ProductionEnvironmentVars.png)


## Project Folder Structure
MLOPS <br/>
    |-src <br/>
    |    |-my_custom_package <br/>
    |    |    |-scripts <br/>
    |    |        |-call_web_service.py <br/>
    |    |    |-test <br/>
    |    |    |    |-testdata/ <br/>
    |    |    |    |-test_aml_interface.py <br/>
    |    |    |    |-test_blob_storage_interface.py <br/>
    |    |    |    |-test_create_aml_env.py <br/>
    |    |    |    |-test_create_aml_experiment.py <br/>
    |    |    |    |-test_create_data.py <br/>
    |    |    |    |-test_deploy.py <br/>
    |    |    |    |-test_deploy_aml_model.py <br/>
    |    |    |    |-test_score.py <br/>
    |    |    |    |-test_transform_data.py <br/>
    |    |    |-utils <br/>
    |    |    |    |-aml_interface.py <br/>
    |    |    |    |-blob_storage_interface.py <br/>
    |    |    |    |-const.py <br/>
    |    |    |    |-transform_data.py <br/>
    |    |    |-create_aml_env.py <br/>
    |    |    |-create_aml_experiment.py <br/>
    |    |    |-create_data.py <br/>
    |    |    |-deploy_aml_data.py <br/>
    |    |    |-cscore.py <br/>
    |    |    |-train.py <br/>
    |    |-setup.py <br/>
    |-ci_pipeline.yml <br/>
    |-data_pipeline.yml <br/>
    |-deploy_pipeline.yml <br/>
    |-env_pipeline.yml <br/>
    |-train_pipeline.yml <br/>
    |-requirements.txt <br/>

### !!! Hurray !!!!  
![Screenshot](Pipeline.png) <br/>