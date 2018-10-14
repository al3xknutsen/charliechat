from base64 import b64decode
from datetime import datetime
from os import getpid, kill
from os.path import isfile
from signal import SIGTERM
import sys

from Crypto.PublicKey import RSA
from wx import App

from core.file_manager import DIR_CREATE, FILE_DELETE, FILE_WRITE, FILE_READ
from core.global_vars import appdata, host, port
from core.network.connection import Connect
from core.network.messages import LOGIN
from core.network.transfer import RECVMSG, SENDMSG
from core.security.hash import HASH
from windows.window_chat import ChatWindow
from windows.wizard.page_start import PageStart


# File paths
current_account = appdata + "current_account.txt"
current_key = appdata + "current_key.txt"
new_server = appdata + "new_server.txt"
last_update = appdata + "\\last_update.txt"

# Creating instances
Connect = Connect()

DIR_CREATE(appdata)
if not isfile(last_update):
    FILE_WRITE(last_update, datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
FILE_DELETE(new_server)

# Creating error file
# sys.stderr = open(appdata + "error.log", "a")

# Starting application
app = App()
if isfile(current_account) and isfile(current_key):
    while host != None and port != None:
        # Connecting
        if Connect.CONNECT(host, port, False):
            key = RSA.importKey(FILE_READ(current_key))
            username, password = eval(key.decrypt(b64decode(FILE_READ(current_account))))
            
            # Changing password when connecting
            oldpass = appdata + username + "\\oldpass.txt"
            newpass = appdata + username + "\\newpass.txt"
            if isfile(newpass) and host in eval(FILE_READ(newpass)):
                changepass = True
                SENDMSG({"actiontype": "changepass", "user": username, \
                         "old_pass": FILE_READ(oldpass), "new_pass": HASH(password)}, \
                        Connect.clientsocket)
            else:
                changepass = False
                msg = LOGIN(username, password, True)
                SENDMSG(msg, Connect.clientsocket)
            
            response = RECVMSG(Connect.clientsocket)
            
            # Opening window
            if response == "PROCEED":
                if changepass:
                    remain_hosts = eval(FILE_READ(newpass))
                    remain_hosts.remove(host)
                    if len(remain_hosts) == 0:
                        FILE_DELETE(oldpass)
                        FILE_DELETE(newpass)
                    else:
                        FILE_WRITE(newpass, remain_hosts)
                
                ChatWindow(username, password, host, port, Connect.clientsocket)
                app.MainLoop()
            else:
                # SHOW LOGIN WINDOW IF LOGIN FAILED
                break
            
            # Checking if client should logon to new server (switching server)
            hostdata = FILE_READ(new_server)
            if hostdata:
                host, port = eval(hostdata)
            else:
                host = port = None
        else:
            host = port = None
    else:
        FILE_DELETE(new_server)
                
else:
    PageStart()
    app.MainLoop()

# Terminate
sys.stderr.close()
kill(getpid(), SIGTERM)
