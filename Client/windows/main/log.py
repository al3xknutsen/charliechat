from core.file_manager import FILE_WRITE
from core.global_vars import codec

class LogManager:
    log_commands = ["chat", "comment", "connect", "disconnect"] # Not AFK??
    
    def write_log(self, time, msg, room="GLOBAL CHAT"):
        '''Function for writing to log file'''
        date = time.split(" ")[0]
        if self.lastmsg != date:
            FILE_WRITE(self.paths["log"], "--- " + date + " ---\n", "a")  # Date headline

            # Save date of last message
            self.lastmsg = date
            FILE_WRITE(self.paths["lastmsg"], "'" + self.lastmsg + "'")

        # Write to log file
        if room == "GLOBAL CHAT":
            roommsg = ""
        else:
            roommsg = "|" + room
        FILE_WRITE(self.paths["log"], ("[" + time.split(" ")[1] + roommsg + "] " + msg + "\n").encode(codec), "a")