from unittest import TestCase

import pandas as pd

from my_custom_package.utils.transform_data import remove_collinear_cols


class TestTransformData(TestCase):
    def test_remove_collinear_cols(self):
        test_data_column_names = [
            'A', 'B', 'C', 'D', 'E',
            'F', 'G', 'H', 'I', 'J'
        ]
        test_X_data = pd.DataFrame([
            [
                -0.25, -0.90, 0.11, -0.12, -0.04,
                0.21, -0.41, -0.69, -0.13, -0.06
            ],
            [
                0.79, 0.13, -0.1, 0.87, -2.2,
                0.4,1.38, -0.78, -1.98, 0.5
            ]
        ], columns=test_data_column_names)
        
        self.assertIn('D', test_X_data.columns)
        self.assertIn('I', test_X_data.columns)

        X_data_transformed = remove_collinear_cols(test_X_data)

        self.assertIsInstance(X_data_transformed, pd.DataFrame)
        self.assertNotIn('D', X_data_transformed.columns)
        self.assertNotIn('I', X_data_transformed.columns)
        self.assertIn('A', X_data_transformed.columns)
        self.assertIn('E', X_data_transformed.columns)
        self.assertIn('J', X_data_transformed.columns)
        self.assertEqual(X_data_transformed.loc[0, 'C'], 0.11)
        self.assertEqual(X_data_transformed.loc[1, 'E'], -2.2)
