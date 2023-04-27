from unittest import TestCase
from unittest.mock import patch, Mock

from azureml.core import ScriptRunConfig

from my_custom_package.deploy_aml_model import (
    get_inference_config, deploy_service, update_service)


@patch('my_custom_package.deploy_aml_model.InferenceConfig')
@patch('my_custom_package.deploy_aml_model.Environment')
def test_get_inference_config(mock_environment, mock_config):
    # We are not testing Azure ML SDK functionality in a unit test
    # Rather that the correct calls to the correct objects are made
    # using mock objects
    mock_aml_interface = Mock()
    get_inference_config(mock_aml_interface)

    mock_environment.get.assert_called_once()
    mock_config.assert_called_once()


@patch('my_custom_package.deploy_aml_model.Model')
@patch('my_custom_package.deploy_aml_model.AciWebservice')
@patch('my_custom_package.deploy_aml_model.get_inference_config')
def test_deploy_service(mock_get_inference_config, mock_AciWebservice,
                        mock_Model):
    mock_aml_interface = Mock()
    mock_service = Mock()
    mock_service.scoring_uri = 'https://foo.bar/'
    mock_Model.deploy.return_value = mock_service
    
    deploy_service(mock_aml_interface)
    # mock_get_inference_config is tested independently above
    mock_get_inference_config.assert_called_once()

    mock_AciWebservice.deploy_configuration.assert_called_once_with(
        cpu_cores=1,
        memory_gb=1
    )
    mock_service.wait_for_deployment.assert_called_once()


@patch('my_custom_package.deploy_aml_model.Webservice')
@patch('my_custom_package.deploy_aml_model.get_inference_config')
def test_update_service(mock_get_inference_config, mock_Webservice):
    mock_aml_interface = Mock()
    mock_get_inference_config.return_value = 'test_inference_config'
    mock_aml_interface.workspace.models.get.return_value = 'test_model_name'
    mock_service = Mock()
    mock_Webservice.return_value = mock_service
    
    update_service(mock_aml_interface)
    # mock_get_inference_config is tested independently above
    mock_get_inference_config.assert_called_once()
    mock_service.update.assert_called_once_with(
        models=['test_model_name'],
        inference_config='test_inference_config'
    )
