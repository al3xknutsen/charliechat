from socket import error as socketerror, SHUT_RDWR
from threading import enumerate as thread_enum
from time import sleep

import wx

from core.file_manager import FILE_WRITE
from core.network.transfer import SENDMSG
from util.platforms import Hook
from ui.html.html_vars import HTML_SESSION


class ConnectionManager(Hook):
    def reconnect_client(self):
        '''Function for reconnecting after losing connection to server'''
        try:
            self.clientsocket.shutdown(SHUT_RDWR)
            self.clientsocket.close()
            self.CONNECT_CORE(self.host, self.port)
            SENDMSG({"actiontype": "reconnect", "user": self.username}, self.clientsocket)
            return True
        except socketerror:
            return False
    
    def reconnect_msg(self):
        '''Displaying message that the client is reconnecting'''
        wx.CallAfter(self.reconnect.Show)
        # self.reconnect.Show()
        while self.reconnecting:
            # Hide and display periods after text
            if self.reconnect.GetLabel().endswith("..."):
                wx.CallAfter(self.reconnect.SetLabel, self.reconnect.GetLabel().strip("."))
            else:
                wx.CallAfter(self.reconnect.SetLabel, self.reconnect.GetLabel() + ".")
            sleep(1)

        # Reset text when connection has been re-established
        wx.CallAfter(self.reconnect.Hide)
        wx.CallAfter(self.reconnect.SetLabel, self.reconnect.GetLabel().strip("."))
    
    def disconnect(self, event, sendmsg=True):
        self.quitting = self.disconnected = True

        # Saving settings
        if self.settings != self.initsettings:
            FILE_WRITE(self.paths["settings"], self.settings)

        # Disable widgets
        if event:
            html_online = self.paths["online"]
            
            self.chatinput.Disable()
            self.send.Disable()
            self.menu_connection_disconnect.Enable(False)

            self.servers.DeselectAll()
            FILE_WRITE(html_online, HTML_SESSION)
            self.userlist.LoadURL(html_online)

            self.conv_info.SetLabel(self.username + " - disconnected")

        # Unhooking hooks
        self.hook_remove()

        # Sending disconnect
        if sendmsg:
            msg = {"datatype": "disconnect"}
            if self.settings != self.initsettings:
                msg["settings"] = self.settings
            self._try_send(msg)
        
        # Joining threads
        threads = thread_enum()
        for thread in [self.thread_stream, self.thread_recv, self.thread_afk]:
            if thread in threads:
                thread.join()

        # Closing socket
        self.clientsocket.shutdown(SHUT_RDWR)
        self.clientsocket.close()
        