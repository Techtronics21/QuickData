import os.path

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleSheetsHandler:
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.token_path = os.path.join(os.path.dirname(credentials_path), "token.json")
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self._authenticate()

    def _authenticate(self):
        try:
            self.service = self._initialize_service()
        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}")

    def _initialize_service(self):
        try:
            creds = None
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(
                    self.token_path, self.scopes
                )

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.scopes
                    )
                    creds = flow.run_local_server(port=0)

                # Save the credentials for the next run
                with open(self.token_path, "w") as token:
                    token.write(creds.to_json())

            return build("sheets", "v4", credentials=creds)
        except Exception as e:
            raise Exception(f"Service initialization failed: {str(e)}")

    def validate_sheet_access(self, spreadsheet_id: str) -> bool:
        try:
            self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            return True
        except HttpError as e:
            if e.resp.status == 403:
                raise Exception("You don't have permission to access this spreadsheet")
            elif e.resp.status == 404:
                raise Exception("Spreadsheet not found. Please check the URL")
            else:
                raise Exception(f"Error accessing spreadsheet: {str(e)}")

    def get_sheet_data(self, spreadsheet_id: str) -> pd.DataFrame:
        try:
            self.validate_sheet_access(spreadsheet_id)
            sheet = self.service.spreadsheets()
            result = (
                sheet.values()
                .get(
                    spreadsheetId=spreadsheet_id,
                    range="A1:ZZ",  # Default range to get all data
                )
                .execute()
            )

            values = result.get("values", [])
            if not values:
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(values[1:], columns=values[0])
            return df

        except HttpError as e:
            raise Exception(f"Error fetching sheet data: {str(e)}")

    def update_sheet_data(
        self, spreadsheet_id: str, range_name: str, data: pd.DataFrame
    ) -> bool:
        try:
            values = [data.columns.values.tolist()] + data.values.tolist()
            body = {"values": values}

            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body,
            ).execute()

            return True

        except HttpError as e:
            raise Exception(f"Error updating sheet: {str(e)}")

    def create_new_sheet(self, title: str) -> str:
        try:
            spreadsheet = {
                'properties': {
                    'title': title
                },
                'sheets': [{
                    'properties': {
                        'title': 'Results'
                    }
                }]
            }
            spreadsheet = self.service.spreadsheets().create(body=spreadsheet).execute()
            return spreadsheet['spreadsheetId']
        except Exception as e:
            raise Exception(f"Error creating new sheet: {str(e)}")

    def export_results(self, data: pd.DataFrame, spreadsheet_id: str = None, sheet_name: str = "Results") -> str:
        try:
            if not spreadsheet_id:
                spreadsheet_id = self.create_new_sheet(f"AI Data Agent Results - {pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Ensure the sheet exists by getting all sheets
            sheet_metadata = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', '')
            sheet_exists = any(sheet['properties']['title'] == sheet_name for sheet in sheets)
            
            if not sheet_exists:
                # Add new sheet if it doesn't exist
                request = {
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }
                body = {'requests': [request]}
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body=body
                ).execute()
            
            # Now update the data
            range_name = f"'{sheet_name}'!A1"  # Use single range reference
            self.update_sheet_data(spreadsheet_id, range_name, data)
            
            return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            
        except Exception as e:
            raise Exception(f"Error exporting results: {str(e)}")
