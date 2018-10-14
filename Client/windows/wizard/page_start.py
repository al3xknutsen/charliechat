import wx

from page_login import PageLogin
from page_register import PageRegister
from wizard_core import WizardPage


class PageStart(WizardPage):
    '''Introduction page'''
    def __init__(self):
        WizardPage.__init__(self, "Welcome!")

    def UI(self):
        grid = wx.FlexGridSizer(3, 1, 25, 25)  # Sizer

        # Widgets
        welcome_headline = wx.StaticText(self.panel, label="Welcome to CharlieChat!")
        welcome_body = wx.StaticText(self.panel, label="Since this is the first time starting the application, you need to create an account.")
        welcome_body.Wrap(250)
        self.have_account = wx.CheckBox(self.panel, label="I already have an account.")

        # Adding to sizer
        grid.AddMany([(welcome_headline, 0, wx.ALIGN_CENTER), welcome_body, self.have_account])

        # Binding events
        self.Bind(wx.EVT_CHECKBOX, self.changenext, self.have_account)
        self.changenext(None)
        return grid

    def changenext(self, event):
        '''Dynamically change which page is next (based on value of checkbox)'''
        if self.have_account.IsChecked():
            self.nextpage = PageLogin
        else:
            self.nextpage = PageRegister