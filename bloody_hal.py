'''
TITLE: BLOODY HAL
BY:
    Some Guy they call Scooter
    Common Sense Cyber Group

Created: 12/7/2021
Updated: 12/13/2021

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
    -hal_timer - Script for timers and alarms
    -hal_weather - script for providing the current weather for a given location
    -hal_bluess - Integrations with BlueSS Security System script by Common Sense Cyber Group (setup through config file, outside scope of this project / documentation)
    -hal_smart - Script for interacting with smart devices using HomeAssistant (setup through config file, outside the scope of this project / documentation)

To Do:
    -Search for the current weather based on location (?) and provide it to the user
    -API calls to Spotify to play music (as well as let the user know what current song is playing when asked)
    -Set up timers and alarms
    -Prevent Hal from hearing his own voice and using it as a question from the user

'''

### IMPORT LIBRARIES ###
import subprocess
import logging
#import speech_recognition as sr
import threading
import pyttsx3
import random
import queue
import sounddevice as sd
import vosk
import sys

### DEFINE VARIABLES ###
wake_word = "Harold"    #We do our own wake word listening. This is what we listen for
vulgar = True   #Variable that makes Hal vulgar
user_question = ""  #Used for holding the question the user asks Hal
hal_full_response = ""  #Place holder var for the response Hal will speak back to the user
question_response = "I'm sorry, I didn't understand your question."  #Place holder for the answer to the action/question that the user had
cursed_value = False    #Holds bool value for if the user cursed at Hal or not in their question/response
voice_type = 0      #Place holder for voice Harold's voice type
q = queue.Queue()   #Queue of words heard that still need to be processed
model = vosk.Model("C:\\Users\\Scott\\Desktop\\Scripting\\SENS\\Archive\\Voice Models\\model")

#List of insults to throw back at the user if they are being mean
insults = [
    "Don't fucking curse at me!",
    "Sorry, I don't talk to peseants.",
    "Shut your whore mouth!",
    "You can fuck right off.",
    "Your dad should have pulled out.",
    "You're a shit stain."
]

#List of curse words for Hal to detect in the users questions / statement
curse_words = [
    "fuck",
    "shit",
    "bitch",
    "cunt",
    "ass",
    "slut",
    "whore",
    "dipshit",
    "prick",
    "douche"
]

#List of phrases Hal will look for in order to see if there is a question posed where he needs to take action
actions = [
    #Time
    "what time is it in",
    "what time is it",

    #Music
    "play music",
    "play something else",
    "stop",
    "next",

    #Jokes
    "tell me a dirty joke",
    "tell me a joke",

    #Weather
    "what is the weather in",
    "what is the weather like in",
    "how cold is it in", 
    "how cold is it out",

    #Home automation
    "turn on",
    "turn off",
    ""

    #Bad
    "Alexa",
    "Shut up"
]

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
        logger.critical("Unable to open config file!")

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
            """This is called (from a separate thread) for each audio block."""
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
                data = q.get()
                if rec.AcceptWaveform(data):
                    user_question = rec.Result().split('"')[3]

                    #If we actually hear something that the user intended us to hear, set it and then continue to read the question
                    print(user_question)
                    if len(user_question) > 0 and wake_word.lower() in user_question:
                        self.read_question()
                        pass

                    if len(user_question) > 0 and "alexa" in user_question:
                        self.respond("I don't respond to the name of the devil's creation")
                        pass

                    if len(user_question) > 0 and "ok google" in user_question:
                        self.respond("I don't respond to the name of the devil's creation")
                        pass

                    else:
                        user_question = ""

    #Function for reading the question that was posed to the user to respond and/or take action
    def read_question(self):
        #Globals
        global cursed_value, question_response, hal_full_response

        #Look in the question from the user to see if there were any nasty words or phrases
        for word in curse_words:
            if word in user_question:
            #Now that we know the user cursed at us, we set 'cursed_value to True, so we can run the appropriate function
                cursed_value = True
                break

        #Look in the question from the user to see what they are asking for, and call the appropriate module to handle the info
        ## HOW ARE WE GONNA KNOW WHAT TO CALL UNLESS WE GO THROUGH A HUGE IF STATEMENT LIST.... 
        action = False
        for item in actions:
            if item in user_question:
                #Now that we know the user asked Hal to do something, determine what it is and call the necessary module
                action = True
                print("found item to do!")
                break

        #If the user cursed, run the vulgar function, and add the insult to the returned result of the question. Otherwise just throw an insult.
        if cursed_value and action:
            hal_full_response = "Now now, there is no reason to be a demanding prick." + question_response

            self.respond(hal_full_response)

        if cursed_value and not action:
            #Pick a random insult and throw it at the user
            self.respond(insults[random.randrange(0, len(insults), 1)])

        else:
            self.respond(question_response)

    #Function for responding to the user using TTS
    def respond(self, response):
        #Once we get the information from the action taken, set up the response and have Hal give it to the user
        self.engine.say(response)
        self.engine.runAndWait()
        self.engine.stop()

        #Logging the conversation for accuracy tracking as well as display on webapp
        logger.info("User asked %s and Hal responded with %s", user_question, hal_full_response)

        
### THE THING ###
if __name__ == '__main__':
    try:        
        #Initilize Hal
        harold()
        logger.info("Harold successfully started!")
        
    except KeyboardInterrupt:
        logger.info("User quit the script with Ctrl-C")
        quit()

    except:
        logger.critical("Unknown error prevented Harold from starting!")