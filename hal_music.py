'''
TITLE: HAL_WEATHER
BY:
    Some Guy they call Scooter
    Common Sense Cyber Group

Created: 2/1/2022
Updated: 2/1/2022

Version: 1.0.1

License: MIT

Purpose:
    -This script is used for streaming music off of youtube
    -VLC (same arch as installed python version) is required for this to work properly!

To Do:
    -Figure out how to find a playlist and play it (ie create personal playlists, and then randompy play one, or select one from the group)
'''

### IMPORT LIBRARIES ###
import threading
import pafy
import vlc
import re, urllib.parse, urllib.request

### CLASSES AND FUNCTIONS ###
#Function that is called to kick off the thread to play the requested song/video
def kicker(song):
    threading.Thread(target=stream(song))

#Function that is used to find the best quality audio on YouTube, and then play it using VLC. THREADED so it will continue until done, or main script kills it.
def stream(name):
    #Create the string and use it to search YouTube for the song we want
    query_string = urllib.parse.urlencode({"search_query": name})
    formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
    search_results = re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())

    #Get the best audio path for the video
    vid_clip = "https://www.youtube.com/watch?v=" + "{}".format(search_results[0])
    link = pafy.new(vid_clip) 
    audio_url = link.getbestaudio()  

    #Now stream the video with VLC instead of downloading it
    media = vlc.MediaPlayer(audio_url.url)  
    media.play()

#For ad-hoc testing only
if __name__ == "__main__":
    threading.Thread(target=stream(input("Search for a song: ")))
    stream(input("Search for a song: "))  