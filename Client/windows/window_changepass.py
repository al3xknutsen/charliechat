from core.file_manager import FILE_WRITE
from core.global_vars import appdata
from core.network.transfer import RECVMSG, SENDMSG
from core.security.crypt import key_generate, key_return
from core.security.hash import HASH
from ui.error_handler import ErrorMsg
from ui.templates.windows import AccountWindow


class ChangePassWindow(AccountWindow, ErrorMsg):
    '''Window for changing password of current user'''
    def __init__(self, host, port, username, password, servers):
        self.keygen = key_generate()
        
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.servers = servers

        self.servers.remove(self.host)

        AccountWindow.__init__(self, "change password", self.host, self.port, self.username, self.password, \
                               ["old password", "new password", "repeat new password"])

    def mainfunc(self, event):
        '''Main function'''
        self.RESET_COLOR(*self.textboxes)

        field_oldpass, field_newpass, field_newpass_repeat = self.textboxes
        old_password = field_oldpass.GetValue()
        new_password = field_newpass.GetValue()

        # Error handling
        if len(old_password) == 0:
            self.SHOW_ERRORMSG("Please input a password.", field_oldpass)
        elif len(new_password) == 0:
            self.SHOW_ERRORMSG("Please input a new password.", field_newpass)
        elif field_newpass_repeat.GetValue() != new_password:
            self.SHOW_ERRORMSG("'New password' and 'Repeat new password'\nneed to be identical!", \
                               field_newpass, field_newpass_repeat)
        else:
            # Connect to server if no errors occured
            if self.CONNECT(self.host, self.port):
                SENDMSG({"actiontype": "changepass", "user": self.username, \
                         "old_pass": HASH(old_password), \
                         "new_pass": HASH(new_password)}, self.clientsocket)
                response = RECVMSG(self.clientsocket)

                if response == "PROCEED":
                    # Create files and start main window
                    userdir = appdata + "\\" + self.username + "\\"

                    self.keygen.join()
                    self.ACCOUNT_FILES(key_return(), self.username, new_password)
                    FILE_WRITE(userdir + "oldpass.txt", HASH(old_password))
                    FILE_WRITE(userdir + "newpass.txt", str(self.servers))

                    from window_chat import ChatWindow
                    ChatWindow(self.username, new_password, self.host, self.port, self.clientsocket)
                    self.Destroy()
                else:
                    self.DEFAULT_ERROR(response, self.inputs)

