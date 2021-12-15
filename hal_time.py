'''
First pull out the requested location of where we need to find the time

Second find the geolocation of the requested place and match it to a timezone

Third get the time in that timezone and send it back as the response

'''

### IMPORT LIBRARIES ###
import datetime
import logging
import geopy
from geopy import geocoders
from timezonefinder import TimezoneFinder
import pytz
import ssl

### DEFINE VARIABLES ###
#Set the SSL context (rather remove TLS)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
geocoders.options.default_ssl_context = ctx

geolocator = geopy.Nominatim(user_agent="hal_time_geoapi")    #Locator to do the work

### CLASSES AND FUNCTIONS ###
#Function to locate the timezone of the requested location
def get_time(request):
    #Get the location
    location = geolocator.geocode(request)

    #Get the timezone of location
    req_timezone = TimezoneFinder().timezone_at(lng=location.longitude, lat=location.latitude)
    timezone = pytz.timezone(str(req_timezone))

    #Now get the current time and turn it into a readable output for Hal to speak
    requested_time = f'It is {datetime.datetime.now(timezone).strftime("%I:%M %p")} in {request}.'

    return requested_time

### THE THING ###
#This is for stand-alone testing as the get_time function will be called exclusively from the bloody_hal script.
if __name__ == '__main__':
    time_output = get_time("Baltimore")

    print(time_output)