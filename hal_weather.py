'''
TITLE: HAL_WEATHER
BY:
    Some Guy they call Scooter
    Common Sense Cyber Group

Created: 12/17/2021
Updated: 12/17/2021

Version: 1.0.1

License: MIT

Purpose:
    -This script is used for getting weather data from any given location that the user asks for
    -This script will be called from the main Bloody_Hal script as a function/class call
'''

### IMPORT LIBRARIES ###
import python_weather   # - Used to get the weather from MSN using an API call, returns json format
import asyncio  # - Used for looping function
import logging  # - Used for logging script errors to main Hal log file
import sys  # - Used for system related things and error catching

### DEFINE VARIABLES ###
#Set up logging for user activities
logging_file = "bloody_hal.log"         #Define log file location for windows
logger = logging.getLogger("Hal_Weather Log")  #Define log name
logger.setLevel(logging.DEBUG)              #Set logger level
fh = logging.FileHandler(logging_file)      #Set the file handler for the logger
fh.setLevel(logging.DEBUG)                  #Set the file handler log level
logger.addHandler(fh)                       #Add the file handler to logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')   #Format how the log messages will look
fh.setFormatter(formatter)                  #Add the format to the file handler

### CLASSES AND FUNCTIONS ###
class get_weather():
    def __init__(self, location):
        #Create a loop with the function
        loop = asyncio.get_event_loop()

        #Run the loop until we get all of the weather data
        weather_response = loop.run_until_complete(self.getweather(location))

        #Return weather data to bloody_hal
        return weather_response

    async def getweather(local):
        try:
            #Create client and change values to metric/F
            client = python_weather.Client(format=python_weather.IMPERIAL)

            #Get the weather from the desireed location
            weather = await client.find(local)

            #Close the client once finished
            await client.close()

            #Return the weather json mess for the Main Hal script to parse through and return depending on what the user asked
            return weather

        except:
            logger.critical("Unable to get weather data: %s", sys.exc_info())
            return "An error occurred while trying to fetch the weather data."

'''
EXAMPLE JSON RESPONSE
{"location": "Washington, DC", 
    "coordinates": "38.892, -77.02", 
    "provider": "Foreca", 
    "temperature": "14 �C", 
    "feels like": "14 �C", 
    "sky text": "Cloudy", "humidity": "74%", 
    "wind speeds": "6 km/h", 
    "date": "Friday, 17 December 2021 at 08:30:00 (UTC-4)", 
    "url": "http://a.msn.com/54/en-US/ct38.892,-77.02?ctsrc=outlook", 
    
    "forecasts": {
        "Thursday, 16 December 2021 at 00:00:00 (UTC-4)": {"lowest temperature": "13 �C", "highest temperature": "18 �C", "sky text": "Mostly Cloudy", "precipitation": "unknown"}, 
        "Friday, 17 December 2021 at 00:00:00 (UTC-4)": {"lowest temperature": "8 �C", "highest temperature": "16 �C", "sky text": "Mostly Cloudy", "precipitation": "40%"}, 
        "Saturday, 18 December 2021 at 00:00:00 (UTC-4)": {"lowest temperature": "5 �C", "highest temperature": "16 �C", "sky text": "Cloudy", "precipitation": "70%"}, 
        "Sunday, 19 December 2021 at 00:00:00 (UTC-4)": {"lowest temperature": "0 �C", "highest temperature": "15 �C", "sky text": "Sunny", "precipitation": "80%"}, 
        "Monday, 20 December 2021 at 00:00:00 (UTC-4)": {"lowest temperature": "1 �C", "highest temperature": "6 �C", "sky text": "Sunny", "precipitation": "unknown"}}}
'''