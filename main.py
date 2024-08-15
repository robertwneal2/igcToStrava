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
# gpsBabelCmd = f"gpsbabel -i igc -f {igc_filename} -o gpx -F {gpx_filename}"
call(['gpsbabel', '-i', 'igc', '-f', igc_filename, '-o', 'gpx', '-F', gpx_filename])
