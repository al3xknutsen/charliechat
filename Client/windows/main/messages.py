from os import getcwd
from os.path import getmtime, isfile
from re import match

import wx

from core.file_manager import FILE_WRITE
from core.global_vars import codec
from lib.emotes import emote_patterns


class MessageManager:
    def add_msg(self, user, msg, time, color, room, space=True):
        '''Adding message to conversation (HTML file)'''
        private = self.GET_ROOMTYPE("private")
        access = True

        if room in private and "password" in private[room] and room not in self.roomaccess:
            access = False

        if access:  # Check if you have access to room (should always happen - this is in case of permission errors)

            # Display seconds or not, depending on setting
            self.seconds[self.host][room].append(time.split(":")[-1])
            if self.settings["seconds"]:
                timestamp = time.split(" ")[1]
            else:
                timestamp = ":".join(time.split(" ")[1].split(":")[:-1])

            msg = msg.replace("\n", " <br /> ")  # Replace new line with HTML break
            for tag in self.banned_html:
                msg = msg.replace("<" + tag, "&lt;" + tag).replace("</" + tag + ">", "&lt;/" + \
                                  tag + "&gt;").replace("</ " + tag + ">", "&lt;/ " + tag + "&gt;")

            msgsplit = msg.split(" ")
            for wordnum, word in enumerate(msgsplit):

                # Adding HTML links
                if word.startswith("http://") or word.startswith("https://") or word.startswith("ftp://"):
                    msgsplit[wordnum] = "<a href='" + word + "'>" + word + "</a>"
                elif word.startswith("www."):
                    msgsplit[wordnum] = "<a href='http://" + word + "'>" + word + "</a>"

                # Adding emotes
                settings_emotes = self.settings["notemotes"]
                if settings_emotes != "ALL":
                    if len(word) > 0 and word[0] in "cCsSxXToO0:;=-^/\\([{<>|?":
                        for name, pattern in emote_patterns.items():
                            imgpath = getcwd() + "\\images\\emotes\\" + name + ".png"
                            if name not in settings_emotes and match(pattern, word) and isfile(imgpath):
                                msgsplit[wordnum] = "<img src='" + imgpath + "' title='" + name.replace("_", " ").title() + "' />"
                                break

            msg = " ".join(msgsplit)

            # Update HTML file
            htmlfile = self.paths["chatlog"](room)
            html = "<tr style='color:" + color + "'>\n <td "
            if space:
                html += "valign='top'>" + user + "</td>\n <td "
            else:
                html += "colspan=2 "
            html += "class='msg'>" + msg + "</td>\n <td valign='top' title='" + time.split(" ")[1] + "'>" + timestamp + "</td>\n</tr>\n"
            FILE_WRITE(htmlfile, html.encode(codec), "a")

            # Load HTML file (if message was sent to current room)
            if self.currentroom == room:
                wx.CallAfter(self.chattext.LoadURL, htmlfile)
        else:
            # If permission error: send noaccess to server
            self.datastream.put(("send", {"datatype": "noaccess", "room": room}))
    
    
    def startup_data(self, infotype):
        infotype = infotype.lower()
        filepath = self.paths[infotype]
        
        if not isfile(filepath) or (self.userdata["mtime-" + infotype] != None and \
                                  self.userdata["mtime-" + infotype] > getmtime(filepath) + 0.1):
            self._try_send("FETCH-" + infotype.upper())
            return "FETCH"
        else:
            self._try_send("SEND-" + infotype.upper())
            return "SEND"
        