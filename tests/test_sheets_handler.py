import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
from googleapiclient.errors import HttpError

from src.services.sheets_handler import GoogleSheetsHandler


class TestGoogleSheetsHandler(unittest.TestCase):
    @patch("src.services.sheets_handler.build")
    @patch("src.services.sheets_handler.Credentials")
    @patch("src.services.sheets_handler.os.path.exists")
    def setUp(self, mock_exists, mock_credentials, mock_build):
        mock_exists.return_value = False
        self.mock_creds = MagicMock()
        mock_credentials.from_authorized_user_file.return_value = self.mock_creds
        self.mock_service = MagicMock()
        mock_build.return_value = self.mock_service

        self.handler = GoogleSheetsHandler("dummy_credentials_path")

    @patch("src.services.sheets_handler.build")
    @patch("src.services.sheets_handler.Credentials")
    @patch("src.services.sheets_handler.os.path.exists")
    def test_authentication(self, mock_exists, mock_credentials, mock_build):
        mock_exists.return_value = False
        mock_credentials.from_authorized_user_file.return_value = self.mock_creds
        mock_build.return_value = self.mock_service

        handler = GoogleSheetsHandler("dummy_credentials_path")
        self.assertIsNotNone(handler.service)

    def test_validate_sheet_access_success(self):
        self.mock_service.spreadsheets().get().execute.return_value = {}
        result = self.handler.validate_sheet_access("dummy_spreadsheet_id")
        self.assertTrue(result)

    def test_validate_sheet_access_permission_denied(self):
        error = HttpError(resp=MagicMock(status=403), content=b"")
        self.mock_service.spreadsheets().get().execute.side_effect = error

        with self.assertRaises(Exception) as context:
            self.handler.validate_sheet_access("dummy_spreadsheet_id")
        self.assertIn(
            "You don't have permission to access this spreadsheet",
            str(context.exception),
        )

    def test_validate_sheet_access_not_found(self):
        error = HttpError(resp=MagicMock(status=404), content=b"")
        self.mock_service.spreadsheets().get().execute.side_effect = error

        with self.assertRaises(Exception) as context:
            self.handler.validate_sheet_access("dummy_spreadsheet_id")
        self.assertIn(
            "Spreadsheet not found. Please check the URL", str(context.exception)
        )

    def test_get_sheet_data_success(self):
        self.mock_service.spreadsheets().values().get().execute.return_value = {
            "values": [["header1", "header2"], ["value1", "value2"]]
        }
        df = self.handler.get_sheet_data("dummy_spreadsheet_id")
        self.assertEqual(df.shape, (1, 2))
        self.assertEqual(list(df.columns), ["header1", "header2"])

    def test_get_sheet_data_empty(self):
        self.mock_service.spreadsheets().values().get().execute.return_value = {
            "values": []
        }
        df = self.handler.get_sheet_data("dummy_spreadsheet_id")
        self.assertTrue(df.empty)

    def test_update_sheet_data_success(self):
        data = pd.DataFrame({"header1": ["value1"], "header2": ["value2"]})
        self.mock_service.spreadsheets().values().update().execute.return_value = {}

        result = self.handler.update_sheet_data("dummy_spreadsheet_id", "A1:Z1", data)
        self.assertTrue(result)

    def test_update_sheet_data_failure(self):
        data = pd.DataFrame({"header1": ["value1"], "header2": ["value2"]})
        error = HttpError(resp=MagicMock(status=400), content=b"")
        self.mock_service.spreadsheets().values().update().execute.side_effect = error

        with self.assertRaises(Exception) as context:
            self.handler.update_sheet_data("dummy_spreadsheet_id", "A1:Z1", data)
        self.assertIn("Error updating sheet", str(context.exception))


if __name__ == "__main__":
    unittest.main()
