from copy import deepcopy
from threading import enumerate as thread_enum

import wx

from core.file_manager import FILE_WRITE, FILE_READ
from core.global_vars import defaultsettings
from core.thread import MultiThread
from core.time_manager import now
from util.platforms import Hook
from windows.settings.settings_afk import AFKSettings
from windows.settings.settings_avatar import AvatarSettings
from windows.settings.settings_emotes import EmoteSettings


class SettingsManager:
    def new_settings(self):
        '''Add new settings'''
        # Creating new settings
        for key, value in defaultsettings.items():
            if key not in self.settings:
                self.settings[key] = value
        # Deleting old settings
        for key in deepcopy(self.settings):
            if key not in defaultsettings:
                del self.settings[key]

    def apply_settings(self):
        '''Apply all settings to corresponding widgets'''
        self.toolbar.ToggleTool(1, self.settings["sounds"])
        self.toolbar.ToggleTool(2, self.settings["seconds"])

    def settings_afk(self, event):
        '''Edit AFK settings'''
        new_afk = AFKSettings(self.settings["autoafk"], self.settings["afkinterval"]).new_settings

        if new_afk != None:
            # Save settings
            self.settings["autoafk"], self.settings["afkinterval"] = new_afk
            FILE_WRITE(self.paths["settings"], self.settings)
            self.autoafk = self.settings["autoafk"]

            # Start threads if auto-afk
            if self.settings["autoafk"]:
                self.afkinit = self.afktimer = self.settings["afkinterval"]
                if self.thread_afk not in thread_enum():
                    self.thread_afk = MultiThread(self.afk_countdown)
                    self.thread_afk.daemon = True
                    self.thread_afk.start()

    def settings_avatar(self, event):
        '''Edit avatar settings'''
        path_avatar = self.paths["avatar"]
        avatar = AvatarSettings(self.username).new_settings

        if avatar != None:
            # Delete avatar
            if avatar == wx.NullBitmap:
                self._avatar_delete(self.username)
                value = "delete"
            # Save new avatar
            else:
                self.avatar_change(self.username, avatar)
                value = FILE_READ(path_avatar, True)

            self.datastream.put(("send", {"datatype": "avatar-change", "value": value}))


    def settings_emotes(self, event):
        '''Edit emote settings'''
        new_emotes = EmoteSettings(self.settings["notemotes"]).new_settings
        if new_emotes != None:
            self.settings["notemotes"] = new_emotes
            FILE_WRITE(self.paths["settings"], self.settings)

    def avatar_change(self, user, avatar):
        '''Function for creating/changing avatar'''
        path_avatar = self.dirs["avatars"] + "\\" + user + ".png"
        time_now = now()
        
        # Write to log
        if user == self.username:
            self.write_log(time_now, "You changed your avatar.")
        else:
            self.write_log(time_now, user + " changed their avatar.")

        # Save avatar
        if type(avatar) == wx.Bitmap:
            avatar.SaveFile(path_avatar, wx.BITMAP_TYPE_PNG)
        else:
            FILE_WRITE(path_avatar, avatar, "wb")
        self.avatar_thumb(user)  # Create thumbnail for user list

        # Update user list
        self.edit_userlist(user, avatar=True)
        wx.CallAfter(self.userlist.LoadURL, self.paths["online"])

class ToggleSettings(Hook):
    def toggle_sounds(self, event):
        '''Toggle if sounds should be played when receiving messages'''
        self.settings["sounds"] = self.tool_sounds.IsToggled()

    def toggle_seconds(self, event):
        '''Toggle if seconds sould be displayed in the conversation window'''
        file_html = self.paths["chatlog"](self.currentroom)
        roomseconds = self.seconds[self.host][self.currentroom]

        # Get HTML of conversation window
        htmldoc = FILE_READ(file_html)

        self.settings["seconds"] = self.tool_seconds.IsToggled()  # Update setting

        # Parse the HTML and inject/extract the seconds
        splithtml = htmldoc.split("title=\"")
        newhtml = splithtml[0]

        for x in range(len(roomseconds)):
            splitdate = splithtml[1:][x].split("\">")
            newhtml += "title=\"" + splitdate[0] + "\">"

            if self.tool_seconds.IsToggled():
                self.settings["seconds"] = True
                newhtml += splitdate[1].split("</td>")[0] + ":" + str(roomseconds[x])
            else:
                self.settings["seconds"] = False
                newhtml += ":".join(splitdate[1].split("</td>")[0].split(":")[:-1])

            newhtml += "</td>" + "</td>".join(splitdate[1].split("</td>")[1:]) + "\">" + "\">".join(splitdate[2:])
        newhtml = newhtml[:-2] + newhtml[-2:].replace("\">", "")

        # Update and reload HTML file
        FILE_WRITE(file_html, newhtml)
        self.chattext.LoadURL(file_html)

    def toggle_afk(self, event):
        '''Toggle AFK status'''

        # Stop AFK countdown if AFK
        if self.tool_afk.IsToggled():
            self.autoafk = False
            self.hook_remove()
            self.afk_actions(True)

        else:
            self.afk_actions(False)

            # Start AFK countdown if Auto-AFK
            if self.settings["autoafk"]:
                self.autoafk = True
                self.hook_create()
                
                self.thread_afk = MultiThread(self.afk_countdown)
                self.thread_afk.daemon = True
                self.thread_afk.start()