'''
TITLE: HAL_TIME
BY:
    Some Guy they call Scooter
    Common Sense Cyber Group

Created: 12/14/2021
Updated: 12/14/2021

Version: 1.0.1

License: MIT

Purpose:
    -This script is a small action script that Hal uses in order to respond to the user when they aks what time it is
    -This script can also take in aother locations (other than the current users location) and find the current time based on that timezone
'''

### IMPORT LIBRARIES ###
import datetime     # - Used for getting current date and time
import logging      # - Used for logging errors in the script
import geopy        # - Used for finding coordinates of location if user asks
from geopy import geocoders     # - Geocoder for doing work on finding coordinates
from timezonefinder import TimezoneFinder   # - Used for mapping coordinates to a timezone
import pytz     # - Used for setting a timezone to search the current time in
import ssl      # - SSL encryption during API call
import sys      # - System related activities
import logging

### DEFINE VARIABLES ###
#Set the SSL context (rather remove TLS)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
geocoders.options.default_ssl_context = ctx

geolocator = geopy.Nominatim(user_agent="hal_time_geoapi")    #Locator to do the work

#Set up logging for user activities
logging_file = "bloody_hal.log"         #Define log file location for windows
logger = logging.getLogger("Hal_Time Log")  #Define log name
logger.setLevel(logging.DEBUG)              #Set logger level
fh = logging.FileHandler(logging_file)      #Set the file handler for the logger
fh.setLevel(logging.DEBUG)                  #Set the file handler log level
logger.addHandler(fh)                       #Add the file handler to logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')   #Format how the log messages will look
fh.setFormatter(formatter)                  #Add the format to the file handler

#Set up logging for user activities
logging_file = "bloody_hal.log"         #Define log file location for windows
logger = logging.getLogger("hal_time Log")  #Define log name
logger.setLevel(logging.DEBUG)              #Set logger level
fh = logging.FileHandler(logging_file)      #Set the file handler for the logger
fh.setLevel(logging.DEBUG)                  #Set the file handler log level
logger.addHandler(fh)                       #Add the file handler to logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')   #Format how the log messages will look
fh.setFormatter(formatter)                  #Add the format to the file handler

### CLASSES AND FUNCTIONS ###
#Function to locate the timezone of the requested location
def get_time(request):
    try:
        #Get the location
        location = geolocator.geocode(request)

        #Get the timezone of location
        req_timezone = TimezoneFinder().timezone_at(lng=location.longitude, lat=location.latitude)
        timezone = pytz.timezone(str(req_timezone))

        #Now get the current time and turn it into a readable output for Hal to speak
        requested_time = f'It is {datetime.datetime.now(timezone).strftime("%I:%M %p")} in {request}.'

        return requested_time

    except:
        logger.critical("Unknown error caused Harold to crash: %s", sys.exc_info())