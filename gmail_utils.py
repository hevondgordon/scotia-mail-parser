from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from gmail_credentials import get_credentials


def search_for_email_based_on_sender(service, user_id, sender, get_emails_after, get_emails_before):
    '''
    Search for emails based on sender and date range.
    Parameters:
        service: The Gmail service
        user_id: The user's email address. The special value 'me'
        can be used to indicate the authenticated user.
        sender: The sender of the email, e.g. 'alerts@scotiabank.com'
        get_emails_after: The date to start searching for emails, e.g. '2020-01-01'
        get_emails_before: The date to stop searching for emails, e.g. '2020-01-20'
    '''
    print('params:', user_id, sender, get_emails_after, get_emails_before)
    try:
        query = f'from: {sender} after:{get_emails_after} before:{get_emails_before}'
        response = service.users().messages().list(userId=user_id, q=query).execute()
        messages = []

        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(
                userId=user_id,
                q=query,
                pageToken=page_token).execute()
            messages.extend(response['messages'])
        return messages
    except HttpError as error:
        print(f'An error occurred: {error}')


def get_gmail_service():
    '''
    Gets the Gmail service.
    '''
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    return service
