from __future__ import print_function

import os.path
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'       #Define a range of rows. "Class Data" is a sheet name.
APPLICATION_SPREADSHEET_ID = '1_m04l3E4JM0jBeSAfbJmmS6IWO_5NzJaU2j18a_CYh4'
APPLICATION_RANGE_NAME = 'Accepted!A2:E'
SCHEDULE_SPREADSHEET_ID = '1r-smbYFeQF-gTrP6_v3L3J63mRz2exwfdPcT7v3DiRc'

local_schedule = []
workshop_list = []

class Workshop:
    def __init__(self, teacher, title, prop, diff):
        self.teacher = teacher
        self.title = title
        self.prop = prop
        self.diff = diff

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,  #CREATE A DICT(?) OF THIS SHEET
                                    range=SAMPLE_RANGE_NAME).execute()      #RANGE OF ROWS 
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s' % (row[0], row[4]))
    except HttpError as err:
        print(err)

def get_workshop_difficulty(item):
    if 'SPECIFICALLY' in item:
        return 1
    if 'OK' in item:
        return 2
    if 'NOT' in item:
        return 3

def get_workshops(row):
    if row[3] != ''
        _teacher = row[3]
    else:
        _teacher = row[2]
    if row[16] != '': #if "first workshop title" isn't blank,
        _title = row[16] #grab the title
        _prop = row[18] #grab the prop
        _difficulty = get_workshop_difficulty(row[19]) #grab the difficulty
        _workshop = Workshop(_teacher, _title, _prop, _difficulty) #make a new workshop object
        workshop_list.append(_workshop) #stick it in the list!
    if row[20] != "": #repeat as desired below
        _title = row[20]
        _prop = row[22]
        _difficulty = get_workshop_difficulty(row[23])
        _workshop = Workshop(_teacher, _title, _prop, _difficulty)
        workshop_list.append(_workshop)
    if row[24] != "":
        _title = row[24]
        _prop = row[26]
        _difficulty = get_workshop_difficulty(row[27])
        _workshop = Workshop(_teacher, _title, _prop, _difficulty)
        workshop_list.append(_workshop)
    if row[28] != "":
        _title = row[28]
        _prop = row[30]
        _difficulty = get_workshop_difficulty(row[31])
        _workshop = Workshop(_teacher, _title, _prop, _difficulty)
        workshop_list.append(_workshop)

def schedule_a_class(class):
    

# # # WHAT TO DO?
# # READ IN THE WORKSHOPS (functions exist for this now)

# # SCHEDULE THE CLASSES
# check row for an easy or intermediate poi class
# if one is there, pass. if not, schedule one

    # is_it_there = False
    # while is_it_there = False:
    #     for item in row:
    #         if item.prop == 'Poi':
    #             if item.diff == '1':
    #             is_it_there = True
    #             pass
    #         else:
    #             pass
    #     else:
    #         pass
# # if not there, check if that teacher is in the same or an adjacent slot* (this might already exist)
# # make an exception for lunch / day breaks*
# repeat for hoop and staff
# check row for a difficult poi class
# if not there, schedule it
# repeat for hoop and staff

# now let's infill!
# check to see if a row is complete
# if it's not, find an unscheduled workshop
# check to see if the teacher can be scheduled in that slot*
# check to see if there's already a class in More Obscure Prop
# if not, slap it in!
# repeat final loop until all classes are scheduled.


if __name__ == '__main__':
    main()