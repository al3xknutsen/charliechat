import wx

from ui.clear_input import ERASE_TEXT
from ui.templates.widgets import ControlButtons


class RoomPasswordWindow(wx.Dialog, ControlButtons):
    '''Window for prompting of password when trying to enter a password-protected private room'''
    def __init__(self, parent, room):
        wx.Dialog.__init__(self, parent, title=room)

        self.password = None

        # Panel
        self.panel = wx.Panel(self)

        # Sizers
        box = wx.BoxSizer()
        self.grid = wx.GridSizer(1, 1, 5, 5)
        passwidgets = wx.FlexGridSizer(1, 2, 10, 10)

        # Widgets
        lbl_passinput = wx.StaticText(self.panel, label="Password:")
        self.passinput = wx.TextCtrl(self.panel, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)

        # Adding widgets to sizers
        passwidgets.AddMany([(lbl_passinput, 0, wx.ALIGN_CENTER_VERTICAL), (self.passinput, 0, wx.EXPAND)])
        self.grid.Add(passwidgets, flag=wx.EXPAND)
        box.Add(self.grid, flag=wx.ALL, border=20)
        self.panel.SetSizer(box)

        passwidgets.AddGrowableCol(1)

        proceed = self.CONTROL_BUTTONS("Proceed", "Cancel")

        # Binding events
        self.passinput.Bind(wx.EVT_KEY_DOWN, ERASE_TEXT)
        self.Bind(wx.EVT_TEXT_ENTER, self.switch_room, self.passinput)
        self.Bind(wx.EVT_BUTTON, self.switch_room, proceed[0])
        self.Bind(wx.EVT_CLOSE, self.quit)

        # Setting size and showing window
        self.SetClientSize(self.panel.GetBestSize())
        self.Center()
        self.ShowModal()

    def switch_room(self, event):
        '''Completing password prompt and returning to main window'''

        # Get text from input and set value to class-space variable (to be used by main window)
        passinput = self.passinput.GetValue()
        if len(passinput) > 0:
            self.password = passinput
            self.quit(None)

    def quit(self, event):
        '''Close window'''
        self.Destroy()
