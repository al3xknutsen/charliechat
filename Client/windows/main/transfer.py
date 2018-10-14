from socket import error as socketerror
from time import sleep

from core.network.transfer import SENDMSG, RECVMSG
from core.thread import MultiThread
from core.time_manager import now
from windows.main.commands import CommandManager


class TransferManager(CommandManager):
    def _try_send(self, msg):
        '''Try sending message until connection is re-established'''
        while self.reconnecting:
            sleep(0.02)
        SENDMSG(msg, self.clientsocket)

    def msg_send(self, event):
        '''Sending message when pressing the "Send" button (redirecting to datastream)'''
        msg = self.chatinput.GetValue()
        
        ### / PUT THIS INTO COMMAND MANAGER / ###
        if len(msg.strip(" ")) > 0:  # Strip spaces and check for content
            if msg in ["/" + c for c in self.commands]:  # Check for commands
                # Quit if "/exit", else send
                if msg == "/exit":
                    self.write_log(now(), self.username + ": " + msg)
                    self.quit(None)
                else:
                    msgsend = {"datatype": "command", "msg": msg}
                    if self.currentroom != "GLOBAL CHAT":
                        msgsend["room"] = self.currentroom
                    self.datastream.put(("send", msgsend))
            else:
                # HAN SOM SKRIVER DETTE PROGRAMMET ER GOD!
                # DE SOM TESTER DETTE PROGRAMMET ER GODE!

                # Sending all chat messages
                msgsend = {"datatype": "chat", "msg": msg}
                if self.currentroom != "GLOBAL CHAT":
                    msgsend["room"] = self.currentroom
                self.datastream.put(("send", msgsend))
            self.chatinput.Clear()
    
    
    def msg_recv(self):
        '''Receiving all messages from server, and redirecting to datastream'''
        while True:
            try:
                self.datastream.put(("recv", eval(RECVMSG(self.clientsocket))))
            except (socketerror, ValueError):
                if not hasattr(self, "quitting") or self.quitting:
                    return

                # Reconnecting
                self.reconnecting = True
                MultiThread(self.reconnect_msg).start()
                while not self.reconnect_client():
                    sleep(0.02)
                self.reconnecting = False
                