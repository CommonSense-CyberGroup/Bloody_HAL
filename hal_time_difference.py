#Turn this into a small script 'hal_time_difference' that can be called from the main script so we dont have to copy and paste it everywhere

import datetime
#Specify Time differences
day = 1
hour = 0
minute = 2

#Calculate difference and convert it to seconds
current_time = datetime.datetime.today()
alarm_time = current_time - datetime.timedelta(days = day, hours  = hour, minutes = minute)
difference_in_days = abs((alarm_time - current_time).seconds)

#If the day is not today, add the apppropriate number of seconds
if day > 0:
    difference_in_days += (day * 86400)

#Print
print(difference_in_days)