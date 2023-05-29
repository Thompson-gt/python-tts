from typing import NewType
import sys
#tts engine lib
import pyttsx3
#config options for the tts engine
from _driver import get_driver, DEBUG
#the handles for reading the args
from handlers import  get_arguments, text_to_say, display_help,default_args,query_website
import time



def main() -> None:
    tts = pyttsx3.init(get_driver(),DEBUG)
    args = get_arguments()
    args.validate()
    tts.setProperty('volume',args.readervolume)
    tts.setProperty('voices',tts.getProperty('voices')[args.readertype])
    tts.setProperty('rate',args.rate)
    #will check the args are return the text to be read
    if default_args(args): 
        display_help()
    else:
        #make output while the bot is reading the words, make them read in place 
        tts.say(text_to_say(args))
        tts.runAndWait()


if __name__ == "__main__":
    main()