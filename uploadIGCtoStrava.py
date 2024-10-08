#!/usr/bin/env python3

#  Takes an IGC file from paragliding, uses GPSBabel (must be installed https://www.gpsbabel.org/download.html) to
#  convert IGC to GPX, then posts it to Strava

import subprocess
from dotenv import load_dotenv  # pip install python-dotenv
import json
import os
import requests
from subprocess import call

load_dotenv("/home/bert/PycharmProjects/environment_variables/.env")
STRAVA_CLIENT_ID = os.environ['STRAVA_CLIENT_ID']
STRAVA_SECRET = os.environ['STRAVA_SECRET']

#  Select IGC file and create new GPX file name
current_directory = os.getcwd() + '/'
igc_file_path = subprocess.check_output(['zenity', '--file-selection', '--filename', current_directory]).decode('utf-8').strip()  # Open default Ubuntu fle browser, manually browse for and select file
last_slash_index = igc_file_path.rfind('/')
last_dot_index = igc_file_path.rfind('.')
filename = igc_file_path[last_slash_index+1:last_dot_index]  # Get IGC filename without extension
igc_filename = filename + '.IGC'
gpx_filename = filename + '.gpx'

#  Run gpsBabel command
call(['gpsbabel', '-i', 'igc', '-f', igc_filename, '-o', 'gpx', '-F', gpx_filename])  # Convert IGC to GPX with GPSBabel (Must have GPSBabel installed)

#  Edit GPX file to remove pressure altitude values
with open(gpx_filename, 'r') as file:  # Read gpx file and copy to array
    gpx_data = file.readlines()

for idx, line in enumerate(gpx_data):  # Find start and end of pressure altitude values
    if line.find('<trk>') != -1:
        remove_start_idx = idx

    if line.find('</trk>') != -1:
        remove_end_idx = idx
        break

new_gpx_data = []  # Create new array with pressure altitude data removed
for idx, line in enumerate(gpx_data):
    if idx < remove_start_idx or idx > remove_end_idx:
        new_gpx_data.append(line)

with open(gpx_filename, 'w') as file:  # Write new gpx array to file
    file.writelines(new_gpx_data)

#  Upload gpx to Strava
refresh_token_file = 'refresh_token.txt'  # File to store refresh token in
refresh_token_exists = os.path.exists(refresh_token_file)

if refresh_token_exists:  # Check if refresh token exists. If so, use to get response
    with open(refresh_token_file, 'r') as file:  # Grab refresh token
        refresh_token_file_data = file.readlines()
    refresh_token = refresh_token_file_data[0]

    data = {
        'client_id': STRAVA_CLIENT_ID,
        'client_secret': STRAVA_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    response = requests.post('https://www.strava.com/api/v3/oauth/token', data=data)  # Get response with access token

else:  # If no refresh token, authenticate
    authorization_url = f'https://www.strava.com/oauth/authorize?client_id={STRAVA_CLIENT_ID}&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=auto&scope=activity:write'
    print(f'Please go to {authorization_url} and authorize access.')  # Manually open URL in browser and authorize
    authorization_response = input('Enter the full callback URL')  # Manually paste full redirect URL
    code_start_idx = authorization_response.find('code=') + 5
    code_end_idx = authorization_response.find('scope=') - 1
    code = authorization_response[code_start_idx:code_end_idx]

    files = {
        'client_id': (None, STRAVA_CLIENT_ID),
        'client_secret': (None, STRAVA_SECRET),
        'code': (None, code),
        'grant_type': (None, 'authorization_code'),
    }

    response = requests.post('https://www.strava.com/oauth/token', files=files)  # Get response with access token

response_dict = json.loads(response.text)
access_token = response_dict['access_token']  # Get access token from response
refresh_token = response_dict['refresh_token']  # Get refresh token from response
with open("refresh_token.txt", "w") as file:  # Write refresh token to file
    file.write(refresh_token)

name = 'Paragliding'
# description = 'API test'  # Uncomment to add description when posting activity
data_type = 'gpx'
url = 'https://www.strava.com/api/v3/uploads'
gpx_file = open(gpx_filename, 'rb')
sport_type = 'Workout'

headers = {'Authorization': 'Bearer ' + access_token}

files = {
    'sport_type': (None, sport_type),
    'name': (None, name),
    # 'description': (None, description),
    'data_type': (None, data_type),
    'file': gpx_file
}

response = requests.post('https://www.strava.com/api/v3/uploads', headers=headers, files=files)  # Upload activity to Strava

if response.status_code == 201:
    print('Upload successful')
else:
    print('Upload failed:', response.text)
