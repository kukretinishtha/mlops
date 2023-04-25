import json
import os

import numpy as np
import requests
from azureml.core.webservice import Webservice
from sklearn.metrics import f1_score

from my_custom_package.utils.aml_interface import AMLInterface
from my_custom_package.utils.blob_storage_interface import BlobStorageInterface
from my_custom_package.utils.const import (
    SCORING_CONTAINER, DEPLOYMENT_SERVICE_NAME)
from my_custom_package.utils.transform_data import remove_collinear_cols


def get_validation_data(storage_acct_name, storage_acct_key):
    blob_storage_interface = BlobStorageInterface(
        storage_acct_name,
        storage_acct_key
    )
    x_valid = blob_storage_interface.download_blob_to_df(
        container_name=SCORING_CONTAINER,
        remote_path='X_valid.csv'
    )
    y_valid = blob_storage_interface.download_blob_to_df(
        container_name=SCORING_CONTAINER,
        remote_path='y_valid.csv'
    )
    return x_valid, y_valid


def get_web_service_uri(aml_interface):
    service = Webservice(
        name=DEPLOYMENT_SERVICE_NAME,
        workspace=aml_interface.workspace
    )
    return service.scoring_uri


def make_predictions(x_df, scoring_uri):
    data = json.dumps({'data': x_df.values.tolist()})
    headers = {'Content-Type': 'application/json'}
    response = requests.post(scoring_uri, data=data, headers=headers)
    return np.array(response.json())


def score_predictions(y_valid, y_pred):
    model_validation_f1_score = round(f1_score(y_valid, y_pred), 3)
    print(f"F1 Score on Validation Data Set: {model_validation_f1_score}")


def main():
    storage_acct_name = os.environ['STORAGE_ACCT_NAME']
    storage_acct_key = os.environ['STORAGE_ACCT_KEY']
    workspace_name = os.environ['AML_WORKSPACE_NAME']
    resource_group = os.environ['RESOURCE_GROUP']
    subscription_id = os.environ['SUBSCRIPTION_ID']

    spn_credentials = {
        'tenant_id': os.environ['TENANT_ID'],
        'service_principal_id': os.environ['SPN_ID'],
        'service_principal_password': os.environ['SPN_PASSWORD'],
    }

    aml_interface = AMLInterface(
        spn_credentials, subscription_id, workspace_name, resource_group
    )
    x_valid, y_valid = get_validation_data(storage_acct_name, storage_acct_key)
    x_valid = remove_collinear_cols(x_valid)
    y_valid = y_valid['Target']
    aml_interface = AMLInterface(
        spn_credentials, subscription_id, workspace_name, resource_group
    )
    scoring_uri = get_web_service_uri(aml_interface)
    y_pred = make_predictions(x_valid, scoring_uri)
    score_predictions(y_valid, y_pred)


if __name__ == '__main__':
    main()
