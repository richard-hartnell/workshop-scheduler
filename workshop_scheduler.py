from __future__ import print_function

import os.path
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import random

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
instructor_spreadsheet_id = open('spreadsheet_id.txt', 'r').read()
instructor_spreadsheet_range = 'automation_test_2!A2:AX99' #Define a range of rows. "Class Data" is a sheet name.
schedule_spreadsheet_id = ""

extra_workshops = []
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
                 "sat_1000", "sat_1130", "sat_1430", "sat_1600", "sat_1730", "END_OF_TIME"]

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
    if row[17] != '': #if "first workshop title" isn't blank,
        _title = row[17] #grab the title
        _prop = str(row[19]).lower() #grab the prop
        _difficulty = get_workshop_difficulty(row[20]) #grab the difficulty
        _workshop = Workshop(_teacher, _title, _prop, _difficulty) #make a new workshop object
        workshop_list.append(_workshop) #stick it in the list!
    if row[21] != "": #repeat for 2nd workshop if present
        _title = row[21]
        _prop = str(row[23]).lower()
        _difficulty = get_workshop_difficulty(row[24])
        _workshop = Workshop(_teacher, _title, _prop, _difficulty)
        workshop_list.append(_workshop)
    if row[25] != "": #repeat for 3rd workshop if present
        _title = row[25]
        _prop = str(row[27]).lower()
        _difficulty = get_workshop_difficulty(row[28])
        _workshop = Workshop(_teacher, _title, _prop, _difficulty)
        workshop_list.append(_workshop)
    if row[29] != "": #repeat for 4th workshop if present
        _title = row[29]
        _prop = str(row[31]).lower()
        _difficulty = get_workshop_difficulty(row[32])
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

#big prop jams automatically slotted. note: these never enter workshop_list.
POIJAM = Workshop('Everyone!', 'POI JAM', 'poi', 9)
STAFFJAM = Workshop('Everyone!', 'STAFF JAM', ['single-staff', 'multi-staff'], 9)
HOOPJAM = Workshop('Everyone!', 'HOOP JAM', 'hoop', 9)
JUGGLEJAM = Workshop('Everyone!', 'JUGGLE JAM', ['ball', 'club'], 9)
fri_1430.append(POIJAM)
sat_1130.append(STAFFJAM)
sat_1430.append(JUGGLEJAM)
sat_1600.append(HOOPJAM)

def getCurrentTeacherList(i):
    current_teacher_list = []
    for workshop in list_of_times[i]:
        current_teacher_list.append(workshop.teacher)
    if i in [1, 3, 4, 6, 8, 9]: #check behind if desired
        for workshop in list_of_times[i-1]:
            current_teacher_list.append(workshop.teacher)
    if i in [0, 2, 3, 5, 7, 8]: #check ahead if desired
        for workshop in list_of_times[i+1]:
            current_teacher_list.append(workshop.teacher)
    # print("current teacher list:", current_teacher_list)
    return current_teacher_list

def getCurrentPropList(i):
    _temp_prop_list = []
    for workshop in list_of_times[i]:
        _temp_prop_list.append(str(workshop.prop).replace("[","").replace("]","").replace("'",'').lower())
    return _temp_prop_list

def checkDiffConflict(a, b): #this is where you are working.
    if a.diff or b.diff == None:
        print("Null difficulty found")
        return True    
    if a.diff == 9 or b.diff == 9:
        print ("checkDiffConflict found a prop jam here")
        return True
    if abs(a.diff - b.diff) != 2:
        print("checkDiffConflict found a conflict here")
        return True
    else:
        return False

def checkPropConflict(i, ws, timeslot):
    _current_prop_list = getCurrentPropList(i)
    for individual_prop in ws.prop:
        individual_prop = individual_prop.replace("[","").replace("]","").replace("'",'').lower()
        _strung_prop_list = str(_current_prop_list)
        print("TEST: prop = ", individual_prop, "| _strung_prop_list = ", _strung_prop_list)
        # if "hoop" in str(['poi', 'hoop']):
        #     print(3 / 0)
        if (individual_prop in str(_current_prop_list)):
            for scheduled_class in timeslot:
                if (individual_prop in str(scheduled_class.prop)):
                    # print("Found a conflict: ", individual_prop, "vs", scheduled_class.prop, ". Compare difficulty.")
                    if checkDiffConflict(ws, scheduled_class) == True:
                        print("checkDiffConflict: true. Prop1:", individual_prop, ws.diff, ". Prop2:", str(scheduled_class.prop).lower(), scheduled_class.diff)
                        return True
                    elif checkDiffConflict(ws, scheduled_class) == False:
                        print("checkDiffConflict: false. Prop1:", individual_prop, ws.diff, ". Prop2:", str(scheduled_class.prop).lower(), scheduled_class.diff)
                        # return False
                    else:
                        print("Error in checkDiffConflict")
                else:
                    print("checkPropConflict: no prop conflict found.")
                    # return False
        else:
            print("checkDiffConflict: false. Prop1:", individual_prop, ws.diff, ". Prop list: ", str(_current_prop_list))
            return False

if __name__ == '__main__':
    main()

def buildWorkshopSchedule(workshop_list):
    for ws in workshop_list: #for every workshop in the list,
        _scheduled = False
        i = 0
        print("SCHEDULING: " + ws.title + " with " + ws.teacher)
        while _scheduled == False:
            if i > 9:
                print("A workshop couldn't be scheduled for some reason.")
                extra_workshops.append(ws)
                _scheduled = True #not really haha!
                break
            timeslot = list_of_times[i]
            print("Timeslot: ", i)
            if len(timeslot) > 9:
                if i == 9:
                    print("The last timeslot is full!")
                    extra_workshops.append(ws)
                    _scheduled = True
                print("Timeslot", (i), "is full")
                print("Advancing timeslot from ", list_of_timenames[i], "to", list_of_timenames[i+1])
                i += 1
                continue
            elif str(ws.teacher).lower() in str(getCurrentTeacherList(i)).lower(): #check workshop teacher against timeslot (and last timeslot)
                print("Teacher conflict")
                print("Advancing timeslot from ", list_of_timenames[i], "to", list_of_timenames[i+1])
                i += 1
                continue
            elif checkPropConflict(i, ws, timeslot) == True:
                print("checkPropConflict returned True")
                print("Advancing timeslot from ", list_of_timenames[i], "to", list_of_timenames[i+1])
                i += 1
                continue
            else:
                print("Appending", ws.title, "-", ws.teacher, "to", list_of_timenames[i])
                print("Prop:", ws.prop, ws.diff, ". Prop list: ", getCurrentPropList(i))
                timeslot.append(ws)
                _scheduled = True


print("IT'S TIME FOR THE BIG TEST!")

def printSchedule():
    i = 0
    for time in list_of_times:
        print("\n TIMESLOT:", list_of_timenames[i])
        for ws in time:
            print(ws.title, "with", ws.teacher + ". Prop:", ws.prop, "Difficulty:", ws.diff)
        i += 1
    print("\n Extra workshops: ")
    for ws in extra_workshops:
        print(ws. title, "with", ws.teacher)

buildWorkshopSchedule(workshop_list)
printSchedule()

