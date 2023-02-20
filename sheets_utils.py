from gmail_credentials import get_credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

import os

load_dotenv()
AUTO_BUDGET_SPREADSHEET_ID = os.getenv('AUTO_BUDGET_SPREADSHEET_ID')


def get_sheets_service():
    '''
    Gets the Google Sheets service.
    '''
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    return service

def insert_data_into_sheet(service, range_name, values):
    '''
    Inserts data into a Google Sheet.
    Parameters:
        service: The Google Sheets service
        range_name: The range of cells to insert data into
        values: The values to insert into the cells
    '''
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=AUTO_BUDGET_SPREADSHEET_ID, range=range_name,
        valueInputOption='USER_ENTERED', body=body).execute()
    return result
