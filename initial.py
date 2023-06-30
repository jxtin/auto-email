import os
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import datetime
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64


# Define the scopes you want to request access to
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


def load_info():
    if input("Resume from json? Y/n") != "n":
        # Load the json file
        with open("info.json", "r") as f:
            vacation_info = json.load(f)
        vacation_start = (
            datetime.datetime.strptime(vacation_info["vacation_start"], "%Y-%m-%d")
            if vacation_info["vacation_start"] != ""
            else datetime.datetime.now()
        )
        last_checked = (
            datetime.datetime.strptime(vacation_info["last_checked"], "%Y-%m-%d")
            if vacation_info["last_checked"] != ""
            else None
        )
        return vacation_start, last_checked


def authenticate():
    creds = None
    # The file path to the credentials.json you downloaded from the Developer Console
    creds_path = "credentials.json"

    # Check if there are already valid credentials
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


creds = authenticate()
service = build("gmail", "v1", credentials=creds)


def get_all_thread_ids(service):
    # Call the Gmail API to retrieve all threads
    results = service.users().threads().list(userId="me").execute()
    threads = results.get("threads", [])

    # Extract the thread IDs
    thread_ids = [thread["id"] for thread in threads]

    return thread_ids


def last_thread_interaction(service, thread_id):
    thread = service.users().threads().get(userId="me", id=thread_id).execute()
    last_message = thread["messages"][-1]
    date = last_message["internalDate"]
    date = datetime.datetime.fromtimestamp(int(date) / 1000)

    headers = last_message["payload"]["headers"]
    try:
        sender = (
            [header["value"] for header in headers if header["name"] == "From"][0]
            .split("<")[1]
            .split(">")[0]
        )
    except IndexError:
        print(thread_id)
        return None, None, None
    body = last_message["snippet"]
    return date, sender, body


def check_handled(thread_ids, service, vacation_start):
    me = service.users().getProfile(userId="me").execute()["emailAddress"]

    for thread_id in thread_ids:
        date, sender, body = last_thread_interaction(service, thread_id)
        if sender is None:
            print(f"Thread {thread_id} has no sender.")
            continue
        vacation_start = (
            datetime.datetime.strptime(vacation_start, "%Y/%m/%d")
            if isinstance(vacation_start, str)
            else vacation_start
        )
        if date > vacation_start:
            if sender == me:
                print(f"Thread {thread_id} has been handled.")
            else:
                print(f"Thread {thread_id} needs to be handled.")
                reply_to_thread(service, thread_id)
        else:
            print(f"Thread {thread_id} is before the vacation start date.")


def get_emails_after_timestamp(service, timestamp):
    # Call the Gmail API to retrieve emails after the specified timestamp
    try:
        timestamp = int(timestamp)
    except ValueError:
        print("Assuming timestamp is in datetime format(2014/02/01)")
    results = (
        service.users().messages().list(userId="me", q=f"after:{(timestamp)}").execute()
    )

    emails = results.get("messages", [])

    return emails


def reply_to_thread(service, thread_id):
    # Get the thread
    thread = service.users().threads().get(userId="me", id=thread_id).execute()

    # Get the ID of the last message in the thread
    last_message_id = thread["messages"][-1]["id"]
    reply_text = "Thank you for your email. I am currently on vacation and will not be able to respond to your email until I return."

    # Create the reply message
    reply_message = MIMEText(reply_text)
    reply_message["to"] = thread["messages"][0]["payload"]["headers"][0]["value"]
    reply_message["reply-to"] = thread["messages"][0]["payload"]["headers"][1]["value"]
    reply_message[
        "subject"
    ] = f"Vacation Reply: {thread['messages'][0]['payload']['headers'][3]['value']}"
    reply_message["In-Reply-To"] = last_message_id
    reply_message["References"] = last_message_id

    # Encode the message as base64 URL-safe string
    raw_message = {"raw": base64.urlsafe_b64encode(reply_message.as_bytes()).decode()}
    target = thread["messages"][0]["payload"]["headers"][0]["value"]
    print(f"Replying to {target}...")

    # Send the reply message
    service.users().messages().send(userId="", body=raw_message).execute()

    print("Reply sent successfully!")


if __name__ == "__main__":
    vacation_start, last_checked = load_info()
    if last_checked is None:
        # get all messages on or after the vacation start date
        start = vacation_start.strftime("%Y/%m/%d")
    else:
        start = last_checked.timestamp()
    emails = get_emails_after_timestamp(service, start)

    thread_ids = [email["threadId"] for email in emails]

    vacation_start_date = (
        start if type(start) == str else datetime.datetime.fromtimestamp(start)
    )
    thread_ids = list(set(thread_ids))

    check_handled(thread_ids, service, vacation_start_date)
