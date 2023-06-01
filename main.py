from typing import NewType
import sys
import threading
#tts engine lib
import pyttsx3
#config options for the tts engine
from _driver import get_driver, DEBUG
#the handles for reading the args
from handlers import  get_arguments, text_to_say, display_help,default_args,query_website, voice_to_terminal, text_to_speach


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
        text = text_to_say(args)
        #make output while the bot is reading the words, make them read in place 
        writer = threading.Thread(target=voice_to_terminal, args=(text.split(" "), args.rate))
        reader = threading.Thread(target=text_to_speach, args=(text,tts))
        reader.start()
        writer.start()
        reader.join()
        writer.join()
        sys.exit()


if __name__ == "__main__":
    main()