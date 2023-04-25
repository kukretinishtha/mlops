"""
This file is for unit testing the module
my_custom_package.utils.blob_storage_interface

Just as with other similar files, the aim is to test
the correct Azure SDK classes are instantiated and
methods are called, rather than testing the functionality
of the external classes themselves.
"""
from unittest import TestCase
from unittest.mock import Mock, patch

import pandas as pd
from azure.core.exceptions import ResourceExistsError

from my_custom_package.utils.blob_storage_interface import BlobStorageInterface


test_module = 'my_custom_package.utils.blob_storage_interface'


class TestBlobStorageInterface(TestCase):
    @patch(f'{test_module}.BlobServiceClient')
    def setUp(self, mock_BlobServiceClient):
        self.blob_service_client_obj = Mock()
        mock_BlobServiceClient.from_connection_string.return_value = (
            self.blob_service_client_obj
        )

        self.blob_storage_interface = BlobStorageInterface(
            'test_storage_acct_name',
            'test_storage_acct_key'
        )
        mock_BlobServiceClient.from_connection_string.assert_called_once_with(
            'DefaultEndpointsProtocol=https;'
            + 'AccountName=test_storage_acct_name;'
            + 'AccountKey=test_storage_acct_key;'
            + 'EndpointSuffix=core.windows.net'
        )
    
    def test_create_container(self):
        self.blob_service_client_obj.create_container.side_effect = [
            None,
            ResourceExistsError
        ]
        self.blob_storage_interface.create_container('test_container_name')

        self.blob_service_client_obj.create_container.assert_called_with(
            'test_container_name'
        )

        # Upon second call to BlobStorageInterface.create_container,
        # ResourceExistsError is raised from
        # BlobStorageInterface.blob_service_client.create_container
        # Second call checks that no error is raised from
        # BlobStorageInterface.create_container
        self.blob_storage_interface.create_container('test_container_name')
    
    def test_upload_df_to_blob(self):
        mock_blob_client = Mock()
        mock_blob_client.upload_blob.side_effect = [
            None,
            ResourceExistsError,
            None
        ]
        self.blob_service_client_obj.get_blob_client.return_value = (
            mock_blob_client)
        
        test_df = pd.DataFrame([{'a': 1, 'b': 2}, {'a': 3, 'b': 4}])
        
        self.blob_storage_interface.upload_df_to_blob(
            test_df, 'test_container_name', 'test_remote_path'
        )

        self.blob_service_client_obj.get_blob_client.assert_called_with(
            container='test_container_name',
            blob='test_remote_path'
        )
        mock_blob_client.upload_blob.assert_called()
        args, _ = mock_blob_client.upload_blob.call_args_list[0]
        upload_arg = args[0]
        # The file uploaded is uploaded as bytes
        self.assertIsInstance(upload_arg, bytes)

        # First time upload_df_to_blob is called, there is no
        # ResourceExistsError so the blob is not deleted
        mock_blob_client.delete_blob.assert_not_called()

        # 2nd call to upload_df_to_blob
        self.blob_storage_interface.upload_df_to_blob(
            test_df, 'test_container_name', 'test_remote_path'
        )
        # Second time upload_df_to_blob is called, there is a
        # ResourceExistsError raised so the blob is deleted first
        mock_blob_client.delete_blob.assert_called_once()
    
    def test_download_blob_to_df(self):
        mock_blob_client = Mock()
        mock_stream = Mock()
        test_csv_str = "a,b\n1,2\n3,4"
        self.blob_service_client_obj.get_blob_client.return_value = (
            mock_blob_client)
        mock_blob_client.download_blob.return_value = mock_stream
        mock_stream.content_as_text.return_value = test_csv_str
        
        
        output_df = self.blob_storage_interface.download_blob_to_df(
            'test_container_name', 'test_remote_path'
        )

        self.assertIsInstance(output_df, pd.DataFrame)
        self.assertIn('a', output_df.columns)
        self.assertEqual(output_df.loc[1, 'b'], 4)

        self.blob_service_client_obj.get_blob_client.assert_called_once_with(
            container='test_container_name',
            blob='test_remote_path'
        )
        mock_blob_client.download_blob.assert_called_once()
        mock_stream.content_as_text.assert_called_once()
