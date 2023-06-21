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

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
instructor_spreadsheet_id = open('spreadsheet_id.txt', 'r').read()
instructor_spreadsheet_range = 'WORKSHOPS!A2:AX99' #Define a range of rows. "automation_test_2" is a sheet name here.
schedule_spreadsheet_id = ""

#some useful variables.
extra_workshops = []
extra_workshops_2 = []
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
teacher_list = []
list_of_times = [fri_1000, fri_1130, fri_1430, fri_1600, fri_1730,
                 sat_1000, sat_1130, sat_1430, sat_1600, sat_1730]
list_of_timenames = ["fri_1000", "fri_1130", "fri_1430", "fri_1600", "fri_1730",
                 "sat_1000", "sat_1130", "sat_1430", "sat_1600", "sat_1730", "END_OF_TIME"]
# list_of_exempt_times = [fri_1000, fri_1430, sat_1000, sat_1430] #times we don't worry about teacher conflicts
list_of_tech_times = [fri_1600, fri_1730] #reserved for gala performers

# define workshop and timeslot object classes
class Workshop:
    def __init__(self, teacher, title, prop, diff):
        self.teacher = teacher #stage name if given, else given name
        self.title = title #workshop title
        self.prop = list(str(prop).split(", ")) #check boxes, not radio buttons
        self.diff = diff #difficulty

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
        _prop = str(row[19]).lower() #grab the prop and lowercase it.
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

def print_the_schedule(): #pretty self-explanatory. this should be expanded into create_schedule or something.
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

def getCurrentTeacherList(i): #creates a list of teachers of concern so that nobody's double-booked.
    current_teacher_list = [] #initialize.
    for workshop in list_of_times[i]: #append every teacher in the current timeslot.
        current_teacher_list.append(workshop.teacher) 
    if i in [1, 3, 4, 6, 8, 9]: #check behind if the slot before isn't lunch or yesterday.
        for workshop in list_of_times[i-1]: #append every teacher in that timeslot.
            current_teacher_list.append(workshop.teacher) 
    if i in [0, 2, 3, 5, 7, 8]: #check ahead if the slot isn't before lunch or last in the day.
        for workshop in list_of_times[i+1]: #append every teacher in that timeslot.
            current_teacher_list.append(workshop.teacher)
    return current_teacher_list

def getCurrentPropList(i): #get a list of props in THIS timeslot.
    _temp_prop_list = [] #initialize
    for workshop in list_of_times[i]: #and iterate over this timeslot.
        _temp_prop_list.append(str(workshop.prop).replace("[","").replace("]","").replace("'",'').lower()) #clean and stringify
    return _temp_prop_list

def checkDiffConflict(a, b): #check relative difficulty of any workshop in the same prop.
    if len(a.prop) > 5 or len(b.prop) > 5 or a.prop == 'Misc-Prop' or b.prop == 'Misc-Prop':
        # print("One class is miscellaneous. Don't worry about it.")
        return False 
    if a.diff or b.diff == None:
        # print("Null difficulty found!!", a.title, a.diff, b.title, b.diff)
        return True    
    if a.diff == 9 or b.diff == 9:
        # print ("checkDiffConflict found a prop jam here")
        return True
    if abs(a.diff - b.diff) != 2:
        # print("checkDiffConflict found a conflict here")
        return True
    else:
        return False

def checkPropConflict(i, ws, timeslot):
    _current_prop_list = getCurrentPropList(i)
    if len(ws.prop) > 4 or 'Misc-Prop' in ws.prop:
        # print("Check")
        return False
    for individual_prop in ws.prop:
        individual_prop = individual_prop.replace("[","").replace("]","").replace("'",'').lower()
        _strung_prop_list = str(_current_prop_list)
        # print("TEST: prop = ", individual_prop, "| _strung_prop_list = ", _strung_prop_list)
        # if "hoop" in str(['poi', 'hoop']):
        #     print(3 / 0)
        if (individual_prop in str(_current_prop_list)):
            for scheduled_class in timeslot:
                if (individual_prop in str(scheduled_class.prop)):
                    # print("Found a conflict: ", individual_prop, "vs", scheduled_class.prop, ". Compare difficulty.")
                    if checkDiffConflict(ws, scheduled_class):
                        return True
                else:
                    pass
        else:
            # print("checkDiffConflict: false. Prop1:", individual_prop, ws.diff, ". Prop list: ", str(_current_prop_list))
            return False

if __name__ == '__main__':
    main()

def buildWorkshopSchedule(workshop_list):
    for ws in workshop_list: #for every workshop in the list,
        _scheduled = False
        i = 0
        # print("SCHEDULING: " + ws.title + " with " + ws.teacher)
        while _scheduled == False:
            if i > 9:
                # print("A workshop couldn't be scheduled for some reason.")
                extra_workshops.append(ws)
                _scheduled = True #not really haha!
                break
            timeslot = list_of_times[i]
            # print("Timeslot: ", i)
            if len(timeslot) > 8:
                if i == 9:
                    # print("The last timeslot is full!")
                    extra_workshops.append(ws)
                    _scheduled = True
                # print("Timeslot", (i), "is full")
                # print("Advancing timeslot from ", list_of_timenames[i], "to", list_of_timenames[i+1])
                i += 1
                continue
            elif str(ws.teacher).lower() in str(getCurrentTeacherList(i)).lower(): #check workshop teacher against timeslot (and last timeslot)
                # print("Teacher conflict")
                # print("Advancing timeslot from ", list_of_timenames[i], "to", list_of_timenames[i+1])
                i += 1
                continue
            elif checkPropConflict(i, ws, timeslot) == True:
                # print("checkPropConflict returned True")
                # print("Advancing timeslot from ", list_of_timenames[i], "to", list_of_timenames[i+1])
                i += 1
                continue
            else:
                # print("Appending", ws.title, "-", ws.teacher, "to", list_of_timenames[i])
                # print("Prop:", ws.prop, ws.diff, ". Prop list: ", getCurrentPropList(i))
                timeslot.append(ws)
                _scheduled = True

def makeTeacherList():
    for ws in workshop_list:
        if ws.teacher not in teacher_list:
            teacher_list.append(ws.teacher)

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

# random.shuffle(workshop_list)
buildWorkshopSchedule(workshop_list)
# printSchedule()
# print("Length of workshop_list: ", len(workshop_list))
# print("Length of extra_workshops: ", len(extra_workshops))
# talky_classes = []
# for workshop in workshop_list:
#     if "talk" in workshop.prop:
#         talky_classes.append(workshop)
# print("Talks: ")
# for talk in talky_classes:
#     print(talk.title, "with", talk.teacher)

def scheduleToCsv():
    print("Attempting to write CSV...")
    with open('event.csv', 'a') as csv_to_write:
        writer(csv_to_write).writerow(['','MOON','HEART','CIRCLE','SQUARE','HEX','STAR','SPIRAL','DIAMOND'])
        nextline = []
        i = 0
        for time in list_of_times:
            nextline = []
            # begin row with timeslot name
            nextline.append(list_of_timenames[i])
            #iterate over workshops in slot and add all titles
            for workshop in time:
                nextline.append(workshop.title)
            #append the line to CSV
            writer(csv_to_write).writerow(nextline)
            #re-init nextline with an empty space below timeslot title
            nextline = ['']
            #iterate over workshops in slot and add instructor names
            for workshop in time:
                nextline.append(workshop.teacher)
            #append the line
            writer(csv_to_write).writerow(nextline)
            #special cases
            if i == 1 or i == 6:
                writer(csv_to_write).writerow(['LUNCH'])
            if i == 4:
                writer(csv_to_write).writerow(['SATURDAY'])
            i += 1

# scheduleToCsv()
makeTeacherList()

def makeLetters():
    show_list = ['Abi Lindsey',
                'Bella LaRue',
                'Exuro Piechocki',
                'Scramble James',
                'Alison Lockfeld',
                'Haley Doran',
                'Enrico Vinholi',
                'Lance Woods',
                'Ling Ling Lee',
                'Eli March',
                'Kendall Moyer',
                'Matan Presberg',
                'Allie T',
                'Tyfoods']
    for teacher in teacher_list:
        filename = "./letters/" + teacher.replace(" ", "_") + ".txt"
        shops = []
        show_decision = ""
        for ws in workshop_list:
            if ws.teacher == teacher:
                shops.append(ws.title)
        totalmoney = len(shops) * 50
        # greeting = "Hellooooo " + teacher + "!"  + '\n\n'
        # paragraph1 = "So happy to finally be sending you this email confirming your offer from Kindle NW. Thanks for hanging on for as long as you have about our decision-making process this year." + '\n\n'
        # paragraph2 = "We've selected your following workshop offerings for our schedule: " + '\n'
        shopstring = '\n'.join(str(shop) for shop in shops)
        # paragraph3 = "A draft workshop schedule will be coming out very soon. I may edit some of your workshop titles for length, clarity, spelling, etc." + '\n\n'
        if teacher in show_list:
            totalmoney += 100
            show_decision = "We also selected you for an act in the show! Please expect another email from Riel Green, our show coordinator, following this one."
        else:
            show_decision = "You are not on the roster for this year's show. A little less glory, but a lot fewer responsibilities...!"
        # paragraph5 = "We have budgeted XX to compensate you for your contribution to the event." + '\n\n'
        # paragraph6 = "We know that this is better than most festivals pay, but we also know that it's not a lot for a weekend's work. We wish we would pay like corporate clients! In the case that you do have to bail out for another gig or any other reason, we understand; but please let us know ASAP by replying to this email." + '\n\n'
        # paragraph8 = "Again, thanks so much for applying and we'll see you in the woods so soon!" + '\n\n'
        # closing = "Y'all's truly," + '\n' + "Richard Hartnell" + '\n' + "Team Workshops, Kindle NW"
        # lettercontent = greeting + paragraph1 + paragraph2 + shopstring + '\n\n' + paragraph3 + paragraph4 + paragraph5 + paragraph6 + paragraph8 + closing
        if teacher == 'Abi Lindsey':
            with open(filename, 'a+') as file:
                # file.write(lettercontent)
                file.write(f'''
Hellooooo {teacher}!
                           
So happy to finally be sending you this email confirming your offer from Kindle NW. Thanks for hanging on for as long as you have about our decision-making process this year.
                           
We've selected your following workshop offerings for our schedule: 
                           
{shopstring}
                           
{show_decision}

We have budgeted XX to compensate you for your contribution to the event. Of course we wish we could pay like corporate clients...! In the case that you do have to bail out for another gig or any other reason, we understand; but please let us know ASAP by replying to this email.

Again, thanks so much for applying and we'll see you in the woods so soon!

Y'all's truly,
Richard Hartnell
Team Workshops, Kindle NW''')

makeLetters()