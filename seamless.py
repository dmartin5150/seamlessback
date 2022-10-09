# from collections import _OrderedDictValuesView
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



care_teams = pd.read_csv('careteams.csv', parse_dates=['DISCH_DT_TM','PREV_APPT','POST_APPT'])


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
 

    print (care_team_array)
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






def create_response(message, status):
    response = {
        'message': message
    }
    return response, status

def get_date(request):
    date_requested = pd.to_datetime((request["date"]))
    print('date requested:', date_requested)
    return date_requested


@app.route('/', methods=['POST'])
def upload_form():
    print(request.json)
    date_requested = get_date(request.json)
    discharge_info = getFinInfoGivenDate(date_requested)
    print('discharge info ', discharge_info)
    return discharge_info, 200


@app.route('/discharges', methods=['GET'])
def dischargeData():
    discharge_data = getDischargeData()
    return discharge_data, 200




app.run(host='0.0.0.0', port=5000)