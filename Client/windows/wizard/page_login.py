import wx

from core.global_vars import host, port
from core.security.crypt import key_return
from ui.complex.ui_account import AccountInfo
from ui.error_handler import ErrorMsg
from wizard_core import WizardPage

from . import keygen


class PageLogin(WizardPage, AccountInfo, ErrorMsg):
    '''Page for logging in'''
    def __init__(self):
        WizardPage.__init__(self, "Login", "Oh! Sorry about the mixup. Simply login to your account to continue.")

    def UI(self):
        from page_start import PageStart
        self.prevpage = PageStart

        # Sizers
        grid = wx.FlexGridSizer(2, 1, 25, 25)
        self.inputs = wx.FlexGridSizer(2, 2, 10, 10)

        # Widgets
        self.UI_LOGIN(self.panel, self.inputs)
        self.UI_ERROR(self.panel, grid)
        grid.Add(self.inputs, flag=wx.ALIGN_CENTER)

        self.username.SetFocus()

        # Binding events
        self.Bind(wx.EVT_TEXT_ENTER, self.gonext, self.username)
        self.Bind(wx.EVT_TEXT_ENTER, self.gonext, self.password)

        return grid

    def gonext(self, event):
        '''Define what happens when pressing "Next"'''
        self.RESET_COLOR(self.username, self.password)

        keygen.join()  # Finishing keygen

        # LOGGING IN
        if not self.LOGIN_ERROR(event, host, port, key_return(), [self.username, self.password], self.inputs):
            self.quit(None)
            from windows.window_chat import ChatWindow
            ChatWindow(self.username.GetValue(), self.password.GetValue(), host, port, self.clientsocket)