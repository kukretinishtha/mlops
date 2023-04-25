import os
import shutil
from unittest import TestCase
from unittest.mock import Mock, patch

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression

from my_custom_package.train import (
    get_df_from_datastore_path, prepare_data, train_model,
    evaluate_model, save_model, register_model)


__here__ = os.path.dirname(__file__)
test_data_dir = os.path.join(__here__, 'test_data')


@patch('my_custom_package.train.Dataset')
def test_get_df_from_datastore_path(mock_dataset):
    mock_datastore = Mock()
    datastore_path = 'test_path'
    mock_dataset_obj = Mock()
    mock_dataset.Tabular.from_delimited_files.return_value = mock_dataset_obj
    test_df = pd.DataFrame([{'a': 1, 'b': 2}, {'a': 3, 'b': 4}])
    mock_dataset_obj.to_pandas_dataframe.return_value = test_df
    
    df = get_df_from_datastore_path(mock_datastore, datastore_path)
    mock_dataset.Tabular.from_delimited_files.assert_called_once_with(
        path=[(mock_datastore, datastore_path)]
    )
    mock_dataset_obj.to_pandas_dataframe.assert_called_once()
    assert df.equals(test_df)


class TestPrepareData(TestCase):
    @patch('my_custom_package.train.get_df_from_datastore_path')
    @patch('my_custom_package.train.Datastore')
    def test_get_df_from_datastore_path(self, mock_datastore,
                                        mock_get_df_from_datastore_path):
        # get_df_from_datastore_path tested above
        mock_get_df_from_datastore_path.side_effect = [
            pd.read_csv(os.path.join(test_data_dir, 'test_X_train.csv')),
            pd.read_csv(os.path.join(test_data_dir, 'test_y_train.csv')),
            pd.read_csv(os.path.join(test_data_dir, 'test_X_test.csv')),
            pd.read_csv(os.path.join(test_data_dir, 'test_y_test.csv')),
        ]
        X_train, y_train, X_test, y_test = prepare_data('test_workspace')

        self.assertIsInstance(X_train, pd.DataFrame)
        self.assertIsInstance(y_train, pd.Series)
        self.assertIsInstance(X_test, pd.DataFrame)
        self.assertIsInstance(y_test, pd.Series)

        self.assertIn('A', X_train.columns)
        self.assertIn('C', X_train.columns)
        self.assertIn('J', X_train.columns)
        self.assertIn('C', X_test.columns)
        self.assertNotIn('D', X_train.columns)
        self.assertNotIn('I', X_train.columns)
        self.assertNotIn('D', X_test.columns)
        self.assertNotIn('I', X_test.columns)

        self.assertEqual(len(X_train), len(y_train))
        self.assertEqual(len(X_test), len(y_test))


class TestTrainModel(TestCase):
    @patch('my_custom_package.train.get_df_from_datastore_path')
    @patch('my_custom_package.train.Datastore')
    def setUp(self, mock_datastore, mock_get_df_from_datastore_path):
        # prepare_data tested above
        mock_get_df_from_datastore_path.side_effect = [
            pd.read_csv(os.path.join(test_data_dir, 'test_X_train.csv')),
            pd.read_csv(os.path.join(test_data_dir, 'test_y_train.csv')),
            pd.read_csv(os.path.join(test_data_dir, 'test_X_test.csv')),
            pd.read_csv(os.path.join(test_data_dir, 'test_y_test.csv')),
        ]
        self.X_train, self.y_train, _, _ = prepare_data('test_workspace')
    
    def test_train_model(self):
        trained_model = train_model(self.X_train, self.y_train)
        self.assertIsInstance(trained_model, LogisticRegression)


class TestEvaluateModel(TestCase):
    @patch('my_custom_package.train.get_df_from_datastore_path')
    @patch('my_custom_package.train.Datastore')
    def setUp(self, mock_datastore, mock_get_df_from_datastore_path):
        # prepare_data tested above
        mock_get_df_from_datastore_path.side_effect = [
            pd.read_csv(os.path.join(test_data_dir, 'test_X_train.csv')),
            pd.read_csv(os.path.join(test_data_dir, 'test_y_train.csv')),
            pd.read_csv(os.path.join(test_data_dir, 'test_X_test.csv')),
            pd.read_csv(os.path.join(test_data_dir, 'test_y_test.csv')),
        ]
        _, _, self.X_test, self.y_test = prepare_data('test_workspace')
        self.classifier = joblib.load(
            os.path.join(test_data_dir, 'test_model.pkl')
        )
    
    def test_evaluate_model(self):
        mock_run = Mock()

        evaluate_model(self.classifier, self.X_test, self.y_test, mock_run)
        
        mock_run.log.assert_called_once()
        # First argument of first call
        self.assertEqual(mock_run.log.call_args[0][0], 'F1_Score')
        # Second argument of first call
        self.assertIsInstance(mock_run.log.call_args[0][1], float)


class TestSaveModel(TestCase):
    def setUp(self):
        self.classifier = joblib.load(
            os.path.join(test_data_dir, 'test_model.pkl')
        )
    
    @patch('my_custom_package.train.__here__', test_data_dir)
    def test_save_model(self):
        save_model(self.classifier)
        self.assertTrue(
            os.path.exists(
                os.path.join(test_data_dir, 'outputs')
            )
        )
        self.assertTrue(
            os.path.exists(
                os.path.join(test_data_dir, 'outputs', 'model.pkl')
            )
        )

    def tearDown(self):
        outputs_dir = os.path.join(test_data_dir, 'outputs')
        shutil.rmtree(outputs_dir, ignore_errors=True)


def test_register_model():
    mock_run = Mock()
    mock_azure_model_obj = Mock()
    mock_azure_model_obj.id = 'test_id'
    mock_run.register_model.return_value = mock_azure_model_obj

    register_model(mock_run, 'test_model_path')
    mock_run.upload_file.assert_called_once_with(
        'test_model_path', "outputs/model.pkl"
    )
    mock_run.register_model.assert_called_once()
    mock_run.log.assert_called_once_with('Model_ID', 'test_id')
