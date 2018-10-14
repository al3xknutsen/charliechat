from os import getcwd, getenv
from os.path import basename, split
from socket import gethostname


__appname__ = "CharlieChat"
__version__ = "Alpha 16 [WIP]"

codec = "utf-8"

appdata = getenv("APPDATA") + "\\CharlieChat\\"

if basename(split(getcwd())[0]) == "CharlieChat Dev Eclipse":
    __version__ += " [DEV]"
    host = gethostname()
else:
    host = gethostname()
port = 25000

defaultsettings = {
    "afkinterval": 300,
    "autoafk": True,
    "color": "#000000",
    "notemotes": [],
    "seconds": False,
    "sounds": True
}