'''
TITLE: HAL_MUSIC
BY:
    Some Guy they call Scooter
    Common Sense Cyber Group

Created: 2/1/2022
Updated: 5/30/2023

Version: 1.0.1

License: MIT

Purpose:
    -This script is used for streaming music off of youtube
    -VLC (same arch as installed python version) is required for this to work properly!
    -This script will be subprocessed from the main script so it can be killed if the user asks for the music to stop

To Do:
    -How can we play a number of songs in a row or similar without stopping?

'''

### IMPORT LIBRARIES ###
import pafy # - Used for grabbing URLs of YouTube songs
import vlc # - Used for playing audio from a YouTube URL
import re, urllib.parse, urllib.request # - Used for regex and url related items
import argparse # - Used for getting script arguments passed in
import logging # - Used for error logging


### DEFINE VARIABLES ###
#Set up logging for user activities
logging_file = "bloody_hal.log"         #Define log file location for windows
logger = logging.getLogger("Hal_Music Log")  #Define log name
logger.setLevel(logging.DEBUG)              #Set logger level
fh = logging.FileHandler(logging_file)      #Set the file handler for the logger
fh.setLevel(logging.DEBUG)                  #Set the file handler log level
logger.addHandler(fh)                       #Add the file handler to logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')   #Format how the log messages will look
fh.setFormatter(formatter)                  #Add the format to the file handler

### CLASSES AND FUNCTIONS ###
#Function that is used to find the best quality audio on YouTube, and then play it using VLC. THREADED so it will continue until done, or main script kills it.
def yt_stream(name):
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

### THE THING ###
if __name__ == "__main__":
    #Set up the argument parsing so we can recieve what the user wants to play
    parser = argparse.ArgumentParser()
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument("-s", dest="Song", required=True, type=str)  #Argument used for getting the song/playlist from the main script

    args = parser.parse_args()

    #Kick off the stream with the requested song/music
    yt_stream(args.Song)


    #For ad-hoc testing only
    #stream(input("Search for a song: "))
