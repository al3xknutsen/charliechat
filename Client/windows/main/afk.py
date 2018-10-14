from time import sleep

from core.thread import MultiThread
from core.time_manager import now


class AFKManager:
    def afk_countdown(self):
        '''Counting down to 0 when user is inactive'''
        while self.afktimer > 0:
            if self.quitting or not self.autoafk:
                return
            self.afktimer -= 1
            sleep(1)

        self.afk_actions(True)

    def afk_actions(self, afk, user=None):
        '''Function for handling AFK actions'''

        # Set AFK status
        status = "AFK" if afk else "back"

        # Send info if this user becomes AFK
        if user == None:
            user = self.username
            self.add_msg("", "You are " + status + ".", now(), "black", self.currentroom)
            self.datastream.put(("send", {"datatype": "afk", "status": afk, "room": self.currentroom}))

        self.edit_userlist(user, afk=afk)  # Edit HTML


    def afk_reset(self, event):
        '''Resetting AFK counter on mouse or keyboard actions'''
        if self.afktimer <= 0:
            # Update HTML and restart countdown thread
            self.afk_actions(False)
            self.afktimer = self.afkinit
            afk_thread = MultiThread(self.afk_countdown)
            afk_thread.daemon = True
            afk_thread.start()
        else:
            self.afktimer = self.afkinit
        return True