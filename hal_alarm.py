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

import datetime
import os

alarm_time = ""
stop = False
while stop == False:
    rn = str(datetime.datetime.now().time())
    if str(datetime.datetime.now().time()) >= alarm_time:
        stop = True
        os.system("alarm.mp3")