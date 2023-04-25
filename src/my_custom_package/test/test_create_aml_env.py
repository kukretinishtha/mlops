import os
import shutil

from azureml.core.conda_dependencies import CondaDependencies
from unittest import TestCase
from unittest.mock import patch, Mock

from my_custom_package.create_aml_env import (
    get_dist_dir, retrieve_whl_filepath, create_aml_environment)


__here__ = os.path.dirname(__file__)


class TestGetDistDir(TestCase):
    def test_get_dist_dir(self):
        dist_dir = get_dist_dir()
        self.assertIsInstance(dist_dir, str)
        self.assertTrue(dist_dir.endswith('dist'))


class TestRetrieveWhlFilepath(TestCase):
    def setUp(self):
        self.test_dist_dir = os.path.join(__here__, 'test_dist_dir')
        whl_filename = 'my_custom_package-0.1-py3.whl'
        self.whl_filepath = os.path.join(
            self.test_dist_dir,
            whl_filename
        )

    @patch('my_custom_package.create_aml_env.get_dist_dir')
    def test_retrieve_whl_filepath_fails_no_dist_dir(self, mock_get_dist_dir):
        mock_get_dist_dir.return_value = self.test_dist_dir
        if os.path.exists(self.test_dist_dir):
            shutil.rmtree(self.test_dist_dir)

        # Dist Directory not present
        with self.assertRaises(FileNotFoundError):
            retrieve_whl_filepath()
    
    @patch('my_custom_package.create_aml_env.get_dist_dir')
    def test_retrieve_whl_filepath_fails_no_file(self, mock_get_dist_dir):
        mock_get_dist_dir.return_value = self.test_dist_dir
        if os.path.exists(self.test_dist_dir):
            shutil.rmtree(self.test_dist_dir)
        os.makedirs(self.test_dist_dir)

        # Dist Directory present but no wheel file
        with self.assertRaises(FileNotFoundError):
            retrieve_whl_filepath()
    

    @patch('my_custom_package.create_aml_env.get_dist_dir')
    def test_retrieve_whl_filepath(self, mock_get_dist_dir):
        mock_get_dist_dir.return_value = self.test_dist_dir
        if not os.path.exists(self.test_dist_dir):
            os.makedirs(self.test_dist_dir)
        # Create empty file
        open(self.whl_filepath, 'w').close()
        
        filepath = retrieve_whl_filepath()
        self.assertIsInstance(filepath, str)
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('my_custom_package-0.1-py3.whl'))
    
    def tearDown(self):
        if os.path.exists(self.test_dist_dir):
            shutil.rmtree(self.test_dist_dir)


class TestCreateAMLEnvironment(TestCase):
    def setUp(self):
        self.test_dist_dir = os.path.join(__here__, 'test_dist_dir')
        os.makedirs(self.test_dist_dir)
        whl_filename = 'my_custom_package-0.1-py3.whl'
        self.whl_filepath = os.path.join(
            self.test_dist_dir,
            whl_filename
        )
        # Create empty file
        open(self.whl_filepath, 'w').close()

    @patch('my_custom_package.create_aml_env.retrieve_whl_filepath')
    @patch('my_custom_package.create_aml_env.Environment')
    def test_create_aml_environment(self, mock_env,
                                    mock_retrieve_whl_filepath):
        mock_retrieve_whl_filepath.return_value = self.whl_filepath
        # We are not testing Azure ML SDK functionality in a unit test
        # Rather that the correct calls are made so use mock objects
        mock_env_obj = Mock()
        mock_env.return_value = mock_env_obj
        # Some valid pip file for testing purposes
        mock_env.add_private_pip_wheel.return_value = 'requests'

        mock_env_obj.foo = 'bar'
        aml_interface = Mock()
        create_aml_environment(aml_interface)
        self.assertIsInstance(
            mock_env_obj.python.conda_dependencies,
            CondaDependencies
        )
        pkg_list = [
            pkg for pkg in
            mock_env_obj.python.conda_dependencies.pip_packages
        ]
        self.assertIn('numpy==1.18.2', pkg_list)
        self.assertIn('pandas==1.0.3', pkg_list)
        self.assertIn('scikit-learn==0.22.2.post1', pkg_list)
        self.assertIn('requests', pkg_list)
        self.assertTrue(mock_env_obj.docker.enabled)

    def tearDown(self):
        shutil.rmtree(self.test_dist_dir, ignore_errors=True)
