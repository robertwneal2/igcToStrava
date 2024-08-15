#  Takes an IGC file from paragliding, uses GPSBabel (must be installed https://www.gpsbabel.org/download.html) to
#  convert IGC to GPX, then posts it to Strava

import tkinter as tk
from tkinter import filedialog
from subprocess import call

#  Select IGC file and create new GPX file name
root = tk.Tk()
root.withdraw()
igc_file_path = filedialog.askopenfilename()
last_slash_index = igc_file_path.rfind('/')
last_dot_index = igc_file_path.rfind('.')
filename = igc_file_path[last_slash_index+1:last_dot_index]
igc_filename = filename + '.IGC'
gpx_filename = filename + '.gpx'

#  Run gpsBabel command
call(['gpsbabel', '-i', 'igc', '-f', igc_filename, '-o', 'gpx', '-F', gpx_filename])

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

