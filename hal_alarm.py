'''
Alarm questions / conditions the user can ask for:
    -Set an alarm/timer for 6pm
    -Set an alarm/timer tomorrow for 4am
    -set an alarm/timer for 30 minutes
    -set an alarm/timer for 2 hours


First, interpret what the user is asking (today/tomorrow/hours/minutes/time)
Second, find the alarm_time based on the current time (or just for a specific time if need be)
Third, set the alarm time and then thread this function from the main hal script

'''
### IMPORT LIBRARIES ###
import datetime     # - Used for getting current time
import os   # - Used for OS related things
import time # - Used for waiting
import logging  # - Used for logging errors in the script

### DEFINE VARIABLES ###
stop_alarm = False  #Used for stopping the alarm when finished

### CLASSES AND FUNCTIONS ###
#Function for counting through given alarm_time
def start_alarm(given_time):
    #Globals
    global stop_alarm

    #Determine the length of time from now the user wishes to wait (in the given format), and then convert it to seconds
    ##Move this to Hal and then just take in the number of seconds in this function??? That way it is easier to alert the user when the alarm is set, for how long, and if there is an error
    if "minutes" in given_time:
        alarm_time = ""
        print()

    if "hour" in given_time:
        alarm_time = ""
        print()

    if "tomorrow" in given_time:
        alarm_time = ""
        print()
    
    if "am" in given_time or "pm" in given_time:
        alarm_time = ""
        print()

    #Error catching
    else:
        return False

    while stop_alarm == False:
        if str(datetime.datetime.now().time()) >= alarm_time:
            stop_alarm = True
            os.system("alarm.mp3")


#Just used for ad-hoc testing
if __name__ == '__main__':
    start_alarm("set a timer for 10 minutes")