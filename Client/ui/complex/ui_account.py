from base64 import b64encode

import wx

from core.file_manager import DIR_CREATE, FILE_WRITE
from core.global_vars import appdata
from core.network.connection import Connect
from core.network.messages import LOGIN, REGISTER
from core.network.transfer import RECVMSG, SENDMSG
from ui.clear_input import ERASE_TEXT
from ui.error_handler import ErrorMsg


class AccountInfo(Connect, ErrorMsg):
    '''Class for managing account stuff'''
    def UI_LOGIN(self, panel, sizer):
        '''Creating UI for login widgets'''

        # Widgets
        lbl_username = wx.StaticText(panel, label="Username:")
        self.username = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        lbl_password = wx.StaticText(panel, label="Password:")
        self.password = wx.TextCtrl(panel, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)

        # Adding to sizer
        sizer.AddMany([(lbl_username, 0, wx.ALIGN_CENTER_VERTICAL), self.username, \
                       (lbl_password, 0, wx.ALIGN_CENTER_VERTICAL), self.password])

        # Binding events
        self.username.Bind(wx.EVT_KEY_DOWN, ERASE_TEXT)
        self.password.Bind(wx.EVT_KEY_DOWN, ERASE_TEXT)

    def INFO_ERROR(self, field_user, field_password):
        '''Error messages for login'''
        if len(field_user.GetValue()) == 0:  # Empty username
            self.SHOW_ERRORMSG("Please input a username.", field_user)
            return True
        elif len(field_password.GetValue()) == 0:  # Empty password
            self.SHOW_ERRORMSG("Please input a password.", field_password)
            return True
        else:
            return False

    def ACCOUNT_ERROR(self, event, username, password, host, port, key, sizer, actiontype="login"):
        '''Connection errors when logging in or registering'''
        if self.CONNECT(host, port):
            if actiontype == "login":
                msg = LOGIN
            else:
                msg = REGISTER

            # Sending info and getting resonse
            SENDMSG(msg(username, password), self.clientsocket)
            response = RECVMSG(self.clientsocket)

            if response == "PROCEED":
                # keygen.join()
                self.ACCOUNT_FILES(key, username, password)  # Set up files
                if msg == REGISTER:
                    self.clientsocket.close()
                return False
            else:
                self.DEFAULT_ERROR(response, sizer)  # Show error msg according to response
                self.clientsocket.close()
                return True
        else:
            return True

    def LOGIN_ERROR(self, event, host, port, key, fields, sizer):
        '''Error when logging in'''
        if self.INFO_ERROR(*fields):  # Checking UI errors first...
            return True
        else:
            return self.ACCOUNT_ERROR(event, fields[0].GetValue(), fields[1].GetValue(), host, port, key, sizer)
            # ...then connection errors

    def REGISTER_ERROR(self, event, host, port, key, fields, sizer):
        '''Error when registering'''
        if self.INFO_ERROR(*fields[:2]):
            return True
        else:
            password = fields[1].GetValue()
            if fields[2].GetValue() != password:
                self.SHOW_ERRORMSG("'Password' and 'Repeat password'\nneeds to be identical!", *fields[1:])
                # Needs an extra check for "repeat password"
                return True
            else:
                return self.ACCOUNT_ERROR(event, fields[0].GetValue(), password, host, port, key, sizer, "register")

    def ACCOUNT_FILES(self, key, username, password):
        '''Setting up encryption key and account file'''
        userdir = appdata + username
        keystr = key.exportKey()
        accountinfo = b64encode(key.encrypt(str([username, password]), None)[0])

        DIR_CREATE(userdir)
        FILE_WRITE(appdata + "current_key.txt", keystr)
        FILE_WRITE(appdata + "current_account.txt", accountinfo)