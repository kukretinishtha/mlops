from unittest import TestCase
from unittest.mock import patch, Mock

from azureml.core import ScriptRunConfig

from my_custom_package.create_aml_experiment import submit_run


class TestSubmitRun(TestCase):
    @patch('my_custom_package.create_aml_experiment.Environment')
    @patch('my_custom_package.create_aml_experiment.Experiment')
    def test_submit_run(self, mock_experiment, mock_environment):
        # We are not testing Azure ML SDK functionality in a unit test
        # Rather that the correct calls are made
        mock_experiment_obj = Mock()
        mock_run = Mock()
        mock_experiment.return_value = mock_experiment_obj
        mock_experiment_obj.submit.return_value = mock_run
        mock_aml_interface = Mock()

        submit_run(mock_aml_interface)
        mock_experiment_obj.submit.assert_called_once()
        mock_environment.get.assert_called_once()
        mock_aml_interface.get_compute_target.assert_called_once()
        _, kwargs = mock_experiment_obj.submit.call_args_list[0]
        exp_config = kwargs['config']
        self.assertIsInstance(exp_config, ScriptRunConfig)
        self.assertEqual(exp_config.script, 'train.py')
        mock_run.wait_for_completion.assert_called_once_with(show_output=True)
        mock_run.get_metrics.assert_called_once()
