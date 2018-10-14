from datetime import datetime
from ftplib import Error as ftperror, FTP
from os import getcwd, getpid, kill, listdir, mkdir, walk
from os.path import getmtime, isdir, isfile, relpath
from shutil import move
from signal import SIGTERM
from socket import error as socketerror
from subprocess import Popen
from time import gmtime, sleep, strptime

import wx

from core.file_manager import DIR_CREATE, DIR_DELETE, FILE_WRITE, FILE_DELETE
from core.global_vars import appdata, __version__
from core.thread import MultiThread

DIR_DELETE("tempfiles")  # Remove if already exists (wiping away any old files)
DIR_CREATE("tempfiles")
tempfiles = getcwd() + "\\tempfiles"

def connect():
    global ftp
    ftp = FTP("mystic.ddns.net", "CC-Client", "CHS1yFl4N1X92hJj")

def update_timer():
    while True:
        sleep(1)
        update_info()

def update_info():
    if not progress.Update(percent, message.format(str(totalbytes), str(percent), f))[0]:
        ftp.close()
        DIR_DELETE("tempfiles")
        kill(getpid(), SIGTERM)

# Vars
alldirs = [""]
allfiles = []
updatefiles = []
totalbytes = percent = currentbytes = 0

connect()

for folder in alldirs:  # Loop trough all folders
    content = []
    
    while True:
        try:
            ftp.retrbinary("MLSD " + folder, content.append)  # DOWNLOAD OVERVIEW
            break
        except ftperror:
            continue
        
    items = "".join(content).split("\r\n")[:-1]  # Join content if split in several blocks

    for x in items:
        # Parse data
        itemdata = x.split(";")
        name = itemdata[-1].lstrip(" ").strip("\r\n")
        itemtype, modify = [x.split("=")[1] for x in itemdata[:2]]

        partpath = (folder + "\\" + name).lstrip("\\")
        fullpath = tempfiles + "\\" + partpath

        # Folder: create local and add to loop
        if itemtype == "dir":
            if not isdir(fullpath):
                mkdir(fullpath)
            alldirs.append(partpath)

        # File: add if timestamp is newer or local does not exist
        elif itemtype == "file":
            if not isfile(partpath) or strptime(modify, "%Y%m%d%H%M%S") > gmtime(getmtime(partpath)):
                updatefiles.append(partpath)
                totalbytes += int(itemdata[2].split("=")[1])  # Add to total bytes
            allfiles.append(partpath)

# Text for ProgressDialog
title = "Updating - {0}%"
message = "Updating CharlieChat\n{0} / " + str(totalbytes) + " bytes   ({1}%)\n{2}"

app = wx.App()
app.MainLoop()
progress = wx.ProgressDialog(title.format(str(percent)), message.format(str(currentbytes), str(percent), ""), \
                             style=wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)

MultiThread(update_timer).start()

for f in updatefiles:  # Loop through all files needing download
    filecontent = []
    try:
        update_info()

        ftp.retrbinary("RETR " + f, filecontent.append)  # DOWNLOAD FILE

        # Write content to local file
        if not __version__.endswith(" [DEV]"):
            with open(tempfiles + "\\" + f, "wb") as updatefile:
                updatefile.write("".join(filecontent))

        # Update bytes and percent progress
        currentbytes += sum([len(x) for x in filecontent])
        percent = int(float(currentbytes) / totalbytes * 100)

        progress.SetTitle(title.format(str(percent)))

    except (ftperror, EOFError):
        updatefiles.append(f)  # Re-add file to loop if something goes wrong
    except socketerror:
        connect()

ftp.close()
FILE_WRITE(appdata + "\\last_update.txt", datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

# Deleting local files/dirs if not on server
if not __version__.endswith(" [DEV]"):
    for f in updatefiles:
        move(tempfiles + "\\" + f, f)

DIR_DELETE("tempfiles")
currentdir = getcwd()

programdirs = ["core", "images", "lib", "ui", "util", "windows"]

for pdir in programdirs:
    for path, folders, files in walk(currentdir + "\\" + pdir):
        for f in files:
            filepath = relpath(path + "\\" + f)
            if filepath not in allfiles:
                FILE_DELETE(filepath)
        for d in folders:
            dirpath = relpath(path + "\\" + d)
            if dirpath not in alldirs:
                DIR_DELETE(dirpath)

for f in listdir(currentdir):
    if f.startswith("CharlieChat.py"):
        Popen("python \"" + currentdir + "\\" + f + "\"")
        kill(getpid(), SIGTERM)
