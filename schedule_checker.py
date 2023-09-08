from __future__ import print_function

import os.path
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from csv import writer
import random

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
schedule_spreadsheet_range = 'SCHEDULE!A1:K28' #Define a range of rows. "automation_test_2" is a sheet name here.
schedule_spreadsheet_id = open('schedule_id.txt', 'r').read()
values = []


def fetch_schedule(): #fetches all the remote data and builds workshop_list."
    creds = None
    if os.path.exists('token.json'): #this file provides credentials. if it's toast, just delete it and re-run
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=schedule_spreadsheet_id,
                                    range=schedule_spreadsheet_range).execute()
        values = result.get('values', [])
        if not values:
            print('No data found.')
            return
        
        #here's what you change in the checker.
        get_workshops(values)
        # for row in values:
        #     get_workshops(row)
    except HttpError as err:
        print(err)

#read in each row.

def get_workshops(values):
    for row in values:
        print(row)

fetch_schedule()
# get_workshops(values)

    # if row[3] != '':
    #     _teacher = row[3] #stage name
    # else:
    #     _teacher = row[2] #if no stage name, use given name
    # if row[17] != '': #workshop 1
    #     _title = row[17]
    #     _prop = str(row[19]).lower()
    #     _difficulty = get_workshop_difficulty(row[20])
    #     _workshop = Workshop(_teacher, _title, _prop, _difficulty)
    #     workshop_list.append(_workshop)
    # if row[21] != "": #workshop 2
    #     _title = row[21]
    #     _prop = str(row[23]).lower()
    #     _difficulty = get_workshop_difficulty(row[24])
    #     _workshop = Workshop(_teacher, _title, _prop, _difficulty)
    #     workshop_list.append(_workshop)
    # if row[25] != "":#workshop 3
    #     _title = row[25]
    #     _prop = str(row[27]).lower()
    #     _difficulty = get_workshop_difficulty(row[28])
    #     _workshop = Workshop(_teacher, _title, _prop, _difficulty)
    #     workshop_list.append(_workshop)
    # if row[29] != "": #workshop 4
    #     _title = row[29]
    #     _prop = str(row[31]).lower()
    #     _difficulty = get_workshop_difficulty(row[32])
    #     _workshop = Workshop(_teacher, _title, _prop, _difficulty)
    #     workshop_list.append(_workshop)

