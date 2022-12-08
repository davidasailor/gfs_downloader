# Python script to download GFS GRIB file from https://nomads.ncep.noaa.gov

# Change these to latest run (00, 06, 12, 18)
RUN = "18"
DATE = "20221208"

# Where to save final grib
#PATH = "Java14/Christmas2022/grib/"
PATH = "grib/"

# Set boundary of GRIB (negative for south and west)
LEFT_BOUNDARY = 84
RIGHT_BOUNDARY = 220
TOP_BOUNDARY = 33
BOTTOM_BOUNDARY = -63

# Extent of days (up to 16)
DAYS = 16

# Variables and altitude levels (see https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl for examples)
# Surface winds are just "10_m_above_ground" and "UGRD:, "VGRD"
LEVELS = ["10_m_above_ground"]
VARIABLES = ["UGRD", "VGRD"]


import errno
import os
from time import sleep
import requests
from urllib.request import urlopen

varstring = ""
for v in  VARIABLES:
    varstring = varstring + "&var_"+ v + "=on"
    
level_string = ""
for l in LEVELS:
    level_string = level_string + "&lev_" + l + "=on"


base_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.tRUNz.pgrb2.0p25.fINCLEVELVARS&subregion=&leftlon="+str(LEFT_BOUNDARY)+"&rightlon="+str(RIGHT_BOUNDARY)+"&toplat="+str(TOP_BOUNDARY)+"&bottomlat="+str(BOTTOM_BOUNDARY)+"&dir=%2Fgfs.DATE%2FRUN%2Fatmos"

base_url = base_url.replace("RUN", RUN)
base_url = base_url.replace("VARS", varstring)
base_url = base_url.replace("LEVEL", level_string)
base_url = base_url.replace("DATE", DATE)

print(base_url)

if not PATH.endswith("/"):
    PATH = PATH + "/"
    
if not os.path.exists(os.path.dirname(PATH)):
    try:
        os.makedirs(os.path.dirname(PATH))
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

filename = PATH + "noaa_gfs_" + DATE + RUN + ".grib2"

hours = 0

blob = b''

while(hours <= DAYS*24):
    print("Getting forecast hour " + str(hours))
    url = base_url.replace("INC", str(hours).zfill(3))
    if(hours < 120):
        hours = hours + 1
    else:
        hours = hours + 3
    #print(url)
    try:
        with urlopen(url) as new_increment:
            blob = blob + new_increment.read()
    except IOError as err:
        print("Error on hour " + str(hours-1) + "; Pausing 10 seconds to try again")
        sleep(10)
        try:
            with urlopen(url) as new_increment:
                blob = blob + new_increment.read()
        except IOError as err:
            break
            
with open (filename, 'wb') as output:
    output.write(blob)

print("Saved " + str(hours-1) + " hours of data as " + filename)
