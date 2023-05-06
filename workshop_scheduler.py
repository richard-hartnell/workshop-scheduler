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
list_of_timenames = ["fri_1000", "fri_1130", "fri_1430", "fri_1600", "fri_1730",
                 "sat_1000", "sat_1130", "sat_1430", "sat_1600", "sat_1730"]

list_of_exempt_times = [fri_1000, fri_1430, sat_1000, sat_1430]
list_of_tech_times = [fri_1600, fri_1730] #reserved for gala performers

# define workshop and timeslot object classes
class Workshop:
    def __init__(self, teacher, title, prop, diff):
        self.teacher = teacher #stage name if given, else given name
        self.title = title #workshop title
        self.prop = list(str(prop).split(", ")) #check boxes, not radio buttons
        self.diff = diff #difficulty

TBA = Workshop("TBA", "TBA", "TBA", 0)

def main(): #fetches all the remote data and builds workshop_list."
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
def get_workshop_difficulty(ws):
    if 'SPECIFICALLY' in ws:
        return 1
    if 'OK' in ws:
        return 2
    if 'NOT' in ws:
        return 3
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
def print_the_schedule():
    print("THE SCHEDULE:")
    timecounter = 0
    for time in list_of_times:
        timecounter += 1
        print("Time: " + str(list_of_timenames[timecounter - 1]))
        for thing in time:
            print("Workshop: " + thing.title + " with " + thing.teacher)

    print(sat_1130[0].title)

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

#these might be redundant now
current_teacher_list = []
current_prop_list = []

def getCurrentTeacherList(i):
    current_teacher_list = []
    for workshop in list_of_times[i]:
        current_teacher_list.append(workshop.teacher)
        if i in [1, 3, 4]:
            for workshop in list_of_times[i-1]:
                current_teacher_list.append(workshop.teacher)
    return current_teacher_list

def getCurrentPropList(i):
    _temp_prop_list = []
    for workshop in list_of_times[i]:
        _temp_prop_list.append(workshop.prop)
    return _temp_prop_list

def checkDiffs(a, b): #this is where you are working.
    if a.diff == 9 or b.diff == 9:
        print ("There is a prop jam in the same prop here")
        return "Conflict"
    if abs(a.diff - b.diff) > 1:
        return "Do it"
    else:
        return "Don't do it"

def checkPropConflict(i, ws, timeslot):
    _current_prop_list = getCurrentPropList(i)
    for individual_prop in ws.prop:
        if individual_prop.casefold() in str(_current_prop_list).casefold():
            print("True - prop of interest:", str(ws.prop), "WS rating:", str(ws.diff), "| getCurrentPropList(i) =", str(_current_prop_list))
            print("Checking individual props...")
            for scheduled_class in timeslot:
                if individual_prop.casefold() in str(scheduled_class.prop).casefold():
                    print("Found a conflict: ", individual_prop, "vs", scheduled_class.prop, ". Compare difficulty.")
                    if checkDiffs(ws, scheduled_class) == "Compatible":
                        print("Resolve conflict")
                    elif checkDiffs(ws, scheduled_class) == "Incompatible":
                        print("No conflict")
                        return False
                    else:
                        print("Error in checkDiffs")
                        # UNTESTED. -you, cinco de mayo

            return True
        else:
            return False

if __name__ == '__main__':
    main()

for ws in workshop_list: #for every workshop in the list,
    _scheduled = False
    i = 0
    while _scheduled == False:
        timeslot = list_of_times[i]
        print("SCHEDULING: " + ws.title + " with " + ws.teacher)
        print("Timeslot: ", str(i + 1))
        if len(timeslot) > 8:
            print("Timeslot", (i+1), "is full")
            i+= 1
        elif ws.teacher in getCurrentTeacherList(i): #check workshop teacher against timeslot (and last timeslot)
            print("Teacher conflict")
            i += 1
        elif checkPropConflict(i, ws, timeslot) == True:
            print("Potential prop conflict") #this is fine; update checkPropConflict() with difficulty checker!
            i += 1
        else: 
            timeslot.append(ws)
            _scheduled = True



"""
is the timeslot full?

is there a similar prop?
in a similar difficulty?

is it lunch or morning?
is the teacher teaching now or before?
is it show tech?

"""
