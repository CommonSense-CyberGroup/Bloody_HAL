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
import argparse

### DEFINE VARIABLES ###
stop_alarm = False  #Used for stopping the alarm when finished

### CLASSES AND FUNCTIONS ###
#Function for counting through given alarm_time
def start_alarm(given_time):

    #The actual alarm, witing by 1sec
    while stop_alarm == False:
        time.sleep(1)
        if str(datetime.datetime.now().time()) >= given_time:
            stop_alarm = True
            os.system("alarm.mp3")

#Just used for ad-hoc testing
if __name__ == '__main__':
    #Set up the argument parsing so we can recieve what the user wants to play
    parser = argparse.ArgumentParser()
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument("-t", dest="Time", required=True, type=str)  #Argument used for getting the time from the main script

    args = parser.parse_args()

    #Kick off the stream with the requested song/music
    start_alarm(args.Time)