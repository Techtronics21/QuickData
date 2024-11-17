import unittest
from io import StringIO

import pandas as pd

from services.csv_handler import process_csv_data, read_csv


class TestCSVHandler(unittest.TestCase):
    def test_read_csv_valid_file(self):
        csv_data = "col1,col2\n1,2\n3,4"
        file_path = StringIO(csv_data)
        result = read_csv(file_path)
        expected = pd.DataFrame({"col1": [1, 3], "col2": [2, 4]})
        pd.testing.assert_frame_equal(result, expected)

    def test_read_csv_invalid_file(self):
        result = read_csv("invalid_path.csv")
        self.assertIsNone(result)

    def test_process_csv_data_with_missing_values(self):
        data = pd.DataFrame({"col1": [1, None, 3], "col2": [2, 4, None]})
        result = process_csv_data(data)
        expected = pd.DataFrame({"col1": [1], "col2": [2]})
        pd.testing.assert_frame_equal(result, expected)

    def test_process_csv_data_no_missing_values(self):
        data = pd.DataFrame({"col1": [1, 3], "col2": [2, 4]})
        result = process_csv_data(data)
        expected = data
        pd.testing.assert_frame_equal(result, expected)

    def test_process_csv_data_none_input(self):
        result = process_csv_data(None)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
