# from collections import _OrderedDictValuesView
from calendar import c
from dis import disco
import os
import datetime as dt
from datetime import timedelta
import re 
import numpy as np
import pandas as pd
from flask import Flask, flash, request, redirect, render_template, send_from_directory,abort
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)
app.secret_key = "seamless care" # for encrypting the session

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024



care_teams = pd.read_csv('filtered2.csv', parse_dates=['DISCH_DT_TM','PREV_APPT','POST_APPT'])
# filtered = ['Expired']

# filtered_teams = care_teams[(care_teams['E_DISCH_DISPOSITION_DISP'].isin(filtered)) == False]
# filtered_teams.to_csv('filtered2.csv')




# create obj with date, fin number and careteam size
def getFinInfoGivenDate(discharge_date):
    print('dicharge date', discharge_date)
    care_team_date = care_teams[care_teams['DISCH_DT_TM']== discharge_date]
    fins = care_team_date['FIN'].unique()
    care_team_array = []
    for fin in fins:
        care_team_fin = care_team_date[care_team_date['FIN'] == fin]
        num_care_team_members = care_team_fin.shape[0]
        care_team_obj = {'date':str(discharge_date), 'fin':str(fin), 'size':str(num_care_team_members) }
        care_team_array.append(care_team_obj)
 

    return json.dumps(care_team_array)

def getDischargeData():
    start_date = pd.to_datetime('8/1/2022')
    day_count = 31
    discharge_array = []
    for discharge_date in (start_date + timedelta(n) for n in range(day_count)):
        number_of_discharges = len(care_teams[care_teams['DISCH_DT_TM']== discharge_date]['FIN'].unique())
        formated_date = (discharge_date.strftime("%m/%d/%y"))
        discharge_obj = {'date':str(formated_date), 'discharges':str(number_of_discharges)}
        discharge_array.append(discharge_obj)
    
    return json.dumps(discharge_array)





def getCareTeamData(fin):
    care_team_members = care_teams[care_teams['FIN'] == fin]
    team_array=[]
    for ind in care_team_members.index:
        date = care_team_members['DISCH_DT_TM'][ind]
        fin = care_team_members['FIN'][ind]
        type = care_team_members['E_ENCNTR_TYPE_DISP'][ind]
        disp = care_team_members['E_DISCH_DISPOSITION_DISP'][ind]
        lname = care_team_members['PROVIDER_LASTNAME'][ind]
        fname = care_team_members['PROVIDER_FIRSTNAME'][ind]
        specialty = care_team_members['PROVIDER_SPECIALTY'][ind]
        address = care_team_members['PROVIDER_ADDRESS'][ind]
        city= care_team_members['PROVIDER_CITY'][ind]
        state = care_team_members['PROVIDER_STATE'][ind]
        zip = care_team_members['PROVIDER_ZIP'][ind]
        phone = care_team_members['PROVIDER_PHONE'][ind]
        last = care_team_members['PREV_APPT'][ind]
        next = care_team_members['POST_APPT'][ind]
        care_team_obj = {'date':str(date), 'fin':str(fin), 'type':str(type), 'disp':str(disp),
        'lname':str(lname),'fname':str(fname),'specialty':str(specialty), 'address':str(address),
        'city':str(city), 'state':str(state), 'zip':str(zip), 'phone':str(phone), 'last':str(last),
        'next':str(next)}

        team_array.append(care_team_obj)
    return json.dumps(team_array)
        



def create_response(message, status):
    response = {
        'message': message
    }
    return response, status

def get_date(request):
    date_requested = pd.to_datetime((request["date"]))
    print('date requested:', date_requested)
    return date_requested

def getFin(request):
    fin = int(request["fin"])
    return fin

@app.route('/', methods=['POST'])
def upload_form():
    print(request.json)
    date_requested = get_date(request.json)
    discharge_info = getFinInfoGivenDate(date_requested)
    return discharge_info, 200


@app.route('/careteam', methods=['POST'])
def get_care_teams():
    print('careteam request ', request.json)
    fin = getFin(request.json)
    care_team_data = getCareTeamData(fin)
    return care_team_data, 200


@app.route('/discharges', methods=['GET'])
def dischargeData():
    discharge_data = getDischargeData()
    return discharge_data, 200




app.run(host='0.0.0.0', port=5000)