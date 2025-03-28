from __future__ import print_function
import requests
import re
from urllib.parse import urlparse, parse_qs
import os
import pandas as pd
from timeslots import *
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from csv import writer
import random

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
instructor_spreadsheet_id = open('spreadsheet_id.txt', 'r').read()
instructor_spreadsheet_range = 'Workshops!A2:AL99' #Define a range of rows. "automation_test_2" is a sheet name here.
schedule_spreadsheet_range = 'SCHEDULE!A1:K30' #Define a range of rows. "automation_test_2" is a sheet name here.
# schedule_spreadsheet_id = open('schedule_id.txt', 'r').read()

class Workshop:
    def __init__(self, teacher, title, prop, diff):
        self.teacher = teacher
        self.title = title
        self.prop = list(str(prop).split(", "))
        self.diff = diff

extra_workshops = []
extra_workshops_2 = []
workshop_list = []
teacher_list = []
list_of_timenames = ["fri_1000", "fri_1130", "fri_1430", "fri_1600", "fri_1730",
                 "sat_1000", "sat_1130", "sat_1430", "sat_1600", "sat_1730", "END_OF_TIME"]
list_of_tech_times = [fri_1600, fri_1730] #reserved for gala performers

POIJAM = Workshop('Everyone!', 'POI JAM', 'poi', 9)
STAFFJAM = Workshop('Everyone!', 'STAFF JAM', ['single-staff', 'multi-staff'], 9)
HOOPJAM = Workshop('Everyone!', 'HOOP JAM', 'hoop', 9)
JUGGLEJAM = Workshop('Everyone!', 'JUGGLE JAM', ['ball', 'club'], 9)

fri_1430.append(POIJAM)
sat_1130.append(STAFFJAM)
sat_1430.append(JUGGLEJAM)
sat_1600.append(HOOPJAM)

def get_teachers(values):
    for teacher in values[3]:
        fri_1000.append(teacher)
    for teacher in values[5]:
        fri_1130.append(teacher)
    for teacher in values[8]:
        fri_1430.append(teacher)
    for teacher in values[10]:
        fri_1600.append(teacher)
    for teacher in values[12]:
        fri_1730.append(teacher)
    for teacher in values[16]:
        sat_1000.append(teacher)
    for teacher in values[18]:
        sat_1130.append(teacher)
    for teacher in values[22]:
        sat_1430.append(teacher)
    for teacher in values[24]:
        sat_1600.append(teacher)
    for teacher in values[26]:
        sat_1730.append(teacher)

def check_schedule():
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
        get_teachers(values)
    except HttpError as err:
        print(err)

def trim_teachers():
    for time in list_of_times:
        time.remove('')
        if 'Everyone!' in time:
            time.remove('Everyone!')

def check_teachers():
    for teacher in fri_1000:
        if teacher in fri_1130:
            print("Conflict found: ", teacher, "in both Friday 10:00A and Friday 11:30A")
    for teacher in fri_1600:
        if teacher in fri_1430:
            print("Conflict found: ", teacher, "in both Friday 2:30P and Friday 4:00P")
        if teacher in fri_1730:
            print("Conflict found: ", teacher, "in both Friday 4:00P and Friday 5:30P")
    for teacher in sat_1000:
        if teacher in sat_1130:
            print("Conflict found: ", teacher, "in both Saturday 10:00A and Saturday 11:30A")
    for teacher in sat_1600:
        if teacher in sat_1430:
            print("Conflict found: ", teacher, "in both Saturday 2:30P and Saturday 4:00P")
        if teacher in sat_1730:
            print("Conflict found: ", teacher, "in both Saturday 4:00P and Saturday 5:30P")

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
        result = sheet.values().get(spreadsheetId=instructor_spreadsheet_id,
                                    range=instructor_spreadsheet_range).execute()
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
    #get teacher name
    if row[4] != ".":
        _teacher = row[4] #stage name
    else:
        _teacher = row[3] #if no stage name, use given name
    #get teacher workshops
    try:
        if row[5]: #workshop 1
            _title = row[5]
            _prop = str(row[7]).lower()
            _difficulty = get_workshop_difficulty(row[8])
            _workshop = Workshop(_teacher, _title, _prop, _difficulty)
            workshop_list.append(_workshop)
        if row[9]: #workshop 2
            _title = row[9]
            _prop = str(row[11]).lower()
            _difficulty = get_workshop_difficulty(row[12])
            _workshop = Workshop(_teacher, _title, _prop, _difficulty)
            workshop_list.append(_workshop)
        if row[13]:#workshop 3
            _title = row[13]
            _prop = str(row[15]).lower()
            _difficulty = get_workshop_difficulty(row[16])
            _workshop = Workshop(_teacher, _title, _prop, _difficulty)
            workshop_list.append(_workshop)
        if row[17]: #workshop 4
            _title = row[17]
            _prop = str(row[19]).lower()
            _difficulty = get_workshop_difficulty(row[20])
            _workshop = Workshop(_teacher, _title, _prop, _difficulty)
            workshop_list.append(_workshop)
    except Exception as error:
        print("Error with " + _teacher + "'s workshops:", error)

def print_the_schedule():
    timecounter = 0
    for time in list_of_times:
        timecounter += 1
        print("Time: " + str(list_of_timenames[timecounter - 1]))
        for thing in time:
            print("Workshop: " + thing.title + " with " + thing.teacher)

def getCurrentTeacherList(i):
    current_teacher_list = []
    for workshop in list_of_times[i]:
        current_teacher_list.append(workshop.teacher) 
    if i in [1, 3, 4, 6, 8, 9]:
        for workshop in list_of_times[i-1]:
            current_teacher_list.append(workshop.teacher) 
    if i in [0, 2, 3, 5, 7, 8]:
        for workshop in list_of_times[i+1]:
            current_teacher_list.append(workshop.teacher)
    return current_teacher_list

def getCurrentPropList(i):
    _temp_prop_list = []
    for workshop in list_of_times[i]:
        _temp_prop_list.append(str(workshop.prop).replace("[","").replace("]","").replace("'",'').lower()) #clean and stringify
    return _temp_prop_list

def checkDiffConflict(a, b):
    try:
        if len(a.prop) > 5 or len(b.prop) > 5 or a.prop == 'Misc-Prop' or b.prop == 'Misc-Prop':
            return False 
        if a.diff or b.diff == None:
            return True    
        if a.diff == 9 or b.diff == 9:
            return True
        if abs(a.diff - b.diff) != 2:
            return True
        else:
            return False
    except Exception as error:
        print("DIFFICULTY ERROR: " + a.teacher + a.title + "and" + b.title + ". Error: ", error)

def checkPropConflict(i, ws, timeslot):
    _current_prop_list = getCurrentPropList(i)
    if len(ws.prop) > 4 or 'Misc-Prop' in ws.prop:
        return False
    for individual_prop in ws.prop:
        individual_prop = individual_prop.replace("[","").replace("]","").replace("'",'').lower()
        _strung_prop_list = str(_current_prop_list)
        if (individual_prop in str(_current_prop_list)):
            for scheduled_class in timeslot:
                if (individual_prop in str(scheduled_class.prop)):
                    if checkDiffConflict(ws, scheduled_class):
                        return True
                else:
                    pass
        else:
            return False
    
def buildWorkshopSchedule(workshop_list):
    for ws in workshop_list:
        schedule_workshop(ws)

def schedule_workshop(ws):
    _scheduled = False
    i = 0
    while _scheduled == False:
        if i > 9:
            extra_workshops.append(ws)
            _scheduled = True #note: it's "scheduled" in the overflow list here
            break
        timeslot = list_of_times[i]
        if len(timeslot) > 8:
            if i == 9:
                extra_workshops.append(ws)
                _scheduled = True
            i += 1
            continue
        elif str(ws.teacher).lower() in str(getCurrentTeacherList(i)).lower(): #check workshop teacher against timeslot (and last timeslot)
            i += 1
            continue
        elif checkPropConflict(i, ws, timeslot) == True:
            i += 1
            continue
        else:
            timeslot.append(ws)
            _scheduled = True

def makeTeacherList():
    for ws in workshop_list:
        if ws.teacher not in teacher_list:
            teacher_list.append(ws.teacher)

def scheduleToCsv():
    print("Writing schedule to CSV...")
    if os.path.exists('event.csv'):
        os.remove('event.csv')
    with open('event.csv', 'a') as csv_to_write:
        writer(csv_to_write).writerow(['','MOON','HEART','CIRCLE','SQUARE','HEX','STAR','LODGE','TENT','RANGE','CIRCLE'])
        nextline = []
        i = 0
        for time in list_of_times:
            # nextline = []
            nextline.append(list_of_timenames[i])
            for workshop in time:
                nextline.append(workshop.title)
            writer(csv_to_write).writerow(nextline)
            nextline = ['']
            for workshop in time:
                nextline.append(workshop.teacher)
            writer(csv_to_write).writerow(nextline)
            if i == 1 or i == 6:

                writer(csv_to_write).writerow(['LUNCH'])
            if i == 4:
                writer(csv_to_write).writerow(['SATURDAY'])
            i += 1

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

def makeLetters():
    show_list = ['The FloWarrior',
                'Emma Hörnell',
                'Eric Sipos',
                'Riel Green',
                'Soy Sauce & Seasoned Salt',
                'Rosalie Ash',
                'SolRiso',
                'Master Ong',
                'Melwebstar',
                'Blu Hoopz',
                'Kawika Lee',
                'Mx Marchandt']
    staff_list = ['Annabelle Wright',
            'Brian Hirschberger',
            'The Mighty Bearsnake',
            'Davi Lux',
            'Erika Ryn',
            'Starshine the clown',
            'SpaceFairy',
            'Riel Green',
            'Katiefishface',
            'T-Spoon',
            'Lady Aetheria']
    for teacher in teacher_list:
        filename = "./letters/" + teacher.replace(" ", "_") + ".txt"
        shops = []
        show_decision = ""
        for ws in workshop_list:
            if ws.teacher == teacher:
                shops.append(ws.title)
        totalmoney = len(shops) * 50
        shopstring = '\n'.join(str(shop) for shop in shops)
        if teacher in show_list:
            totalmoney += 100
            show_decision = "We also selected your act for the show! Please expect an additional email from Kendall, our show coordinator, following this email."
        else:
            show_decision = "You are not on the roster for this year's show. A little less glory, but a lot fewer responsibilities...!"
        with open(filename, 'a+') as file:
            file.write(f'''Hellooooo {teacher}!

So happy to finally send you this email confirming your acceptance to the faculty of Kindle NW 2024!!

We've selected your following workshop offerings for our schedule:

{shopstring}

(please remember that we might edit your workshop titles for length and clarity on the final schedule)

{show_decision}

''')
            if teacher in staff_list:
                file.write(f'''Since you are on staff, you will already not have to buy a ticket to attend the event. We also have ${totalmoney + (10 * len(shops))} budgeted to compensate you for your contribution, which includes a bonus for adding instruction on top of your other KNW duties. Thanks for your willingness to be part of this by-artists-for-artists thing.''')
            else:
                file.write(f'''You will not have to buy a ticket to attend the event. We also have ${totalmoney} budgeted to compensate you for your contribution, which includes a travel stipend. Thanks for your willingness to be part of this by-artists-for-artists thing.''')
            file.write(f'''

If you are flying, please please *please* buy your flights now while they are cheap (best airports are PDX, EUG, SEA, or possibly YVR). If you need an advance for travel costs, we have a few stipends available up front but please reach out right away.

If you have any questions or updates for us, you can just reply to this email.

We are so excited that you can be a part of this year's incredible roster and can't wait to see you in the woods!

<3,
The Faculteam @ Kindle NW''')

def download_google_drive_file(link, destination):
    # Parse the file ID from the link
    file_id = extract_file_id(link)

    if file_id:
        # Construct the download URL
        download_url = f"https://drive.google.com/uc?id={file_id}"

        # Send a GET request to the download URL
        response = requests.get(download_url)

        if response.status_code == 200:
            # Save the content to the specified destination
            with open(destination, 'wb') as f:
                f.write(response.content)

            print(f"Downloaded file to {destination}")
        else:
            print("Failed to download the file.")
    else:
        print("Invalid Google Drive link.")

def extract_file_id(link):
    # Extract the file ID from the 'id' query parameter
    parsed_url = urlparse(link)
    query_params = parse_qs(parsed_url.query)
    file_id = query_params.get('id', [None])[0]
    return file_id

def main():
    fetch_schedule()
    buildWorkshopSchedule(workshop_list)
    makeTeacherList()

    # # error checkers if necessary:
    # printSchedule()
    for workshop in extra_workshops:
        print(workshop.title + " with " + workshop.teacher)
    print("Length of workshop_list: ", len(workshop_list))
    print("Length of extra_workshops: ", len(extra_workshops))

    # un-comment functions below to write event.csv and/or make response letters
    # scheduleToCsv()
    # makeLetters()
    # test_google_drive_link = "https://drive.google.com/open?id=1Mox59Xl7YfIsPbGZmm8f-X39ogaNSCwm"
    # download_destination = "downloaded_file.jpg"
    # download_google_drive_file(test_google_drive_link, download_destination)

if __name__ == '__main__':
    main()