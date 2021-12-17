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
def start_alarm(given_time, stop_alarm):

    #The actual alarm, witing by 1sec
    while stop_alarm == False:
        time.sleep(1)
        if str(datetime.datetime.now().time()) >= given_time:
            stop_alarm = True
            os.system("alarm.mp3")


#Just used for ad-hoc testing
if __name__ == '__main__':
    start_alarm("set a timer for 10 minutes")