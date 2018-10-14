import wx

from core.global_vars import host, port
from core.security.crypt import key_return
from page_avatar import PageAvatar
from ui.clear_input import ERASE_TEXT
from ui.complex.ui_account import AccountInfo
from ui.error_handler import ErrorMsg
from wizard_core import WizardPage

from . import keygen


class PageRegister(WizardPage, AccountInfo, ErrorMsg):
    '''Page for registering new user'''
    def __init__(self):
        WizardPage.__init__(self, "Register", "To create an account, we're gonna need a username and a password. "
                            "The account you create will be universal and used across all servers you log on to.",
                            "Register")

    def UI(self):
        from page_start import PageStart
        self.prevpage = PageStart
        self.nextpage = PageAvatar

        # Sizers
        grid = wx.FlexGridSizer(2, 1, 25, 25)
        self.inputs = wx.FlexGridSizer(3, 2, 10, 10)

        # Widgets
        self.UI_LOGIN(self.panel, self.inputs)
        lbl_password_repeat = wx.StaticText(self.panel, label="Repeat password:")
        self.password_repeat = wx.TextCtrl(self.panel, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        self.UI_ERROR(self.panel, grid)

        # Adding to sizers
        self.inputs.AddMany([(lbl_password_repeat, 0, wx.ALIGN_CENTER_VERTICAL), self.password_repeat])
        grid.Add(self.inputs, flag=wx.ALIGN_CENTER)

        # Binding events
        self.Bind(wx.EVT_TEXT_ENTER, self.gonext, self.username)
        self.Bind(wx.EVT_TEXT_ENTER, self.gonext, self.password)
        self.Bind(wx.EVT_TEXT_ENTER, self.gonext, self.password_repeat)
        self.password_repeat.Bind(wx.EVT_KEY_DOWN, ERASE_TEXT)

        self.username.SetFocus()
        return grid

    def gonext(self, event):
        '''Define what happens when pressing "Next"'''
        self.RESET_COLOR(self.username, self.password, self.password_repeat)

        keygen.join()  # Finishing keygen

        # REGISTERING
        if not self.REGISTER_ERROR(event, host, port, key_return(), \
                                   [self.username, self.password, self.password_repeat], \
                                   self.inputs):
            self.quit(None)
            self.nextpage(self.username.GetValue(), self.password.GetValue(), self.clientsocket)