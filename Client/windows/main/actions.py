from time import sleep

from core.file_manager import FILE_READ, FILE_WRITE
from core.time_manager import now
from core.voice import VoiceManager
from core.webcam import WebcamManager
from util.platforms import flash_window
from windows.main.log import LogManager


voice = VoiceManager()
voice.init_voice()

webcam = WebcamManager()
webcam.init_webcam()

class ActionManager(LogManager):
    def data_actions(self):
        '''Handling all data sent and received'''

#         nolog = ["add_room", "afk", "avatar-change", "avatar-fetch", "avatar-send", "color", \
#                  "del_room", "del_user", "noaccess", "roompass", "voice", "webcam"]
        
#         log = ["chat", "command", "connect", "disconnect"]

        while True:
            if self.quitting:
                return

            sleep(0.01)  # Preventing CPU gobbling
            if not self.datastream.empty():
                data_raw = self.datastream.get()  # Get next message from datastream
                data = data_raw[1]
                datatype = data["datatype"]

                ### SENDING MESSAGE ###
                if data_raw[0] == "send":
                    time_now = now()

                    # Write log
                    if datatype == "add_room":
                        self.write_log(time_now, "You added " + data["type"] + " room: " + data["name"])
                    elif datatype in self.log_commands:
                        self.write_log(time_now, self.username + ": " + data["msg"], self.currentroom)

                    self._try_send(data)

                    if datatype in self.log_commands:
                        # Commands
                        if data["msg"] in ["/" + c for c in self.commands]:
                            if data["msg"] == "/help":
                                self.add_msg("", "You need help!", time_now, "black", self.currentroom)
                            elif data["msg"] == "/afk":
                                self.afktimer = 0
                                self.afk_actions(True)
                        # Chat messages
                        else:
                            self.add_msg(self.username, data["msg"], time_now, self.settings["color"], self.currentroom)

                ### RECEIVING MESSAGE ###
                elif data_raw[0] == "recv":
                    print datatype

                    # User connecting #
                    if datatype == "connect":
                        self.write_log(data["time"], data["user"] + " connected.")
                        self.add_user(data["user"], data["mtime-avatar"], color=data["color"])
                        self.add_msg("", data["user"] + " connected.", data["time"], "black", self.currentroom)

                    # Sending avatar to server #
                    elif datatype == "avatar-send":
                        if data["value"] == True:
                            self._try_send({"datatype": "avatar-send", "value": FILE_READ(self.paths["avatar"], True)})

                    # Fetching avatar from server #
                    elif datatype == "avatar-fetch":
                        if data["value"] != False:
                            FILE_WRITE(self.dirs["avatars"] + "\\" + data["user"] + ".png", data["value"], "wb")
                            self.avatar_thumb(data["user"])
                            self.edit_userlist(data["user"], avatar=True)

                    # Changing avatar #
                    elif datatype == "avatar-change":
                        if data["value"] == "delete":
                            self.avatar_delete(data["user"])
                        else:
                            self.avatar_change(data["user"], data["value"])
                    
                    elif datatype == "contact-exists":
                        if data["value"]:
                            with open(self.paths["contacts"], "a") as contactfile:
                                contactfile.write(data["contact"] + "\n")
                            self.users_contacts.widget.Append([data["contact"]])
                            self.users_contacts.contact_name.Clear()
                    
                    # Changing text color
                    elif datatype == "color":
                        self.usercolors[data["user"]] = data["value"]

                    # Chat message #
                    elif datatype == "chat":
                        room = data["room"] if "room" in data else "GLOBAL CHAT"
                        self.write_log(data["time"], data["user"] + ": " + data["msg"], room)
                        self.add_msg(data["user"], data["msg"], data["time"], self.usercolors[data["user"]], room)

                    # Command #
                    elif datatype == "command":
                        self.write_log(data["time"], data["user"] + ": " + data["msg"])
                        if data["msg"] == "/help":
                            self.add_msg("", data["user"] + " needs help!", data["time"], "black", self.currentroom)

                    # AFK #
                    elif datatype == "afk":
                        if data["status"]:
                            self.write_log(data["time"], data["user"] + " is AFK.")
                            self.add_msg("", data["user"] + " is AFK.", data["time"], "black", self.currentroom)
                        else:
                            self.write_log(data["time"], data["user"] + " is back.")
                            self.add_msg("", data["user"] + " is back.", data["time"], "black", self.currentroom)

                        self.afk_actions(data["status"], data["user"])

                    # Adding room #
                    elif datatype == "add_room":
                        self.write_log(data["time"], data["user"] + " added " + data["type"] + " room: " + data["name"])
                        self.add_room(None, "recv", data["type"], data["name"], "password" in data)

                    # Is room unique? #
                    elif datatype == "room_unique":
                        self.room_unique = data["value"]

                    # Was room password correct? #
                    elif datatype == "roompass":
                        self.roomprompt = data["proceed"]

                    # Deleting room #
                    elif datatype == "del_room":
                        self.write_log(data["time"], data["user"] + " deleted " + data["type"] + " room: " + data["name"])
                        self.delete_room(None, data["name"])
                    
                    elif datatype == "webcam":
                        webcam.recv_camstream(data["data"])
                    
                    elif datatype == "voice":
                        voice.recv_voice(data["data"])
                    
                    # User disconnecting #
                    elif datatype == "disconnect":
                        self.write_log(data["time"], data["user"] + " disconnected.")
                        self.edit_userlist(data["user"], False)
                        self.add_msg("", data["user"] + " disconnected.", data["time"], "black", self.currentroom)

                    # Flash window and play sound (if window doesn't have focus)
                    if (datatype not in ["add_room", "avatar-change", "avatar-fetch", "avatar-send", \
                                         "del_room", "roompass", "room_unique", "voice", "webcam"]):
                        flash_window(self.GetHandle(), self.settings["sounds"])
