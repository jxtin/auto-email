# Vacation Auto Responder

This repository contains a vacation auto responder application that automatically replies to emails during your vacation period. It is a work-in-progress project developed for an internship recruitment assignment. (SERP Scraper already done, I just wanted to attempt this as well.)

## Assignment Description

The goal of the assignment is to build an application with the following functionalities:

- Checks for new emails in a given Gmail ID.
- Replies to emails that have no prior replies.
- Adds a label to the replied email and moves it to the label.
- Repeats tasks in random intervals of 45 to 120 seconds.
- Ensures no double replies are sent to any email at any point in time.

## Implementation

The main script, `initial.py`, handles the core functionality of the vacation auto responder. It uses the Google Gmail API to authenticate and interact with the user's Gmail account. The script performs the following tasks:

- Authenticates the user and obtains the necessary credentials.
- Loads the vacation start date and the last checked date from the `info.json` file.
- Retrieves all the thread IDs of the user's emails.
- Checks if each thread needs to be handled based on the last interaction date and the vacation start date.
- Sends a reply to threads that need to be handled.
- Saves the last checked date to `info.json`.
- Implements random intervals for repeating tasks (pending implementation).
- Applies labels to replied emails and moves them to the label (pending implementation).

## Features

### Implemented Features

- Set vacation start: The user can set the vacation start date.
- Check mails to be handled: The script checks for emails that need to be handled based on the vacation start date and the last interaction date.
- Incremental checks: The script only checks for emails received after the last checked date.

### Pending Features

- Run at intervals: The script will be modified to run at random intervals between 45 to 120 seconds.
- Iron out replies: The script will be improved to ensure correct and effective replies to emails.
- Apply labels: The script will apply labels to replied emails and move them to the respective label.

## Getting Started

To get started with the vacation auto responder application, follow these steps:

1. Clone the repository: `git clone https://github.com/jxtin/auto-email.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Set up the Gmail API and obtain the `credentials.json` file. Place it in the project directory.
4. Run the script: `python initial.py`

Please note that the application is a work in progress, and some features are yet to be implemented, such as running at random intervals, improving replies, and applying labels to emails.

## Requirements

The following dependencies are required to run the application:

- Python (>=3.6)
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib
