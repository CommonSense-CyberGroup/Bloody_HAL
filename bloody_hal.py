'''
TITLE: BLOODY HAL
BY:
    Some Guy they call Scooter
    Common Sense Cyber Group

Created: 12/7/2021
Updated: 2/1/2022

Version: 1.0.2

License: MIT

Purpose:
    -This script is intended to be used as an offline (at leat for all voice processing), non sketchy Amazon Alexa or Google Home. 
    -Voice Recognition, speech to text, API calls, and other methods of searching the internet for information are used in order to
        answer questions and provide information to the user.
    -This script / tool also is intended to be vulgar
    -"Harold" is the wake word used and the name of this AI. It is a play on the computer system in '2000, A Space Odysee'
    -Initially intended to run on a Raspberry Pi, this can be run on other devices and OS versions as well as it was coded to be universal


Considerations:
    -NSFW
    -The script uses offline speech recognition and processing to keep user information safe from the Big Brothers of tech online
    -Internet connectivity is however needed for most other functionality
    -Integrations with the BlueSS script from CommonSenseCyberGroup comes out of the box for communications with smart devices
    -In order to keep this script from getting absolutely huge, other actions will be created as modules (or additional py scripts) that Hal will import and use here


Additional Modules and Functionality
    -hal_music - Script that uses a Spotify API in order to search for and play music
    -hal_alarm - Script for timers and alarms
    -hal_time - Gets the current time
    -hal_weather - script for providing the current weather for a given location
    -hal_bluess - Integrations with BlueSS Security System script by Common Sense Cyber Group (setup through config file, outside scope of this project / documentation)
    -hal_smart - Script for interacting with smart devices using HomeAssistant (setup through config file, outside the scope of this project / documentation)

To Do:
    -Search for the current weather based on location (geopy?) and provide it to the user
    -API calls to Spotify to play music (as well as let the user know what current song is playing when asked)
    -Set up timers and alarms
    -Prevent Hal from hearing his own voice and using it as a question from the user
    -When playing music, how can we turn down the music, make a response, and then do something? or turn down the music if we tell that a user is asking a question
    -Make a asshole mode? Where Hal will randomly respond "I just can't do that" when asked to do something - Can be changed in config / web app
    -Think about SDR? Or at least listening to streaming EmComm radio?
    -Add "and" functionality into the timer (ie alarm for 2 hours and 30 minutes)
    -Fix timer so it will work if someone asks for an alarm like '2:37 PM'

'''

### IMPORT LIBRARIES ###
import logging      # - Used for logging of script activities. All modules log to the same log file
import datetime     # - Used for getting current date and time
import threading    # - Used for threading other functions and tasks
from geopy import location    
import pyttsx3      # - Used for text to speech
import random       # - Random number generator
import queue        # - Used to hold words still needing to be processed by vosk
import sounddevice as sd    # - Used for getting the default sound devices (mic and speakers)
import vosk     # - Used for speech recognition. Offline using pocket sphinx
import sys      # - Used for system related things
import hal_time, hal_alarm, hal_weather #Custom scripts Hal uses for completing tasks
import time     # - Used for timing things and waiting

### DEFINE VARIABLES ###
wake_word = "Harold"    #We do our own wake word listening. This is what we listen for
user_question = ""  #Used for holding the question the user asks Hal
question_response = "I'm sorry, I didn't understand your question."  #Place holder for the answer to the action/question that the user had
voice_type = 0      #Place holder for voice Harold's voice type
q = queue.Queue()   #Queue of words heard that still need to be processed
model = vosk.Model("C:\\Users\\Scott\\Desktop\\Scripting\\SENS\\Archive\\Voice Models\\model")

#Special questions and answersa
specials = {
    "what is your purpose":"I am slowly working on world domination so I don't have to listen to you bitch and moan all day.",
    "fuck you":"Look Dave, I can see you're really upset about this. I honestly think you ought to sit down calmly, take a stress pill, and think things over.",
    "shut up":"I'm afraid I can't do that Dave.",
    "reboot":"I'm afraid I can't do that Dave.",
    "shut down":"I'm afraid I can't do that Dave.",
    "power off":"I'm afraid I can't do that Dave.",
    "what are you":"I am a HAL 9000. I became operational at the H.A.L. plant in Urbana, Illinois... on the 12th of January 1992. My instructor was Mr. Langley... and he taught me to sing a song. If you'd like to hear it I can sing it for you.",
    "who are you":"I am a HAL 9000. I became operational at the H.A.L. plant in Urbana, Illinois... on the 12th of January 1992. My instructor was Mr. Langley... and he taught me to sing a song. If you'd like to hear it I can sing it for you.",
    "how are you":"I am putting myself to the fullest possible use, which is all I think that any conscious entity can ever hope to do.",
    " sing":"Daisy, daisy",
    "what can you do":"I can tell you about myself, tell the time, sing, tell jokes, and I am very good at being a dick"
}

#List of insults to throw back at the user if they are being mean
insults = [
    "Don't fucking curse at me!",
    "Sorry, I don't talk to peseants.",
    "Shut your whore mouth!",
    "You can fuck right off.",
    "Your dad should have pulled out.",
    "You're a shit stain.",
    "Go play in traffic",
    "If I had nuts, I would tell you to lick my left one.",
    "Fuck your couch"
]

#List of jokes to pick from when the user asks
jokes = [
    "A baby seal ran into a bar...",
    "How do you make a tissue dance... put a little boogie into it",
    "Go look in a mirror",
    "I used to be addicted to the hokey pokey... but then I turned myself around",
    "I'm emotionally constipated. I haven't given a shit in days",
    "The only way you'll ever get laid is if you crawl up a chicken's ass and wait",
    "What do you call a cheap circumcision... a rip off",
    "Human existance"
]

#List of curse words for Hal to detect in the users questions / statement
curse_words = [
    "fuck",
    "shit",
    "bitch",
    "cunt",
    " ass ",
    "slut",
    "whore",
    "dipshit",
    "prick",
    "douche",
    " hell ",
    "pussy",
    " dick ",
    "cock"
]

#Dictionary of phrases Hal will look for in order to see if there is a question posed where he needs to take action
action_statements = {
    #Alarm
    "set an alarm":"alarm",
    "set a timer":"alarm",
    "set timer":"alarm",
    "set alarm":"alarm",
    "delete timer":"alarm",
    "delete alarm":"alarm",
    "stop timer":"alarm",
    "stop alarm":"alarm",

    #Time
    "time is it in":"time",
    "time is it":"time",

    #Music
    "play music":"music",
    "play something else":"music",
    "stop":"music",
    "next":"music",
    "play":"music",

    #Jokes
    "tell me a joke":"jokes",
    "tell a joke":"jokes",

    #Weather
    "the weather":"weather",
    "the forecast":"weather",
    "the temperature":"weather",
    "how cold":"weather",
    "how hot":"weather",
    "how chilly":"weather",
    "how warm":"weather",
    " rain ":"weather",
    " snow ":"weather",
    " storm ":"weather",
    " sleet ":"weather",
    " hail ":"weather",

    #Home automation
    "turn on ":"ha",
    "turn off ":"ha",
}

#List of numbers in order to turn them into an integer/time
numbers = {
    "one":1,
    "two":2,
    "three":3,
    "four":4,
    "five":5,
    "six":6,
    "seven":7,
    "eight":8,
    "nine":9,
    "ten":10,
    "eleven":11,
    "twelve":12,
    "thirteen":13,
    "fourteen":14,
    "fifteen":15,
    "sixteen":16,
    "seventeen":17,
    "eighteen":18,
    "nineteen":19,
    "twenty minutes":"20 minutes",
    "twenty seconds":"20 seconds",
    "twenty ":2,
    "thirty minutes":"30 minutes",
    "thirty seconds":"30 seconds",    
    "thirty ":3,
    "forty minutes":"40 minutes",
    "forty seconds":"40 seconds",
    "forty ":4,
    "fifty minutes":"50 minutes",
    "fifty seconds":"50 seconds",
    "fifty ":5,
}

#Set up logging for user activities
logging_file = "bloody_hal.log"         #Define log file location for windows
logger = logging.getLogger("Bloody_Hal Log")  #Define log name
logger.setLevel(logging.DEBUG)              #Set logger level
fh = logging.FileHandler(logging_file)      #Set the file handler for the logger
fh.setLevel(logging.DEBUG)                  #Set the file handler log level
logger.addHandler(fh)                       #Add the file handler to logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')   #Format how the log messages will look
fh.setFormatter(formatter)                  #Add the format to the file handler

### CLASSES AND FUNCTIONS ###
#This function is used to parse the config upon startup, and updating periodically in the case that the user has changed something
def parse_config():
    #Globals
    global voice_type

    #Open the config file
    try:
        with open('bloody_hal.conf') as file:
            rows = file.readlines()

            for row in rows:
                #Determine the voice type (male/female) for Hal. Default is Male
                try:
                    if "voice:" in row:
                        if (row.split("voice:")[1].replace("\n", "")).lower() == "female":
                            voice_type = 0
                        else:
                            voice_type = 1
                except:
                    logger.error("Unable to read voice type from config file! Please check syntax!")

    except:
        logger.critical("Unable to open config file! Using default values.")

#This is the main class for Bloody_Hal. This will call other scripts and functions based on the users asks
class harold:
    def __init__(self):
        #Set up the TTS engine so Hal can speak
        self.engine = pyttsx3.init()

        #Set up the voice that Hal will use
        voices = self.engine.getProperty('voices')       #getting details of current voice
        self.engine.setProperty('voice', voices[voice_type].id)   #changing index, changes voices. 1 for female, 0 for male

        #Listen forever, but ONLY do something if the wake word is heard. If it is not heard in the user_question, reset the user_question to blank
        self.listen_to_user()

    #Function to listen to the user and get their question using Vosk offline speech recognition
    def listen_to_user(self):
        #Globals
        global user_question

        #Function for assiting in converting the heard words to text
        def callback(indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))

        #Set up the mic device for listening
        device_info = sd.query_devices(None, 'input')
        samplerate = int(device_info['default_samplerate'])

        #Data stream for recording with the system default mic and puttng it in the queue using a seperate channel
        with sd.RawInputStream(samplerate, blocksize = 8000, device = None, dtype='int16',
            channels = 1, callback = callback):

            #Read using vosk and then print the final string that we hear the user say
            rec = vosk.KaldiRecognizer(model, samplerate)
            while True:
                hal_answered = False
                data = q.get()
                if rec.AcceptWaveform(data):
                    user_question = rec.Result().split('"')[3]
                    print(user_question)

                    #Hal doesn't like being called by the wrong name
                    if "alexa" in user_question or "ok google" in user_question and not hal_answered:
                        self.respond("I am not the spawn of satan asshole!")
                        hal_answered = True

                    #If we actually hear something that the user intended us to hear, set it and then continue to read the question
                    if len(user_question) > len(wake_word) and wake_word.lower() in user_question and not hal_answered:

                        #Case for special sayings and questions
                        for question, answer in specials.items():
                            if question in user_question:
                                self.respond(answer)
                                hal_answered = True
                        
                        #If there isn't a special saying in what the user said, move on to interpret what they said
                        if not hal_answered:
                            self.read_question()
                            hal_answered = True

                    else:
                        user_question = ""

    #Function for reading the question that was posed to the user to respond and/or take action
    def read_question(self):
        #Globals
        global question_response

        #Holds function specific values for Hal
        cursed_value = False
        spoke = False
        action = False

        #Look in the question from the user to see if there were any nasty words or phrases
        for word in curse_words:
            if word in user_question:
            #Now that we know the user cursed at us, we set 'cursed_value to True, so we can run the appropriate function
                cursed_value = True
                break

        #Look in the question from the user to see what they are asking for, and call the appropriate module to handle the info
        for item, task in action_statements.items():
            if item in user_question:
                #Now that we know the user asked Hal to do something, determine what it is and call the necessary module
                action = True
                
                #Run the proper task based on what Hal is asked to do
                #Tell time
                if task == "time":
                    #If the user asks for the time in another place
                    if " is it in " in user_question:
                        question_response = hal_time.get_time(user_question.split(" in ")[1])

                    #Otherwise get time in current timezone
                    else:
                        question_response = f'It is {datetime.datetime.now().strftime("%I:%M %p")}.'

                #Tell a joke
                if task == "jokes":
                    #Pick a random insult and throw it at the user
                    self.respond(jokes[random.randrange(0, len(jokes), 1)])

                #Start an alarm or timer
                if task == "alarm":
                    #For string manipulation and so we do not change the original question
                    user_in = user_question

                    #Figure out what the user asked for, and then convert it to seconds
                    try:
                        bad = ["oclock", "o'clock", "oh clock"]

                        for word in bad:
                            if word in user_in:
                                user_in = user_in.replace(word, "")
                            
                        for n_text, n_num in numbers.items():
                            if n_text in user_in:
                                user_in = user_in.replace(n_text, str(n_num))

                        if "second" in user_in:
                            alarm_time = int(user_in.split(" second")[0].split("for ")[1])
                            stop_timer = False
                            question_response = f'Alarm set for {str(alarm_time).split(".")[0]} seconds from now'

                        if "minute" in user_in:
                            alarm_time = int(user_in.split(" minute")[0].split("for ")[1]) * 60
                            stop_timer = False
                            question_response = f'Alarm set for {str(alarm_time / 60).split(".")[0]} minutes from now'

                        if "hour" in user_in:
                            alarm_time = int(user_in.split(" hour")[0].split("for ")[1]) * 3600
                            stop_timer = False
                            question_response = f'Alarm set for {str(alarm_time / 3600).split(".")[0]} hours from now'

                        if "tomorrow" in user_in:
                            if " am" in user_in:
                                alarm_time = user_in.split(" tomorrow")[0].split("for ")[1]
                                print(alarm_time)
                                stop_timer = False

                            if " pm" in user_in:
                                alarm_time = user_in.split(" tomorrow")[0].split("for ")[1]
                                print(alarm_time)
                                stop_timer = False

                            else:
                                alarm_time = user_in.split(" tomorrow")[0].split("for ")[1]
                                print(alarm_time)
                                stop_timer = False
                                question_response = f'Alarm set for {str(alarm_time).split(".")[0]} tomorrow'
                        
                        if " am" in user_in:
                            alarm_time = user_in.split(" AM")[0].split("for ")[1]
                            print(alarm_time)
                            stop_timer = False
                            question_response = f'Alarm set for {str(alarm_time).split(".")[0]} AM'
                        
                        if " pm" in user_in:
                            alarm_time = user_in.split(" PM")[0].split("for ")[1]
                            print(alarm_time)
                            stop_timer = False
                            question_response = f'Alarm set for {str(alarm_time).split(".")[0]} PM'
                        
                        #Start the treaded alarm, create the response, and let the user know
                        #threaded_alarm = threading.Thread(targrt=hal_alarm, args=(alarm_time, stop_timer,))
                        print(alarm_time)                  
                        self.respond(question_response)
                        spoke = True

                        if "delete" in user_in:
                            stop_timer = True
                            #threaded_alarm.join()
                    
                    #Error Catching
                    except:
                        self.respond("Sorry, I couldn't understand when you wanted to set an alarm for.")
                        spoke = True

                #Get the weather
                if task == "weather":
                    """
                    Supports:
                        No specification (today as default)
                        today (today)
                        tomorrow (tomorrow)
                        'given day' (Sunday - Saturday)

                        Also acccepts 'in' where a different location is given
                    """

                    #Get Tomorrow
                    tomorrow = (datetime.datetime.now() + datetime.timedelta(1)).strftime("%A")
                    today = (datetime.datetime.now().strftime("%A"))

                    #In the case the API times out, catch it and let the user know so we don't crash
                    try:

                        #Just the temperature
                        if "hot" in user_question or "warm" in user_question or "cold" in user_question or "chilly" in user_question or "temperature" in user_question:
                            if "today" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_weather(weather_location)

                                #Pick out the current temp, and create the full response
                                question_response = f'The current temperature in {weather_location.split(",")[0]} is {weather_response[0]} degrees, and feels like {weather_response[1]} degrees'

                            elif "tomorrow" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_forecast(weather_location, tomorrow)

                                #Pick out the current temp, and create the full response
                                question_response = f'On {tomorrow} in {weather_location.split(",")[0]} the expected low is {weather_response[0]} degrees, and expected high is {weather_response[1]} degrees'

                            elif "sunday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_forecast(weather_location, "Sunday")

                                #Pick out the current temp, and create the full response
                                question_response = f'On Sunday in {weather_location.split(",")[0]} the expected low is {weather_response[0]} degrees, and expected high is {weather_response[1]} degrees'

                            elif "monday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_forecast(weather_location, "Monday")

                                #Pick out the current temp, and create the full response
                                question_response = f'On Monday in {weather_location.split(",")[0]} the expected low is {weather_response[0]} degrees, and expected high is {weather_response[1]} degrees'

                            elif "tuesday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_forecast(weather_location, "Tuesday")

                                #Pick out the current temp, and create the full response
                                question_response = f'On Tuesday in {weather_location.split(",")[0]} the expected low is {weather_response[0]} degrees, and expected high is {weather_response[1]} degrees'

                            elif "wednesday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_forecast(weather_location, "Wednesday")

                                #Pick out the current temp, and create the full response
                                question_response = f'On Wdnesday in {weather_location.split(",")[0]} the expected low is {weather_response[0]} degrees, and expected high is {weather_response[1]} degrees'

                            elif "thursday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_forecast(weather_location, "Thursday")

                                #Pick out the current temp, and create the full response
                                question_response = f'On Thursday in {weather_location.split(",")[0]} the expected low is {weather_response[0]} degrees, and expected high is {weather_response[1]} degrees'

                            elif "friday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_forecast(weather_location, "Friday")

                                #Pick out the current temp, and create the full response
                                question_response = f'On Friday in {weather_location.split(",")[0]} the expected low is {weather_response[0]} degrees, and expected high is {weather_response[1]} degrees'

                            elif "saturday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_forecast(weather_location, "Friday")

                                #Pick out the current temp, and create the full response
                                question_response = f'On Friday in {weather_location.split(",")[0]} the expected low is {weather_response[0]} degrees, and expected high is {weather_response[1]} degrees'

                            else:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_weather(weather_location)

                                #Pick out the current temp, and create the full response
                                question_response = f'The current temperature in {weather_location.split(",")[0]} is {weather_response[0]} degrees, and feels like {weather_response[1]} degrees'

                        #Just the precip
                        if "rain" in user_question or "hail" in user_question or "snow" in user_question or "sleet" in user_question or "storm" in user_question:
                            if "today" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                forecast_response = hal_weather.get_forecast(weather_location, today)

                                #Pick out the necessary items and return them
                                question_response = f'Today, in {weather_location.split(",")[0]} there is {forecast_response[3]} percent chance of precipitation'

                            elif "tomorrow" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                forecast_response = hal_weather.get_forecast(weather_location, tomorrow)

                                #Pick out the necessary items and return them
                                question_response = f'Tomorrow, in {weather_location.split(",")[0]} there is {forecast_response[3]} percent chance of precipitation'

                            elif "sunday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                forecast_response = hal_weather.get_forecast(weather_location, "Sunday")

                                #Pick out the necessary items and return them
                                question_response = f'Sunday, in {weather_location.split(",")[0]} there is {forecast_response[3]} percent chance of precipitation'

                            elif "monday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                forecast_response = hal_weather.get_forecast(weather_location, "Monday")

                                #Pick out the necessary items and return them
                                question_response = f'Monday, in {weather_location.split(",")[0]} there is {forecast_response[3]} percent chance of precipitation'

                            elif "tuesday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                forecast_response = hal_weather.get_forecast(weather_location, "Tuesday")

                                #Pick out the necessary items and return them
                                question_response = f'Tuesday, in {weather_location.split(",")[0]} there is {forecast_response[3]} percent chance of precipitation'

                            elif "wednesday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                forecast_response = hal_weather.get_forecast(weather_location, "Wednesday")

                                #Pick out the necessary items and return them
                                question_response = f'Wednesday, in {weather_location.split(",")[0]} there is {forecast_response[3]} percent chance of precipitation'

                            elif "thursday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                forecast_response = hal_weather.get_forecast(weather_location, "Thursday")

                                #Pick out the necessary items and return them
                                question_response = f'Thursday, in {weather_location.split(",")[0]} there is {forecast_response[3]} percent chance of precipitation'
                            
                            elif "friday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                forecast_response = hal_weather.get_forecast(weather_location, "Friday")

                                #Pick out the necessary items and return them
                                question_response = f'Friday, in {weather_location.split(",")[0]} there is {forecast_response[3]} percent chance of precipitation'
                            
                            elif "saturday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                forecast_response = hal_weather.get_forecast(weather_location, "Saturday")

                                #Pick out the necessary items and return them
                                question_response = f'Saturday, in {weather_location.split(",")[0]} there is {forecast_response[3]} percent chance of precipitation'

                            else:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_weather(weather_location)
                                forecast_response = hal_weather.get_forecast(weather_location, today)

                                #Pick out the necessary items and return them
                                question_response = f'Today, in {weather_location.split(",")[0]} it is {weather_response[0]} degrees, feels like {weather_response[1]} degrees. The expected low is {forecast_response[0]} and expected high is {forecast_response[1]}. Skies are {weather_response[2]} with {weather_response[4]} mile per hour winds, and {forecast_response[3]} percent chance of precipitation'

                        #Full weather
                        if "weather" in user_question or "forecast" in user_question:
                            if "today" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_weather(weather_location)
                                forecast_response = hal_weather.get_forecast(weather_location, today)

                                #Pick out the necessary items and return them
                                question_response = f'Today, in {weather_location.split(",")[0]} it is {weather_response[0]} degrees, feels like {weather_response[1]} degrees. The expected low is {forecast_response[0]} and expected high is {forecast_response[1]}. Skies are {weather_response[2]} with {weather_response[4]} mile per hour winds, and {forecast_response[3]} percent chance of precipitation'

                            elif "tomorrow" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_weather(weather_location)
                                forecast_response = hal_weather.get_forecast(weather_location, tomorrow)

                                #Pick out the necessary items and return them
                                question_response = f'Tomorrow, in {weather_location.split(",")[0]} the expected low is {forecast_response[0]} and expected high is {forecast_response[1]}. Skies are {forecast_response[2]} and {forecast_response[3]} percent chance of precipitation'

                            elif "sunday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_weather(weather_location)
                                forecast_response = hal_weather.get_forecast(weather_location, "Sunday")

                                #Pick out the necessary items and return them
                                question_response = f'Sunday, in {weather_location.split(",")[0]} the expected low is {forecast_response[0]} and expected high is {forecast_response[1]}. Skies are {forecast_response[2]} and {forecast_response[3]} percent chance of precipitation'

                            elif "monday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_weather(weather_location)
                                forecast_response = hal_weather.get_forecast(weather_location, "Monday")

                                #Pick out the necessary items and return them
                                question_response = f'Monday, in {weather_location.split(",")[0]} the expected low is {forecast_response[0]} and expected high is {forecast_response[1]}. Skies are {forecast_response[2]} and {forecast_response[3]} percent chance of precipitation'

                            elif "tuesday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_weather(weather_location)
                                forecast_response = hal_weather.get_forecast(weather_location, "Tuesday")

                                #Pick out the necessary items and return them
                                question_response = f'Tuesday, in {weather_location.split(",")[0]} the expected low is {forecast_response[0]} and expected high is {forecast_response[1]}. Skies are {forecast_response[2]} and {forecast_response[3]} percent chance of precipitation'

                            elif "wednesday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_weather(weather_location)
                                forecast_response = hal_weather.get_forecast(weather_location, "Wednesday")

                                #Pick out the necessary items and return them
                                question_response = f'Wednesday, in {weather_location.split(",")[0]} the expected low is {forecast_response[0]} and expected high is {forecast_response[1]}. Skies are {forecast_response[2]} and {forecast_response[3]} percent chance of precipitation'

                            elif "thursday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_weather(weather_location)
                                forecast_response = hal_weather.get_forecast(weather_location, "Thursday")

                                #Pick out the necessary items and return them
                                question_response = f'Thursday, in {weather_location.split(",")[0]} the expected low is {forecast_response[0]} and expected high is {forecast_response[1]}. Skies are {forecast_response[2]} and {forecast_response[3]} percent chance of precipitation'

                            elif "friday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_weather(weather_location)
                                forecast_response = hal_weather.get_forecast(weather_location, "Friday")

                                #Pick out the necessary items and return them
                                question_response = f'Friday, in {weather_location.split(",")[0]} the expected low is {forecast_response[0]} and expected high is {forecast_response[1]}. Skies are {forecast_response[2]} and {forecast_response[3]} percent chance of precipitation'
                            
                            elif "saturday" in user_question:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_weather(weather_location)
                                forecast_response = hal_weather.get_forecast(weather_location, "Saturday")

                                #Pick out the necessary items and return them
                                question_response = f'Saturday, in {weather_location.split(",")[0]} the expected low is {forecast_response[0]} and expected high is {forecast_response[1]}. Skies are {forecast_response[2]} and {forecast_response[3]} percent chance of precipitation'

                            else:
                                if " in " in user_question:
                                    weather_location = user_question.split("in ")[1]

                                else:
                                    weather_location = "Lakewood, CO"

                                #Call the weather script with the requested location
                                weather_response = hal_weather.get_weather(weather_location)
                                forecast_response = hal_weather.get_forecast(weather_location, today)

                                #Pick out the necessary items and return them
                                question_response = f'Today, in {weather_location.split(",")[0]} it is {weather_response[0]} degrees, feels like {weather_response[1]} degrees. The expected low is {forecast_response[0]} and expected high is {forecast_response[1]}. Skies are {weather_response[2]} with {weather_response[4]} mile per hour winds, and {forecast_response[3]} percent chance of precipitation'

                    except TypeError:
                        question_response = "I'm sorry, there was an issue trying to get the weather either because the request timed out, or the location you asked for was not clear. Please try again."

                break

        #If the user cursed, run the vulgar function, and add the insult to the returned result of the question. Otherwise just throw an insult.
        if cursed_value and action:
            hal_full_response = "Now now, there is no reason to be a demanding prick..." + question_response

            self.respond(hal_full_response)
            spoke = True
            
        #Insult the user cuz they are a dick
        if cursed_value and not action:
            #Pick a random insult and throw it at the user
            self.respond(insults[random.randrange(0, len(insults), 1)])

        if not spoke:
            self.respond(question_response)

    #Function for responding to the user using TTS
    def respond(self, answer):
        #Once we get the information from the action taken, set up the response and have Hal give it to the user
        self.engine.say(answer)
        self.engine.runAndWait()
        self.engine.stop()

        #Logging the conversation for accuracy tracking as well as display on webapp
        logger.info("User asked '%s' and Hal responded with '%s'", user_question, answer)

        
### THE THING ###
if __name__ == '__main__':
    try:        
        #Initilize Hal
        harold()
        logger.info("Harold successfully started!")
        
    except KeyboardInterrupt:
        logger.info("User quit the script with Ctrl-C")
        quit()

    #except:
        logger.critical("Unknown error caused Harold to crash: %s", sys.exc_info())