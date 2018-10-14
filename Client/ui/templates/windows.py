import wx

from core.global_vars import host, port
from core.security.crypt import key_generate, key_return
from ui.clear_input import ERASE_TEXT
from ui.complex.ui_account import AccountInfo
from ui.error_handler import ErrorMsg
from widgets import ControlButtons


class AccountWindow(wx.Frame, AccountInfo, ControlButtons, ErrorMsg):
    '''Generic class for generating label-input grid layouts (mainly for login/registering)'''
    def __init__(self, mode, host, port, old_username, old_password, fields):
        self.keygen = key_generate()
        
        wx.Frame.__init__(self, None, title=mode.title())

        # Setting vars
        self.mode = mode
        self.host = host
        self.port = port
        self.old_username = old_username
        self.old_password = old_password
        self.textboxes = []

        # Panel
        self.panel = wx.Panel(self)

        # Sizers
        box = wx.BoxSizer()
        self.grid = wx.FlexGridSizer(2, 1, 15, 15)
        self.inputs = wx.FlexGridSizer(0, 2, 10, 10)

        self.UI_ERROR(self.panel, self.grid)

        # Label-input pair
        for field in fields:
            lbl = wx.StaticText(self.panel, label=field.capitalize() + ":")
            style = wx.TE_PROCESS_ENTER
            if "password" in field.lower():
                style |= wx.TE_PASSWORD
            textbox = wx.TextCtrl(self.panel, style=style)

            self.inputs.AddMany([(lbl, 0, wx.ALIGN_CENTER_VERTICAL), textbox])
            textbox.Bind(wx.EVT_KEY_DOWN, ERASE_TEXT)
            self.Bind(wx.EVT_TEXT_ENTER, self.mainfunc, textbox)

            self.textboxes.append(textbox)

        # Adding to sizers
        self.grid.Add(self.inputs, flag=wx.ALIGN_CENTER)
        box.Add(self.grid, flag=wx.ALL, border=25)
        self.panel.SetSizer(box)

        action, cancel = self.CONTROL_BUTTONS(mode.capitalize(), "Cancel")

        # Binding events
        self.Bind(wx.EVT_BUTTON, self.mainfunc, action)
        self.Bind(wx.EVT_BUTTON, self.quit, cancel)
        self.Bind(wx.EVT_CLOSE, self.quit)

        # Showing window
        self.SetClientSize(self.panel.GetBestSize())
        self.Center()
        self.Show()

    def mainfunc(self, event):
        '''Function defining the main action'''
        self.RESET_COLOR(*self.textboxes)

        # Getting input values
        username = self.textboxes[0].GetValue()
        password = self.textboxes[1].GetValue()

        # Setting error type
        mode_lower = self.mode.lower()
        if mode_lower == "switch user":
            error = self.LOGIN_ERROR
        elif mode_lower == "register":
            error = self.REGISTER_ERROR

        self.keygen.join()  # Finishing keygen

        if not error(event, self.host, self.port, key_return(), self.textboxes, self.inputs):
            self.Hide()
            if mode_lower == "register":
                # If register: Show avatar window
                self.old_username, self.old_password = username, password
                from windows.settings.settings_avatar import AvatarSettings
                AvatarSettings(username, True)
                self.quit(None)
                return

            # Start main window
            self.Destroy()
            from windows.window_chat import ChatWindow
            ChatWindow(username, password, host, port, self.clientsocket)

    def quit(self, event):
        '''Function for closing window and returning to main window'''
        self.CONNECT_LOGIN(self.host, self.port, self.old_username, self.old_password)
        self.Destroy()