from os.path import isfile

import wx

from core.global_vars import appdata
from ui.templates.widgets import ControlButtons
from windows.wizard.page_avatar import PageAvatar


class AvatarSettings(PageAvatar, wx.Dialog, ControlButtons):
    '''Window for changing avatar'''
    def __init__(self, username, newuser=False):
        self.username = username
        self.newuser = newuser
        self.new_settings = None

        self._maxsize()
        wx.Dialog.__init__(self, None, title="Avatar Settings")

        # Panel
        self.panel = wx.Panel(self)

        # Sizers
        box = wx.BoxSizer()
        self.grid = wx.FlexGridSizer(1, 1, 10, 10)

        # Adding to sizer
        self.grid.Add(self.UI())
        box.Add(self.grid, flag=wx.ALL, border=20)
        self.panel.SetSizer(box)
        save, cancel = self.CONTROL_BUTTONS()  # @UnusedVariable

        # Binding events
        self.Bind(wx.EVT_BUTTON, self.gonext, save)
        self.Bind(wx.EVT_CLOSE, self.quit)

        self.path_avatar = appdata + "avatars\\" + self.username + ".png"
        if isfile(self.path_avatar):
            self.pathinput.SetValue(self.path_avatar)
            self.filepath_input(None)

        # Showing window
        self.SetClientSize(self.panel.GetBestSize())
        self.Center()
        self.ShowModal()

    def start_chat(self):
        '''Saving avatar and closing window'''
        if self.newuser:
            self._save_avatar()
        elif self.pathinput.GetValue() != self.path_avatar:
            self.new_settings = self.image.GetBitmap()
        self.quit(None)
