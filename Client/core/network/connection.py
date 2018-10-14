from datetime import datetime
from os import getcwd, getpid, kill
from signal import SIGTERM
from socket import error as socketerror, socket
from ssl import wrap_socket, PROTOCOL_TLSv1
from subprocess import Popen

import wx

from core.file_manager import FILE_READ
from core.global_vars import appdata
from core.network.messages import LOGIN
from core.network.transfer import RECVMSG, SENDMSG
from ui.error_handler import ErrorMsg


class Connect(ErrorMsg):
    def CONNECT_CORE(self, host, port):
        '''Core connection function - creating connection and checking for update'''
        self.clientsocket = socket()
        self.clientsocket = wrap_socket(self.clientsocket, ssl_version=PROTOCOL_TLSv1)
        self.clientsocket.connect((host, port))
    
        # Checking for new version
        version_current = datetime.strptime(RECVMSG(self.clientsocket), "%d-%m-%Y %H:%M:%S")
        version_local = datetime.strptime(FILE_READ(appdata + "\\last_update.txt"), "%d-%m-%Y %H:%M:%S")
        if version_current > version_local:
            SENDMSG(True, self.clientsocket)
            Popen("python \"" + getcwd() + "\\run_updater.py\"")
            kill(getpid(), SIGTERM)
        else:
            SENDMSG(False, self.clientsocket)
    
    def CONNECT(self, host, port, panel=True):
        '''Creating connection to server, displaying message while waiting, and showing error message when failing'''
    
        connecting = wx.BusyInfo("Connecting...")  # Wait msg #@UnusedVariable
    
        try:
            self.CONNECT_CORE(host, port)
            return True
        except socketerror:
            # Show error message if failed
            if panel:
                self.SHOW_ERRORMSG("Could not connect to the server!")
            else:
                wx.MessageDialog(None, "Could not connect to the server!", "Could not connect!", wx.OK | wx.ICON_ERROR).ShowModal()
            self.clientsocket.close()
            return False
    
    def CONNECT_LOGIN(self, host, port, username, password):
        '''Shortcut for connecting and logging in'''
        if self.CONNECT(host, port, False):
            SENDMSG(LOGIN(username, password), self.clientsocket)
            if RECVMSG(self.clientsocket) == "PROCEED":
                from windows.window_chat import ChatWindow
                ChatWindow(username, password, host, port, self.clientsocket)