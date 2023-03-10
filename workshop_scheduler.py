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
instructor_spreadsheet_id = open('spreadsheet_id.txt', 'r').read()
instructor_spreadsheet_range = 'Sheet1!A2:AX99' #Define a range of rows. "Class Data" is a sheet name.
schedule_spreadsheet_id = ""

local_schedule = []
workshop_list = []
fri_1000 = []
fri_1130 = []
fri_1430 = []
fri_1600 = []
fri_1730 = []
sat_1000 = []
sat_1130 = []
sat_1430 = []
sat_1600 = []
sat_1730 = []
list_of_times = [fri_1000, fri_1130, fri_1430, fri_1600, fri_1730,
                 sat_1000, sat_1130, sat_1430, sat_1600, sat_1730]
list_of_exempt_times = [fri_1430, sat_1000, sat_1430]
list_of_tech_times = [fri_1600, fri_1730] #reserved for gala performers
last_teacher_list = []

# define workshop and timeslot object classes
class Workshop:
    def __init__(self, teacher, title, prop, diff):
        self.teacher = teacher #stage name if given, else given name
        self.title = title #workshop title
        self.prop = str(prop).split(", ") #check boxes, not radio buttons
        self.diff = diff #difficulty

TBA = Workshop("TBA", "TBA", "TBA", 0)

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
        result = sheet.values().get(spreadsheetId=instructor_spreadsheet_id,  #CREATE A DICT(?) OF THIS SHEET
                                    range=instructor_spreadsheet_range).execute()      #RANGE OF ROWS 
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return
        for row in values:
            get_workshops(row)
    except HttpError as err:
        print(err)

# a function to rate class difficulty from the radio button response (1 = beginner, 3 = advanced)
def get_workshop_difficulty(ws):
    if 'SPECIFICALLY' in ws:
        return 1
    if 'OK' in ws:
        return 2
    if 'NOT' in ws:
        return 3

#pluck workshops from instructor app (used above in main)
def get_workshops(row):
    if row[3] != '':
        _teacher = row[3] #read in teacher's stage name if present
    else:
        _teacher = row[2] #if no stage name, use given name
    if row[16] != '': #if "first workshop title" isn't blank,
        _title = row[16] #grab the title
        _prop = row[18] #grab the prop
        _difficulty = get_workshop_difficulty(row[19]) #grab the difficulty
        _workshop = Workshop(_teacher, _title, _prop, _difficulty) #make a new workshop object
        workshop_list.append(_workshop) #stick it in the list!
    if row[20] != "": #repeat for 2nd workshop if present
        _title = row[20]
        _prop = row[22]
        _difficulty = get_workshop_difficulty(row[23])
        _workshop = Workshop(_teacher, _title, _prop, _difficulty)
        workshop_list.append(_workshop)
    if row[24] != "": #repeat for 3rd workshop if present
        _title = row[24]
        _prop = row[26]
        _difficulty = get_workshop_difficulty(row[27])
        _workshop = Workshop(_teacher, _title, _prop, _difficulty)
        workshop_list.append(_workshop)
    if row[28] != "": #repeat for 4th workshop if present
        _title = row[28]
        _prop = row[30]
        _difficulty = get_workshop_difficulty(row[31])
        _workshop = Workshop(_teacher, _title, _prop, _difficulty)
        workshop_list.append(_workshop)

#big prop jams automatically slotted. note: these never enter workshop_list.
POIJAM = Workshop('Everyone!', 'POI JAM', 'poi', 9)
STAFFJAM = Workshop('Everyone!', 'STAFF JAM', ['staff', 'staffs'], 9)
HOOPJAM = Workshop('Everyone!', 'HOOP JAM', 'hoop', 9)
JUGGLEJAM = Workshop('Everyone!', 'JUGGLE JAM', ['ball', 'club'], 9)
fri_1430.append(POIJAM)
sat_1130.append(STAFFJAM)
sat_1430.append(JUGGLEJAM)
sat_1600.append(HOOPJAM)

#check to see if workshops are incompatible
def check_ws_match(a, b):
    if len(a.prop) > 2 or len(b.prop) > 2:
        return False
    if a.diff == 9 or b.diff == 9:
        return True
    for thing in a.prop: #check all the props in a.prop
        for thing2 in b.prop: #against all the props in b.prop
            if thing2 == thing: #if any of them are the same,
                if abs(a.diff - b.diff) < 2: #check difficulty (4 lines)
                    return True
                if abs(a.diff - b.diff) > 1:
                    return False              #they match if diffs are similar
    if a.teacher == b.teacher:
        return True
    else:
        return False      


# WHAT TO DO?
# # iterate over list of workshops
    # check earliest timeslot for a class that matches
        # look at each prop for all listed classes in the timeslot.
            # exempt any that use more than one prop.
                # exempt any that have an abs difficulty difference < 2

#build out a teacher list for the current slot for reference NEXT slot
last_teacher_list = []
current_teacher_list = []
def make_last_teacher_list(a):
    last_teacher_list = []
    for slot in a:
        if slot.teacher != "TBA":
            last_teacher_list.append(slot.teacher)

def make_current_teacher_list(b):
    current_teacher_list = []
    for slot in b:
        current_teacher_list.append(slot.teacher)

if __name__ == '__main__':
    main()

#go through workshop_list and schedule everything!
for ws in workshop_list: #for every workshop in the list,
    for time in list_of_times: #search a time (e.g. Friday 10:00)
        make_current_teacher_list(time) #initialize timeslot's roster
        if time not in list_of_exempt_times: #skip if teacher schedule conflict
            if ws.teacher in (last_teacher_list + current_teacher_list):
                make_last_teacher_list(time)
                pass
        make_last_teacher_list(time)
        if len(time) > 8:   #skip if timeslot is full
            make_last_teacher_list(time)
            pass
        for slot in time:   #skip if there's a match in prop+diff
            if hasattr(slot, 'workshop'):
                if check_ws_match(slot.workshop, ws) == True:
                    pass
        time.append(ws)
        make_last_teacher_list(time)
        break

## TODO

#error check everything lol
#get the times as an output

for time in list_of_times:
    print("Time slot")
    for thing in time:
        print("Workshop: " + thing.title + " with " + thing.teacher)