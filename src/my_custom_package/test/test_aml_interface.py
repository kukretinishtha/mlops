"""
This file is for unit testing the module
my_custom_package.utils.aml_interface

Just as with other similar files, the aim is to test
the correct Azure SDK classes are instantiated and
methods are called, rather than testing the functionality
of the external classes themselves.
"""
from unittest import TestCase
from unittest.mock import Mock, patch

from azureml.exceptions import ComputeTargetException

from my_custom_package.utils.aml_interface import AMLInterface

test_module = 'my_custom_package.utils.aml_interface'

class TestAMLInterface(TestCase):
    @patch(f'{test_module}.ServicePrincipalAuthentication')
    @patch(f'{test_module}.Workspace')
    def setUp(self, mock_Workspace, mock_ServicePrincipalAuthentication):
        mock_Workspace.return_value = 'test_workspace'
        spn_credentials = {
            'tenant_id': 'test_tenant_id',
            'service_principal_id': 'test_spn_id',
            'service_principal_password': 'test_spn_password',
        }
        self.aml_interface = AMLInterface(
            spn_credentials=spn_credentials,
            subscription_id='test_subscription_id',
            workspace_name='test_workspace_name',
            resource_group='test_resource_group'
        )
    
    @patch(f'{test_module}.Datastore')
    def test_register_datastore(self, mock_datastore):
        self.aml_interface.register_datastore(
            'test_datastore_name',
            'test_blob_container',
            'test_storage_acct_name',
            'test_storage_acct_key'
        )
        mock_datastore.register_azure_blob_container.assert_called_once_with(
            workspace='test_workspace',
            datastore_name='test_datastore_name', 
            container_name='test_blob_container', 
            account_name='test_storage_acct_name',
            account_key='test_storage_acct_key'
        )
    
    def register_aml_environment(self):
        mock_environment = Mock()
        
        self.aml_interface.register_aml_environment(mock_environment)

        mock_environment.register.assert_called_once_with('test_workspace')

    @patch(f'{test_module}.AmlCompute')
    @patch(f'{test_module}.ComputeTarget')
    def test_get_compute_target(self, mock_ComputeTarget, mock_AmlCompute):
        mock_ComputeTarget.side_effect = [
            'test_compute_target',
            ComputeTargetException("Compute Target Not Found")
        ]
    
        # First call to mock_compute_target returns 'test_compute_target'
        output_1 = self.aml_interface.get_compute_target(
            'test_compute_name',
            'STANDARD_D2_V2'
        )
        self.assertEqual(output_1, 'test_compute_target')
        mock_ComputeTarget.create.assert_not_called()

        mock_compute = Mock()
        # Compute target exists, create not called
        mock_ComputeTarget.create.return_value = mock_compute

        # Second call to mock_compute_target raises ComputeTargetException
        # Suggesting the compute target needs to be created
        output_2 = self.aml_interface.get_compute_target(
            'test_compute_name',
            'STANDARD_D2_V2'
        )

        self.assertEqual(output_2, mock_compute)
        mock_AmlCompute.provisioning_configuration.assert_called_once_with(
            vm_size='STANDARD_D2_V2',
            min_nodes=1,
            max_nodes=2
        )
        mock_ComputeTarget.create.assert_called_once()
        mock_compute.wait_for_completion.assert_called_once()
