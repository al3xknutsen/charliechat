import wx

from ui.templates.widgets import ControlButtons


class AFKSettings(wx.Dialog, ControlButtons):
    '''Window for changing AFK settings'''
    def __init__(self, enabled, old_interval):
        wx.Dialog.__init__(self, None, title="AFK Settings")

        self.new_settings = None

        # Panel
        self.panel = wx.Panel(self)

        # Sizers
        box = wx.BoxSizer()
        self.grid = wx.FlexGridSizer(3, 1, 15, 15)
        interval = wx.FlexGridSizer(1, 2, 5, 5)

        # Widgets
        self.autoafk = wx.CheckBox(self.panel, label="Auto-AFK (triggering when user is inactive)")
        self.lbl_interval = wx.StaticText(self.panel, label="Time interval (minutes):")
        self.input_interval = wx.SpinCtrl(self.panel, value=str(old_interval / 60), size=(70, -1), min=1, max=120)

        # Adding to sizers
        interval.AddMany([(self.lbl_interval, 0, wx.ALIGN_CENTER_VERTICAL), self.input_interval])
        self.grid.AddMany([self.autoafk, interval])
        box.Add(self.grid, flag=wx.ALL, border=25)
        self.panel.SetSizer(box)

        save, cancel = self.CONTROL_BUTTONS()

        # Binding events
        self.Bind(wx.EVT_CHECKBOX, self.toggle_autoafk, self.autoafk)
        self.Bind(wx.EVT_BUTTON, self.save, save)
        self.Bind(wx.EVT_BUTTON, self.quit, cancel)
        self.Bind(wx.EVT_CLOSE, self.quit)

        self.autoafk.SetValue(enabled)
        self.toggle_autoafk(None)

        # Show window
        self.SetClientSize(self.panel.GetBestSize())
        self.Center()
        self.ShowModal()

    def toggle_autoafk(self, event):
        '''Function for toggling Auto-AFK'''

        # Enable
        if self.autoafk.IsChecked():
            self.lbl_interval.Enable()
            self.input_interval.Enable()
        # Disable
        else:
            self.lbl_interval.Disable()
            self.input_interval.Disable()

    def save(self, event):
        '''Function for saving settings'''
        self.new_settings = [self.autoafk.IsChecked(), self.input_interval.GetValue() * 60]
        self.quit(None)

    def quit(self, event):
        '''Closing window'''
        self.Destroy()
