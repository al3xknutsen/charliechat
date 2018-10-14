import wx


class ControlButtons:
    def CONTROL_BUTTONS(self, *labels):
        '''Function for generating control buttons on the bottom of a GUI window'''
        self.grid.SetRows(self.grid.GetRows() + 1)  # Allocating space in parent sizer
    
        # Sizers
        grid = wx.FlexGridSizer(2, 1, 10, 10)
        buttons = wx.FlexGridSizer(1, len(labels), 5, 5)
    
        # Widgets
        line = wx.StaticLine(self.panel)
        if len(labels) == 0:
            labels = ["save", "cancel"]  # Default buttons
        for lbl in labels:
            button = wx.Button(self.panel, label=lbl.title())
            buttons.Add(button, flag=wx.EXPAND)

            # Font size
            font = button.GetFont()
            font.SetPointSize(10)
            button.SetFont(font)
    
            # Bind to cancel
            if lbl.title() == "Cancel":
                self.Bind(wx.EVT_BUTTON, self.quit, button)
    
        # Bold font on main button
        boldbutton = list(buttons.GetChildren())[-2].GetWindow()
        font = boldbutton.GetFont()
        font.SetWeight(wx.BOLD)
        boldbutton.SetFont(font)
    
        # Growables
        buttons.AddGrowableCol(0)
        buttons.AddGrowableCol(1)
    
        # Adding to sizers
        grid.AddMany([(line, 0, wx.EXPAND), (buttons, 0, wx.EXPAND)])
        grid.AddGrowableCol(0)
        self.grid.Add(grid, flag=wx.EXPAND)
        return [widget.GetWindow() for widget in buttons.GetChildren()]