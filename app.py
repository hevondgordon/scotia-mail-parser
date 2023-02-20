from flask import Flask

from gmail import execute

app = Flask(__name__)

@app.route("/v1/process_gmail_messages")
def process_gmail_messages():
    '''
    Processes Gmail messages.'''
    try:
        execute()
        return "Success"
        # handle http exceptions
    except Exception as exception:
        return str(exception)
