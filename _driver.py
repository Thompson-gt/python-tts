from __future__ import annotations
#need this to use enums becuase pyton doesnt have a keyword for it
from enum import Enum
from typing import Final
import sys
import subprocess


#is the debug level for the engine config
DEBUG:Final[bool] = False

#enum for all of the os types
class Driver(Enum):
    LINUX = 1
    WINDOWS = 2
    MAC = 3

    @staticmethod
    #method to convert the enum type into the string value 
    def string_version(driver:Driver) -> str:
        if driver == Driver.WINDOWS:return "sapi5"
        if driver == Driver.LINUX:return "espeak"
        if driver == Driver.MAC:return "nsss"


def check_distro() -> str:
    try:
        #cat distro this dir should containe the type of distro
        distro = subprocess.run(["cat /proc/version"],shell=True,stdout=subprocess.PIPE).stdout.decode('utf-8')
    except:
        raise subprocess.SubprocessError("error checking the distro type ")
    return distro 

#have to do this check because linux might not have all of the dependenies needed for the 
# tts engine
def handle_linux_deps() -> None:
    distro = check_distro()
    try:
        if "Mint" in distro or "Ubuntu" in distro:
            subprocess.run(["sudo apt install espeak && sudo apt install ffmpeg"],shell=True)
        elif "Red Hat" in distro or "CentOs" in distro:
            subprocess.run(["sudo dnf install espeak && sudo dnf install ffmpeg"],shell=True)
        elif "Arch" in distro:
            subprocess.run(["sudo pacman -S espeak && sudo pacman -S ffmpeg"],shell=True)
        else:
            raise ValueError("could not resolve the distro type ")
    except:
        raise subprocess.SubprocessError("error when installing the dependencies for the tts engine")


def get_driver() ->str:
    operating_system = sys.platform
    if operating_system == "linux" or operating_system == "linux2":
        handle_linux_deps()
        return Driver.string_version(Driver.LINUX)
    if operating_system == "darwin":
        return Driver.string_version(Driver.MAC)
    if operating_system == "win32" :
        return Driver.string_version(Driver.WINDOWS)
    raise ValueError("could not resolve the os type")