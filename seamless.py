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
    now = dt.datetime.now()

    current_time = now.strftime("%H:%M:%S")
    care_team_members = care_teams[care_teams['FIN'] == fin].sort_values(['POST_APPT'])
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
        'next':str(next),'time':str(current_time)}

        team_array.append(care_team_obj)
    print(team_array)
    return json.dumps(team_array)
        

def getProviders(letter):
    if letter == '':
        print('no letter')
        return []
    providers = care_teams.loc[care_teams['PROVIDER_LASTNAME'].str.startswith(letter)].copy()
    providers.drop_duplicates(subset=['PROVIDER_NPI'], inplace=True)
    provider_array = []
    for ind in providers.index:
        id =  providers['PROVIDER_NPI'][ind]
        npi = providers['PROVIDER_NPI'][ind]
        name = str(providers['PROVIDER_FIRSTNAME'][ind]) + ' ' + str(providers['PROVIDER_LASTNAME'][ind])
        size = len(care_teams[care_teams['PROVIDER_NPI']== npi]['FIN'].unique())
        providerObj = {'id':str(id), 'npi':str(npi), 'name':str(name),'size':str(size)}
        provider_array.append(providerObj)

    print(provider_array)
    return json.dumps(provider_array)



def getPatients(npi):
    if npi == '':
        print('no npi')
        return []
    providers = care_teams.loc[care_teams['PROVIDER_NPI'] == npi].sort_values(['DISCH_DT_TM']).copy()
    providers.drop_duplicates(subset=['FIN'], inplace=True)
    provider_array = []
    for ind in providers.index:
        npi = providers['PROVIDER_NPI'][ind]
        fin = providers['FIN'][ind]
        fname = providers['PROVIDER_FIRSTNAME'][ind]
        lname = providers['PROVIDER_LASTNAME'][ind]
        specialty = providers['PROVIDER_SPECIALTY'][ind]
        discharge= providers['DISCH_DT_TM'][ind]
        disp = providers['E_DISCH_DISPOSITION_DISP'][ind]
        prev = providers['PREV_APPT'][ind]
        next = providers['POST_APPT'][ind]
        providerObj = {'id':str(npi),'fin':str(fin), 'npi':str(npi), 'fname':str(fname),'lname':str(lname),
        'specialty':str(specialty),'discharge':str(discharge.strftime("%m/%d/%y")),'disp':str(disp), 'prev':str(prev),
        'next':str(next)}
        provider_array.append(providerObj)
        
    print(provider_array)
    return json.dumps(provider_array)



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

def getNPI(request):
    intNPI = request["NPI"].split('.')[0]
    npi = int(intNPI)
    return npi

def getFirstLetter(request):
    first_letter = str(request["letter"])
    return first_letter

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

@app.route('/providers', methods=['POST'])
def getProviderList():
    print('request', request.json)
    first_letter = getFirstLetter(request.json)
    provider_list = getProviders(first_letter)
    return provider_list, 200

@app.route('/patients', methods=['POST'])
def getPatientList():
    print('request', request.json)
    npi = getNPI(request.json)
    patient_list = getPatients(npi)
    return patient_list, 200

app.run(host='0.0.0.0', port=5000)