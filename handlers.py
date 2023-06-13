#included
from __future__ import annotations
from typing import Final
import sys
import os
import argparse
from enum import Enum, auto
import random
import time
#installed
import requests
import bs4
import pyttsx3

#NOTE constants
#ansi code to reset the terminal color 
COLOR_Reset:Final[str] = "\u001b[0m"
DEFAULT_MESSAGE:Final[str] = "neither message,url or file was passed to be read, please pass one of them next time or use the dash help flag for all usage options"
MESSAGE_PATH:Final[str] = "display.txt"

#a enum to handle all of the color options 
#also allows to check the type without it expanding to a string
class Color(Enum):
    RED = auto()
    GREEN = auto() 
    YELLOW = auto()
    BLUE = auto()
    MAGENTA= auto() 
    CYAN = auto()
    
    #use a static method to handle the return of the ansi code
    @staticmethod
    def get_color(color: Color)-> str:
        if color == Color.RED:return "\u001b[31m"  
        if color == Color.GREEN:return "\u001b[32m"  
        if color == Color.YELLOW:return "\u001b[33m"  
        if color == Color.BLUE:return "\u001b[34m"  
        if color == Color.MAGENTA:return "\u001b[35m"  
        if color == Color.CYAN:return "\u001b[36m"  
    
    @staticmethod
    def random_color() -> Color:
        return Color(random.randint(1,6))

#create this so we can type hint the args
class Args():
    def __init__(
        self,
        readfile:str,
        message:list[str],
        volume:float,
        readertype:int,
        rate:int,
        url:str,
        writer:str,
        colorWriter:str,
        useHelp:str
        ) -> None:
        self.readfile = readfile
        self.message = message
        self.readervolume = volume
        self.readertype = readertype
        self.rate = rate
        self.url = url
        self.writer = writer
        self.colorWriter = colorWriter
        self.useHelp = useHelp
    
    def __repr__(self) -> str:
        return f"\nfile: {self.readfile} \n message: {self.message} \n volue: {self.readervolume} \n type: {self.readertype} \n rate: {self.rate} \n url: {self.url} \n writer: {self.writer}\n color: {self.colorWriter} \n"


    def validate(self,) -> None:
        if len(self.message) == 0:
            raise ValueError("valid message must be passsed")
        if self.rate >= 201 or self.rate <= 0:
            raise ValueError("rate must be greater than 0 and less than 201")
        if self.readertype <0 or self.readertype >1:
            raise ValueError("reader type must be 0 or 1")
        if self.readervolume > 1.0 or self.readervolume < 0.0:
            raise ValueError("reader volume range is between 1.0 - 0.0")
        return



def read_file(path:str) -> str:
    try:
        with open(os.path.join(os.getcwd(),path),'r') as f:
            return f.read()
    except Exception as e:
        if isinstance(e,FileNotFoundError):
            raise FileNotFoundError(f"no file found at {path}")
        else:
            raise e

def get_arguments() -> Args:
    try:
        p = argparse.ArgumentParser(add_help=False, exit_on_error=True)
        p.add_argument("-f","--readfile",dest="readfile",default=".nowhere",help="file to read" )
        p.add_argument("-m","--message",dest="message",default="no message",help="message to read",nargs='+' )
        p.add_argument("-v","--readervolume",dest="readervolume",default="1.0",help="volume of the reader(0.0-1.0)",type=float)
        p.add_argument("-t","--readertype",dest="readertype",default="0",help="gender of the reader(1 or 0)" ,type=int,choices=[1,0])
        p.add_argument("-r","--rate",dest="rate",default="200",help="how fast for reader to speak" ,type=int)
        p.add_argument("-u","--url",dest="url",default="www.nowhere.com",help="website to query and read" )
        p.add_argument("-w","--writer",dest="writer",default=0,help="have the text printed to the screen when read", action='count')
        p.add_argument("-c","--color",dest="colorWriter",default=0,help="have the output of the writer be colorful", action='count')
        p.add_argument("-h","--help",dest="useHelp",default=0,help="display all usage options", action='count')
        args = p.parse_args()
        return Args(args.readfile,args.message,args.readervolume,args.readertype,args.rate,args.url, args.writer, args.colorWriter, args.useHelp)
    # catch all of the known errors from the argparser lib so i know what is failing 
    except (argparse.ArgumentError, argparse.ArgumentTypeError) as e:
        raise ValueError("error when parsing the flags", e)
    except Exception as e:
        raise ValueError("unknown error raised", e)



#check if all of the flags still have their default values
def default_args(args:Args) -> bool:
    return args.readfile == ".nowhere" and args.message == "no message" and args.readervolume == 1.0 and args.readertype == 0.0  and args.rate == 100

#check if either message or file was provided, cannot be both
def text_to_say(args:Args) -> str:
    #make sure to add a option for the url flag later
    if  args.message == "no message" and not args.readfile == ".nowhere" and  args.url == "www.nowhere.com":
        return read_file(args.readfile)
    if  not args.message == "no message" and  args.readfile == ".nowhere" and  args.url == "www.nowhere.com":
        return "".join(args.message)
    if not args.url == "www.nowhere.com" and args.message == "no message" and args.readfile == ".nowhere":
        return query_website(args.url)
    return DEFAULT_MESSAGE


#will read and return the colored options
def get_help_options() -> str:
    try:
        with open(MESSAGE_PATH,'r') as f:
            lines = f.readlines()
            h = style_help(lines)
            return h
    except Exception as e:
        raise OSError("problem when reading the help file",e)

#will take in the list of options and return a colored version of them as the full string
def style_help(lines:list[str]) -> str:
    s = Color.get_color(Color.YELLOW) + lines[0] + COLOR_Reset + "\n"
    try:
        #skip the title 
        for item in lines[1:]:
            spliter = item.find(':')
            #change the color of the text in the paranthsis
            start = item.find("(")
            end = item.find(")")
            flags = Color.get_color(Color.GREEN) + item[:spliter+1] + COLOR_Reset
            desc = Color.get_color(Color.CYAN) +item[spliter+1:start] + COLOR_Reset
            params = Color.get_color(Color.MAGENTA) + item[start:end+1] + COLOR_Reset
            s+= flags + desc + params + "\n"
    except Exception as e:
        raise OSError("problem when styling the help options",e)
    return s

def display_help() -> None:
    print(get_help_options())


#simple fucntion to query a website and return the contents as a string
def query_website(url:str) -> str:
    if  type(url) != str or len(url) <=0:
        raise ValueError("the url must be a string and must not be empty")
    try:
        r = requests.get(url)
        soup = bs4.BeautifulSoup(r.content,"html.parser")
        #will read the longer of the 2 tags if both are present
        if soup.body and soup.article:
            choice = soup.body.text if len(soup.body.text) > len(soup.article.text) else soup.article.text
            return choice
        elif soup.body :
            return soup.body.text 
        elif soup.article:
            return soup.article.text
        else:
            raise BaseException("error when reading the body of the request")
    except Exception as e:
        if str(e) == "error when reading the body of the request":
            raise e
        else:
            raise requests.HTTPError("there was a problem when quering the website", e)



def colored_print(color: Color, msg:str) -> None:
    if type(color) != Color: raise ValueError("invalid color given , must be type color")
    if type(msg) != str: raise ValueError("invalid message given, must be of type string")
    if len(msg) <= 0 : raise ValueError("message can not ve empty")
    sys.stdout.write(Color.get_color(color) + msg + COLOR_Reset)


# will be the function that takes the text and prints it to the terminal 
# (should make make one thread for voice reading and another for stdout)
def voice_to_terminal(text:list[str], speed:int, color:int) -> None:
    if len(text) == 0: raise ValueError("text to say must not be empty")
    if color:
        for word in text:
            print(" \033[2K read along: {}".format(Color.get_color(Color.random_color()) + word + COLOR_Reset), end="\r", flush=True, file=sys.stdout)
            time.sleep(speed / 100 )
    else:
        for word in text:
            # ansi code will make sure the full string is printed over 
            print(" \033[2K read along: {}".format(word), end="\r", flush=True, file=sys.stdout)
            # needs to sleep by speed divided by 100 (to make it a ones number)
            # to be in sync with the bots reading speed
            time.sleep(speed / 100 )
    return


# this should take the already configured tts engine and the text to say
# should simply say the text, need to do this in a fucnion so it can be a thread
def text_to_speach(text: str, tts: pyttsx3.Engine) -> None:
    tts.say(text)
    tts.runAndWait()
    return