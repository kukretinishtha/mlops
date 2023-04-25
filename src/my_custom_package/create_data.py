import os

import pandas as pd
from sklearn.datasets import make_classification

from my_custom_package.utils.blob_storage_interface import BlobStorageInterface
from my_custom_package.utils.const import (
    TRAINING_CONTAINER, SCORING_CONTAINER, TRAINING_DATASTORE
)
from my_custom_package.utils.aml_interface import AMLInterface


class CreateClassificationData():
    def __init__(self):
        x_arr, y_arr = make_classification(
            n_samples=5000,
            n_features=10,
            n_classes=2,
            random_state=1
        )
        col_names = ['A', 'B', 'C', 'D', 'E',
                     'F', 'G', 'H', 'I', 'J']
        x_df = pd.DataFrame(x_arr, columns=col_names)
        y_df = pd.DataFrame({'Target': y_arr})
        # Training set n=3500
        self.x_train = x_df.iloc[:3500]
        self.y_train = y_df.iloc[:3500]

        # Testing set n=750
        self.x_test = x_df.iloc[3500:4250]
        self.y_test = y_df.iloc[3500:4250]

        # Validation set n=750
        self.x_valid = x_df.iloc[4250:]
        self.y_valid = y_df.iloc[4250:]

    def upload_training_data(self, blob_storage_interface):
        blob_storage_interface.upload_df_to_blob(
            self.x_train,
            TRAINING_CONTAINER,
            'train/X_train.csv'
        )
        blob_storage_interface.upload_df_to_blob(
            self.y_train,
            TRAINING_CONTAINER,
            'train/y_train.csv'
        )

    def upload_evaluation_data(self, blob_storage_interface):
        # Data to be used during model evaluation
        # So stored in the training container
        blob_storage_interface.upload_df_to_blob(
            self.x_test,
            TRAINING_CONTAINER,
            'test/X_test.csv'
        )
        blob_storage_interface.upload_df_to_blob(
            self.y_test,
            TRAINING_CONTAINER,
            'test/y_test.csv'
        )

    def upload_validation_data(self, blob_storage_interface):
        # Data to be used during model validation
        blob_storage_interface.upload_df_to_blob(
            self.x_valid,
            SCORING_CONTAINER,
            'X_valid.csv'
        )
        blob_storage_interface.upload_df_to_blob(
            self.y_valid,
            SCORING_CONTAINER,
            'y_valid.csv'
        )

    def upload_data(self, blob_storage_interface):
        self.upload_training_data(blob_storage_interface)
        self.upload_evaluation_data(blob_storage_interface)
        self.upload_validation_data(blob_storage_interface)


def main():
    # Retrieve vars from env
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
    # Instantiate Blob Storage Interface
    blob_storage_interface = BlobStorageInterface(
        storage_acct_name, storage_acct_key
    )

    # Create and Upload data to Blob Store
    data_creator = CreateClassificationData()
    data_creator.upload_data(blob_storage_interface)

    # Register Blob Store to AML
    aml_interface = AMLInterface(
        spn_credentials, subscription_id, workspace_name, resource_group
    )
    aml_interface.register_datastore(
        TRAINING_CONTAINER, TRAINING_DATASTORE,
        storage_acct_name, storage_acct_key
    )

if __name__ == '__main__':
    main()
