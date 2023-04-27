from unittest import TestCase
from unittest.mock import Mock

import pandas as pd

from my_custom_package.create_data import CreateClassificationData


class TestCreateClassificationData(TestCase):
    def test_init(self):
        # Run init
        data_creator_obj = CreateClassificationData()
        self.assertIsInstance(data_creator_obj.x_train, pd.DataFrame)
        self.assertIsInstance(data_creator_obj.x_test, pd.DataFrame)
        self.assertIsInstance(data_creator_obj.x_valid, pd.DataFrame)
        self.assertIsInstance(data_creator_obj.y_train, pd.DataFrame)
        self.assertIsInstance(data_creator_obj.y_test, pd.DataFrame)
        self.assertIsInstance(data_creator_obj.y_valid, pd.DataFrame)

        # Train data is 3500 rows
        # X data is 10 columns, y data is 1 column
        self.assertEqual(len(data_creator_obj.x_train), 3500)
        self.assertEqual(len(data_creator_obj.x_train.columns), 10)
        self.assertEqual(len(data_creator_obj.y_train), 3500)
        self.assertEqual(len(data_creator_obj.y_train.columns), 1)

        # Test data is 750 rows
        self.assertEqual(len(data_creator_obj.x_test), 750)
        self.assertEqual(len(data_creator_obj.x_test.columns), 10)
        self.assertEqual(len(data_creator_obj.y_test), 750)
        self.assertEqual(len(data_creator_obj.y_test.columns), 1)
        
        # Validation data is 750 rows
        self.assertEqual(len(data_creator_obj.x_valid), 750)
        self.assertEqual(len(data_creator_obj.x_valid.columns), 10)
        self.assertEqual(len(data_creator_obj.y_valid), 750)
        self.assertEqual(len(data_creator_obj.y_valid.columns), 1)
    
    def test_upload_training_data(self):
        mock_blob_storage_interface = Mock()
        data_creator_obj = CreateClassificationData()
        data_creator_obj.upload_training_data(mock_blob_storage_interface)
        self.assertTrue(
            mock_blob_storage_interface.upload_df_to_blob.call_count,
            2
        )

    def test_upload_evaluation_data(self):
        mock_blob_storage_interface = Mock()
        data_creator_obj = CreateClassificationData()
        data_creator_obj.upload_evaluation_data(mock_blob_storage_interface)
        self.assertTrue(
            mock_blob_storage_interface.upload_df_to_blob.call_count,
            2
        )
    
    def test_upload_validation_data(self):
        mock_blob_storage_interface = Mock()
        data_creator_obj = CreateClassificationData()
        data_creator_obj.upload_validation_data(mock_blob_storage_interface)
        self.assertTrue(
            mock_blob_storage_interface.upload_df_to_blob.call_count,
            2
        )
    
    def test_upload_data(self):
        mock_blob_storage_interface = Mock()
        data_creator_obj = CreateClassificationData()
        data_creator_obj.upload_data(mock_blob_storage_interface)
        self.assertTrue(
            mock_blob_storage_interface.upload_df_to_blob.call_count,
            6
        )
