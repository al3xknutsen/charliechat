import wx


errormessages = {
    "WRONG-USERNAME": ["Wrong username!", "username"],
    "WRONG-PASSWORD": ["Wrong password!", ["password", "old password"]],
    "USER-ALREADY-EXISTS": ["Username is already taken!", "username"]
}

class ErrorMsg:
    '''Class for creating error messages'''
    def UI_ERROR(self, panel, sizer):
        '''Creating error widgets and adding them to sizer'''

        # Adding panel and sizer
        self.panel = panel
        self.sizer = sizer

        self.sizer.SetRows(self.sizer.GetRows() + 1)  # Add rows for the error widgets

        grid = wx.FlexGridSizer(2, 1, 5, 5)
        self.errormsg = wx.StaticText(panel, label="", style=wx.ALIGN_CENTER)
        self.errormsg.Hide()

        # Setting text weight and color
        font = self.errormsg.GetFont()
        font.SetWeight(wx.BOLD)
        self.errormsg.SetFont(font)
        self.errormsg.SetForegroundColour((200, 0, 0))

        # Adding to sizer
        grid.AddMany([(self.errormsg, 0, wx.ALIGN_CENTER)])
        self.sizer.Add(grid, flag=wx.ALIGN_CENTER)

    def SHOW_ERRORMSG(self, msg, *widgets):
        '''Showing the actual error message'''

        self.errormsg.SetLabel(msg)
        self.errormsg.Show()

        # Updating and resizing UI
        self.sizer.Layout()
        if str(type(self.panel)).split(" '")[-1].startswith("lib.startup_wizard"):
            self.panel.Layout()
        else:
            self.SetClientSize(self.panel.GetBestSize())
        self.panel.Refresh()

        # Set color of inputs
        for w in widgets:
            w.SetBackgroundColour("#FFB4B4")
        textctrls = [w for w in widgets if w.GetClassName() == "wxTextCtrl"]
        if len(textctrls) > 0:
            first = textctrls[0]
            first.SetFocus()
            first.SetSelection(-1, -1)

        # Showing window
        if not self.IsShown():
            self.Center()
            self.Show()

    def DEFAULT_ERROR(self, response, sizer):
        '''Using a default error message'''
        
        for widget in sizer.GetChildren():
            window = widget.GetWindow()
            if window.GetClassName() == "wxStaticText" and window.GetLabel().lower().strip(":") in errormessages[response][1]:
                self.SHOW_ERRORMSG(errormessages[response][0], wx.FindWindowById(window.GetId() + 1))

    def RESET_COLOR(self, *widgets):
        '''Resetting color of widgets'''
        for w in widgets:
            w.SetBackgroundColour("white")