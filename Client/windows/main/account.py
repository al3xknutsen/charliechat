import wx

from core.file_manager import FILE_WRITE, DIR_DELETE, FILE_DELETE
from core.global_vars import appdata
from ui.templates.windows import AccountWindow
from windows.window_changepass import ChangePassWindow


class AccountManager:
    def switch_user(self, event):
        '''Switching user'''
        FILE_WRITE(appdata + "new_server.txt", [self.host, self.serverdata[self.host]])
        self.quit(None)
        AccountWindow("switch user", self.host, self.port, self.username, self.password, ["username", "password"])

    def register_user(self, event):
        '''Registering new user'''
        FILE_WRITE(appdata + "new_server.txt", [self.host, self.serverdata[self.host]])
        self.quit(None)
        AccountWindow("register", self.host, self.port, self.username, self.password, \
                      ["username", "password", "repeat password"])

    def delete_user(self, event):
        '''Deleting user'''
        if wx.MessageDialog(self, "Are you sure you want to delete your account (" + self.username + ")?", \
                            "Delete Account",  style=wx.YES_NO | wx.NO_DEFAULT | \
                            wx.ICON_QUESTION).ShowModal() == wx.ID_YES:

            self._try_send({"datatype": "del_user", "user": self.username})
            self.quit(None, False)

            # Delete all user files
            DIR_DELETE(self.userdir)
            FILE_DELETE(self.paths["avatar"])
            FILE_DELETE(appdata + "current_account.txt")
            FILE_DELETE(appdata + "current_key.txt")

    def change_password(self, event):
        '''Changing password'''
        FILE_WRITE(appdata + "new_server.txt", [self.host, self.serverdata[self.host]])
        self.quit(None)
        ChangePassWindow(self.host, self.port, self.username, self.password, self.servers.GetItems())