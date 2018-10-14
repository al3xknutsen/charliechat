from os.path import isfile, getmtime

from core.file_manager import FILE_READ, FILE_WRITE
from core.network.transfer import SENDMSG
from ui.html.html_vars import HTML_USER, HTML_USER_AVATAR

import wx
from wx.html2 import WebView
from wx.lib.agw.ultimatelistctrl import PyImageList, UltimateListCtrl, ULC_LIST,\
    ULC_SHOW_TOOLTIPS


class UserManager:
    def edit_userlist(self, user, exist=True, afk=None, avatar=None):
        '''Function for editing user list'''
        
        html_online = self.paths["online"]
        
        # Loading and parsing HTML
        users_online = FILE_READ(html_online).split("\n")
        line_body = users_online.index("\t<body>") + 1
        users = users_online[line_body:]  # Get all lines containing usernames

        for line in users:
            if line.split("</span>")[0].split(">")[-1] == user:  # Find current user
                if not exist:
                    users.remove(line)
                else:
                    linepos = users.index(line)
                    sep1 = "<span style='color: "

                    # Change color (AFK)
                    if afk != None:
                        sep2 = "'>"
                        start, temp_color = line.split(sep1)
                        color, end = temp_color.split(sep2)

                        color = "grey" if afk else "black"

                        users[linepos] = start + sep1 + color + sep2 + end

                    # Change avatar
                    if avatar != None:
                        tag_outer = "<div>"
                        html_inner = line.split(tag_outer, 1)[1]
                        html_img = "<img src="

                        if html_inner.startswith(html_img) and avatar == False:
                            users[linepos] = tag_outer + html_inner.split("/>", 1)[1]
                        elif html_inner.startswith(sep1) and avatar:
                            users[linepos] = tag_outer + html_img + self.dirs["thumbs"] + \
                            "\\" + user + ".png />" + html_inner

        # Update HTML and GUI
        users_online[line_body:] = users
        FILE_WRITE(html_online, "\n".join(users_online))
        wx.CallAfter(self.userlist.LoadURL, html_online)

    def add_user(self, user, mtime_avatar, afk=False, color=None):
        '''Adding user, and defining AFK status'''
        
        html_online = self.paths["online"]
        
        if color != None:
            self.usercolors[user] = color

        filename = "\\" + user + ".png"
        avatar = self.dirs["avatars"] + filename

        # Fetch avatar
        if not isfile(avatar) or (mtime_avatar != None and mtime_avatar > getmtime(avatar) + 0.3):
            FILE_WRITE(html_online, HTML_USER(user, afk), "a")
            self.datastream.put(("send", {"datatype": "avatar-fetch", "user": user}))
        # Add user with avatar
        else:
            self.avatar_thumb(user)
            FILE_WRITE(html_online, HTML_USER_AVATAR(user, self.dirs["thumbs"], afk), "a")
            if user == self.username:
                self.datastream.put(("send", {"datatype": "avatar-send"}))

        wx.CallAfter(self.userlist.LoadURL, html_online)


class ContactManager:
    def load_contacts(self):
        contactlist = self.users_contacts.widget
        thumblist = PyImageList(50, 50)
        
        with open(self.paths["contacts"]) as contactfile:
            for contact_id, contact in enumerate(contactfile.read().split("\n")[:-1]):
                self.users_contacts.widget.InsertImageStringItem(contact_id, contact, contact_id)
        
        print contactlist.GetItemCount()
        
        for contact_id in range(contactlist.GetItemCount()):
            avatarpath = self.dirs["avatars"] + "\\" + contactlist.GetItemText(contact_id) + ".png"
            print avatarpath
            if isfile(avatarpath):
                avatar = wx.Bitmap(avatarpath)
            else:
                avatar = wx.EmptyBitmap(50, 50)
            thumblist.Add(avatar)
        
        contactlist.AssignImageList(thumblist, wx.IMAGE_LIST_SMALL)


class PanelUsermode(wx.Panel):
    def __init__(self, parent, notebook, windowtype):
        wx.Panel.__init__(self, notebook)
        
        self.parent = parent
        self.windowtype = windowtype
        
        box = wx.BoxSizer()
        grid = wx.FlexGridSizer(0, 1, 5, 5)
        
        if self.windowtype == self.parent.paths["online"]:
            self.widget = self.parent.userlist = WebView.New(self)
            self.widget.LoadURL(self.windowtype)
        elif self.windowtype == "contacts":
            self.widget = UltimateListCtrl(self, agwStyle=ULC_LIST | ULC_SHOW_TOOLTIPS)
        
        grid.Add(self.widget, 1, wx.EXPAND)
        box.Add(grid, 1, wx.EXPAND)
        
        grid.AddGrowableCol(0)
        grid.AddGrowableRow(0)
        
        if self.windowtype == "contacts":
            self.contact_name = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
            add_contact = wx.Button(self, label="Add contact")
            grid.AddMany([(self.contact_name, 1, wx.EXPAND), (add_contact, 1, wx.EXPAND)])
            self.Bind(wx.EVT_BUTTON, self.add_contact, add_contact)
            self.contact_name.Bind(wx.EVT_KEY_DOWN, self.add_contact_hotkey)
        
        self.SetSizer(box)
    
    def add_contact(self, event):
        contact = self.contact_name.GetValue()
        SENDMSG({"datatype": "contact-add", "contact": contact}, self.parent.clientsocket)
    
    def add_contact_hotkey(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.add_contact(None)
        else:
            event.Skip()
