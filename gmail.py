
import base64
import re
import datetime
import json

from bs4 import BeautifulSoup
from googleapiclient.errors import HttpError
from gmail_utils import search_for_email_based_on_sender, get_gmail_service
from sheets_utils import insert_data_into_sheet, get_sheets_service

def track_config(row_to_start_inserting_at):
    '''
    This function will track the last execution date and the row to start inserting
    values in the spreadsheet at
    '''

    config = {
        'last_execution_date':datetime.datetime.now().strftime('%Y-%m-%d'),
        'row_to_start_inserting_at':row_to_start_inserting_at
    }
    with open('config.json', 'w', encoding='utf-8') as config_file:
        json.dump(config, config_file)

def get_config():
    '''
    This function will get the config file
    '''
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
        return config

def process_gmail_messages(config, messages, gmail_service):
    '''
    This function will process the gmail messages and insert the data into the spreadsheet.
    Parameters:
        config: The config file as a dictionary
        messages: The messages to process
        gmail_service: The Gmail service
    '''
    row_to_start_inserting_at = config['row_to_start_inserting_at']
    for _message in messages:
        row_to_start_inserting_at += 1
        message = gmail_service.users().messages().get(userId='me', id=_message['id']).execute()
        if  message['payload']['body'].get('data', None):
            # get data from email
            get_decoded_message = base64.urlsafe_b64decode(
                message['payload']['body']['data'].encode('ASCII'))
            soup_message_body = BeautifulSoup(get_decoded_message.decode('utf-8'), 'html.parser')

            transaction_description = soup_message_body.find_all('p')[0].get_text()
            compiled_transaction_amount = re.compile(r'\$\d{1,3}(,\d{3})*(\.\d{2})?').search(
                transaction_description)
            if compiled_transaction_amount:
                transaction_amount = compiled_transaction_amount.group(0)

                print(transaction_amount, transaction_description)
                insert_data_into_sheet(
                    get_sheets_service(),
                    f'AUTO BUDGET!A{row_to_start_inserting_at}:B{row_to_start_inserting_at}',
                    [[transaction_amount, transaction_description]]
                )
    return row_to_start_inserting_at

def main():
    '''Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    '''
    try:
        config = get_config()
        gmail_service = get_gmail_service()

        messages = search_for_email_based_on_sender(
            gmail_service,
            'me',
            'alerts@scotiabank.com',
            config['last_execution_date'],
            datetime.datetime.now().strftime('%Y-%m-%d')
        )
        new_row_to_start_inserting_at = process_gmail_messages(config, messages, gmail_service)
        track_config(new_row_to_start_inserting_at)

    except HttpError as error:
    #    TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()
