from os import listdir

import wx

from ui.templates.widgets import ControlButtons


class EmoteSettings(wx.Dialog, ControlButtons):
    '''Window for changing emote settings'''
    def __init__(self, disabled):
        wx.Dialog.__init__(self, None, title="Emote Settings")

        self.new_settings = None
        self.disabled_emotes = {}

        # self.panel
        self.panel = wx.Panel(self)

        # Sizers
        box = wx.BoxSizer()
        self.grid = wx.FlexGridSizer(3, 1, 5, 5)
        selection = wx.GridSizer(1, 2, 5, 5)
        self.grid_emotes = wx.FlexGridSizer(0, 8, 5, 5)

        # Widgets
        self.select_all = wx.Button(self.panel, label="Select all")
        self.unselect_all = wx.Button(self.panel, label="Unselect all")

        selection.AddMany([self.select_all, self.unselect_all])
        path_emotes = "images\\emotes\\"

        # Loading images
        for emote in listdir(path_emotes):
            if emote.endswith(".png"):

                # Emote widgets
                emote_name = ".".join(emote.split(".")[:-1])
                emote_image = wx.StaticBitmap(self.panel, bitmap=wx.Bitmap(path_emotes + emote))
                emote_check = wx.CheckBox(self.panel)
                self.disabled_emotes[emote_name] = emote_check

                # Check checkboxes
                if disabled != "ALL":
                    emote_check.SetValue(emote_name not in disabled)

                self.grid_emotes.AddMany([(emote_image, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL), \
                                          (emote_check, 0, wx.ALIGN_CENTER_VERTICAL)])

        # Adding to sizer
        self.grid.AddMany([(selection, 0, wx.ALIGN_CENTER), (self.grid_emotes, 0, wx.ALIGN_CENTER)])
        box.Add(self.grid, flag=wx.ALL, border=20)
        self.panel.SetSizer(box)

        save, cancel = self.CONTROL_BUTTONS()  # @UnusedVariable

        # Binding events
        self.Bind(wx.EVT_BUTTON, self.select, self.select_all)
        self.Bind(wx.EVT_BUTTON, self.select, self.unselect_all)
        self.Bind(wx.EVT_BUTTON, self.save, save)
        self.Bind(wx.EVT_CLOSE, self.quit)

        # Show window
        self.SetClientSize(self.panel.GetBestSize())
        self.Center()
        self.ShowModal()

    def select(self, event):
        '''Function for selecting and unselecting all items'''
        obj = event.GetEventObject()
        checkboxes = [widget.GetWindow() for widget in self.grid_emotes.GetChildren()\
        if widget.GetWindow().GetClassName() == "wxCheckBox"]

        # Selecting / unselecting all items
        for checkbox in checkboxes:
            if obj == self.select_all:
                checkbox.SetValue(True)
            elif obj == self.unselect_all:
                checkbox.SetValue(False)

    def save(self, event):
        '''Saving settings'''
        emotes = [emote.GetValue() for emote in self.disabled_emotes.values()]
        if emotes.count(True) == 0:
            self.new_settings = "ALL"
        else:
            self.new_settings = [emote for emote in self.disabled_emotes if not self.disabled_emotes[emote].GetValue()]
        self.quit(None)

    def quit(self, event):
        '''Closing window'''
        self.Destroy()
