import json
import os
from unittest import TestCase
from unittest.mock import Mock, patch

import pandas as pd
from sklearn.linear_model import LogisticRegression

from my_custom_package.score import init, run
from my_custom_package.utils.transform_data import remove_collinear_cols

__here__ = os.path.dirname(__file__)
test_data_dir = os.path.join(__here__, 'test_data')

class TestInit(TestCase):
    @patch('my_custom_package.score.Model')
    def test_init(self, mock_model):
        mock_model.get_model_path.return_value = os.path.join(
            test_data_dir, 'test_model.pkl'
        )

        init()
        mock_model.get_model_path.assert_called_once()
        
        # model has now been initialised
        from my_custom_package.score import model
        self.assertIsInstance(model, LogisticRegression)


class TestRun(TestCase):
    def setUp(self):
        X_data = pd.read_csv(os.path.join(test_data_dir, 'test_X_valid.csv'))
        X_data = remove_collinear_cols(X_data)
        self.test_data = json.dumps({'data': X_data.values.tolist()})

    def test_run(self):
        result = run(self.test_data)
        self.assertIsInstance(result, list)
        for y_value in result:
            self.assertIn(y_value, [0, 1])
    
    def test_run_error(self):
        result = run('{"data": [0, 1, 0]}')
        self.assertIn("Expected 2D array, got 1D array instead", result)
