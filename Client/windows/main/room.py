from time import sleep, time

import wx

from core.file_manager import FILE_WRITE, FILE_DELETE
from core.security.hash import HASH
from core.time_manager import now
from ui.html.html_vars import HTML_CHAT, HTML_ROOM_WELCOME
from windows.window_addroom import AddRoomWindow
from windows.window_passprompt import RoomPasswordWindow


class RoomManager:
    def add_room(self, event, addtype="send", roomtype=None, roomname=None, roompassword=None):
        '''Adding room'''
        if addtype == "send":  # If user is adding

            # Show window and get variables
            addroom = AddRoomWindow(self)
            if addroom.proceed:
                roomtype, roomname, roompassword, roomwhitelist = addroom.roomtype, \
                addroom.roomname, addroom.roompassword, addroom.roomwhitelist
            else:
                return

        # Adding room to variable
        rtype = self.GET_ROOMTYPE(roomtype)
        room = rtype[roomname] = {}
        if roompassword:
            room["password"] = True

        # Send room data to server if current user created it
        if addtype == "send":
            self.room_unique = None
            room["owner"] = True
            senddata = {"datatype": "add_room", "type": roomtype, "name": roomname}

            if roomtype == "private":
                if roompassword:
                    senddata["password"] = HASH(roompassword)
                elif roomwhitelist != None:
                    senddata["whitelist"] = roomwhitelist + [self.username]

            self.datastream.put(("send", senddata))

            while self.room_unique == None:
                sleep(0.01)
            if not self.room_unique:
                return

        # Updating variables and files
        self.seconds[self.host][roomname] = []
        self.lastupdate[self.host] = time()
        FILE_WRITE(self.paths["lastupdate"], self.lastupdate)
        FILE_WRITE(self.paths["rooms"], self.chatroomdata)
        FILE_WRITE(self.paths["chatlog"](roomname), HTML_CHAT)
        
        # Adding room in tree ctrl
        roomitem = self.roomtypes[roomtype]
        self.chatrooms.AppendItem(roomitem, roomname)
        if not self.chatrooms.IsExpanded(roomitem):
            self.chatrooms.Expand(roomitem)

    def search_rooms(self, event):
        '''Searching rooms'''
        text = event.GetEventObject().GetValue()
        allrooms = self.GET_SERVER()

        # Show all rooms if search input is empty
        if len(text) == 0:
            for roomtype in self.roomtypes:
                self.chatrooms.DeleteChildren(self.roomtypes[roomtype])
                for room in allrooms[roomtype]:
                    self.chatrooms.AppendItem(self.roomtypes[roomtype], room)
        # Finding all rooms containing the search phrase
        else:
            for roomtype in allrooms:
                rooms = []
                if len(allrooms[roomtype]) > 0:
                    for room in allrooms[roomtype]:
                        if text.lower() in room.lower():
                            rooms.append(room)

                # Updating the room overview
                self.chatrooms.DeleteChildren(self.roomtypes[roomtype])
                for r in rooms:
                    self.chatrooms.AppendItem(self.roomtypes[roomtype], r)

    def switch_room(self, event):
        '''Switching room (within current server)'''
        item = event.GetItem()  # Get clicked item

        if item.IsOk():  # If selected room is valid (practically: if rooms are not unselected by UnselectAll)
            roomname = self.chatrooms.GetItemText(item)
            private = self.GET_ROOMTYPE("private")

            if self.chatrooms.GetItemParent(item) == self.chatrooms.GetRootItem():  # Check if clicked room is higher-level
                if roomname == "GLOBAL CHAT":
                    self.currentroom = "GLOBAL CHAT"
            else:
                if roomname in private and "password" in private[roomname]:
                    self.roomprompt = None  # Indication wether password was correct or not (from server)

                    # Show password prompt window if user does not have access yet
                    if roomname not in self.roomaccess:
                        passprompt = RoomPasswordWindow(self, roomname)
                        if passprompt.password == None:  # If window was closed without user inputting password
                            self.chatinput.SetFocus()
                            event.Veto()  # Stop room from being selected
                            return
                        else:
                            # Send data if password input had content
                            self.datastream.put(("send", {"datatype": "roompass", "room": roomname, \
                                                          "password": HASH(passprompt.password)}))

                            while self.roomprompt == None:
                                sleep(0.01)  # Wait for return message
                            if self.roomprompt:
                                self.roomaccess.append(roomname)
                            else:
                                self.chatinput.SetFocus()
                                event.Veto()  # Don't select room if password was wrong
                                return

                self.currentroom = self.chatrooms.GetItemText(item)  # Update current room

            # Load HTML of new room
            if len(self.seconds[self.host][roomname]) == 0:
                self.add_msg("", HTML_ROOM_WELCOME(roomname), now(), "black", roomname)
            self.chattext.LoadURL(self.paths["chatlog"](self.currentroom))
            self.chatrooms.UnselectAll()  # Prevent multiple rooms
            self.chatinput.SetFocus()

    def delete_room(self, event, name=None):
        '''Deleting room'''
        if event == None:  # If someone else deleted room
            for roomtype in self.roomtypes:
                firstroom = self.chatrooms.GetFirstChild(self.roomtypes[roomtype])
                room = firstroom[0]

                if room.IsOk():
                    while self.chatrooms.GetItemText(room) != name:
                        if room.IsOk():
                            room = self.chatrooms.GetNextSibling(room)
                    else:
                        break
                else:
                    continue

        else:  # If this user deleted room
            room = self.roomhittest

        # Get room data
        roomname = self.chatrooms.GetItemText(room)
        parent = self.chatrooms.GetItemParent(room)
        roomtype = self.chatrooms.GetItemText(parent).split(" ")[0].lower()

        # Send room data if this user deleted room
        if event != None:
            self.datastream.put(("send", {"datatype": "del_room", "type": roomtype, "name": roomname}))

        # Delete and save
        wx.CallAfter(self.chatrooms.Delete, room)
        if self.currentroom == self.chatrooms.GetItemText(room):
            wx.CallAfter(self.chatrooms.SelectItem, self.chatrooms.GetFirstChild(self.chatrooms.GetRootItem())[0])

        self.lastupdate[self.host] = time()
        FILE_WRITE(self.paths["lastupdate"], self.lastupdate)
        FILE_DELETE(self.paths["chatlog"](roomname))
        del self.GET_ROOMTYPE(roomtype)[roomname]
        FILE_WRITE(self.paths["rooms"], self.chatroomdata)


    def popup_room(self, event):
        '''Popup menu when right-clicking a room'''
        hittest = self.chatrooms.HitTest(event.GetPosition())  # What is underneath the cursor when clicking?
        roomname = self.chatrooms.GetItemText(hittest[0])
        server = self.GET_SERVER()
        roomowners = [room for roomtype in server for room in server[roomtype] if "owner" in server[roomtype][room]]

        # Show popup menu if right clicking on a room this user owns
        if hittest[1] == wx.TREE_HITTEST_ONITEMLABEL and hittest[0] not in self.roomtypes.values() + \
        [self.chatrooms.GetFirstChild(self.chatrooms.GetRootItem())[0]] and roomname in roomowners:
            self.roomhittest = hittest[0]
            self.panel.PopupMenu(self.roommenu)