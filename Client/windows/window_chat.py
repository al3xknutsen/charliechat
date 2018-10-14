from Queue import Queue
from copy import deepcopy
from os import getcwd
from os.path import basename, isfile, split
from time import time
from webbrowser import open as openwebbrowser

import wx
from wx.html2 import WebView, EVT_WEBVIEW_NAVIGATING

from core.file_manager import DIR_CREATE, DIR_DELETE, FILE_DELETE, FILE_LOAD, \
    FILE_READ, FILE_WRITE
from core.global_vars import __appname__, __version__, appdata, defaultsettings
from core.network.connection import Connect
from core.network.transfer import RECVMSG
from core.thread import MultiThread
from core.time_manager import now
from core.voice import VoiceManager
from core.webcam import WebcamManager
from ui.clear_input import ERASE_TEXT
from ui.html.html_vars import HTML_CHAT, HTML_LINE, HTML_SESSION, HTML_WELCOME
from util.platforms import set_appname
from windows.main.account import AccountManager
from windows.main.actions import ActionManager
from windows.main.afk import AFKManager
from windows.main.avatar import AvatarManager
from windows.main.color import ColorManager
from windows.main.connection import ConnectionManager
from windows.main.keycontrol import KeyManager
from windows.main.log import LogManager
from windows.main.messages import MessageManager
from windows.main.room import RoomManager
from windows.main.server import ServerManager
from windows.main.settings import SettingsManager, ToggleSettings
from windows.main.transfer import TransferManager
from windows.main.users import ContactManager, PanelUsermode, UserManager


class DictLookup:
    def GET_SERVER(self, server=None):
        '''Lookup server in dict'''
        if server == None:
            server = self.host
        return self.chatroomdata[server]

    def GET_ROOMTYPE(self, roomtype):
        '''Lookup roomtype in dict'''
        return self.GET_SERVER()[roomtype]

class ChatWindow(wx.Frame, Connect, AccountManager, ActionManager, AFKManager, AvatarManager, \
                 ColorManager, ConnectionManager, ContactManager, DictLookup, KeyManager, \
                 LogManager, MessageManager, RoomManager, ServerManager, SettingsManager, \
                 ToggleSettings, TransferManager, UserManager, VoiceManager, WebcamManager):
    
    def __init__(self, username, password, host, port, clientsocket):
        wx.Frame.__init__(self, None, title=__appname__ + " " + __version__)
        
        # Making args class-namespaced
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.clientsocket = clientsocket

        # Path variables
        self.userdir = appdata + self.username + "\\"
        self.dirs = {
            "avatars": appdata + "avatars",
            "chatlogs": self.userdir + "chatlogs",
            "chatlogs_server": lambda: self.userdir + "chatlogs\\" + self.host,
            "thumbs": self.userdir + "thumbs"
        }
        self.paths = {
            "avatar": self.dirs["avatars"] + "\\" + self.username + ".png",
            "chatlog": lambda roomname: self.dirs["chatlogs_server"]() + "\\" + roomname + ".html",
            "contacts": self.userdir + "contacts.txt",
            "lastmsg": self.userdir + "lastmsg.txt",
            "lastupdate": self.userdir + "lastupdate.txt",
            "log": self.userdir + "log.log",
            "online": self.userdir + "online.html",
            "rooms": self.userdir + "rooms.txt",
            "servers": self.userdir + "servers.txt",
            "settings": self.userdir + "settings.txt"
        }

        # Misc variables
        self.new_server = [None, None]
        self.currentroom = "GLOBAL CHAT"
        self.roomaccess = []
        self.seconds = {}
        self.roomtypes = {}
        self.usercolors = {}
        self.datastream = Queue()
#         self.commands = ["afk", "die", "exit", "help"]
        self.colordata = self.roomhittest = None
        self.disconnected = self.quitting = self.reconnecting = False
        self.autoafk = True
        self.banned_html = ["body", "caption", "form", "frame", "head", "html", "iframe", "link", "script", "style", \
                            "table", "tbody", "td", "tfoot", "thead", "tr"]

        # Loading values
        file_room = self.paths["rooms"]
        self.chatroomdata = FILE_LOAD(file_room, {})
        self.serverdata = FILE_LOAD(self.paths["servers"], {self.host: port})
        self.lastupdate = FILE_LOAD(self.paths["lastupdate"], {self.host: time()})

        # Getting startup information from server
        self.userdata = eval(RECVMSG(self.clientsocket))

        # Checking if room file needs to be updated
        if (self.host not in self.lastupdate) or (self.host not in self.chatroomdata) or \
        (self.userdata["mtime-rooms"] > self.lastupdate[self.host] + 0.1):
            self._try_send("SEND-ROOMS")
            self.chatroomdata[self.host] = eval(RECVMSG(self.clientsocket))

            FILE_WRITE(file_room, self.chatroomdata)
            self.lastupdate[self.host] = time()
            FILE_WRITE(self.paths["lastupdate"], self.lastupdate)
        else:
            self._try_send("DONT-SEND-ROOMS")
            self.chatroomdata = eval(FILE_READ(file_room))

        # Managing settings
        settings = self.paths["settings"]
        action_settings = self.startup_data("settings")
        if action_settings == "FETCH":
            response = RECVMSG(self.clientsocket)
            if response == "NO-SETTINGS":
                self.settings = defaultsettings
                self._try_send(self.settings)
            else:
                self.settings = eval(response)
            self.new_settings()
            FILE_WRITE(settings, self.settings)
        else:
            self.settings = eval(FILE_READ(settings))
            self.new_settings()
            if self.userdata["mtime-settings"] == None:
                self._try_send(self.settings)

        self.initsettings = deepcopy(self.settings)
        self.afkinit = self.afktimer = self.settings["afkinterval"]

        # Creating structure of "seconds" variable
        for server in self.chatroomdata:
            self.seconds[server] = {}
            self.seconds[server]["GLOBAL CHAT"] = []
            for room in self.GET_ROOMTYPE("public").keys() + self.GET_ROOMTYPE("private").keys():
                self.seconds[server][room] = []

        # Setting up folders and files
        DIR_CREATE(self.dirs["avatars"])
        DIR_CREATE(self.dirs["chatlogs"])
        DIR_CREATE(self.dirs["chatlogs_server"]())
        DIR_CREATE(self.dirs["thumbs"])
        FILE_WRITE(self.paths["chatlog"](self.currentroom), HTML_CHAT)
        FILE_WRITE(self.paths["online"], HTML_SESSION)

        # Panel
        self.panel = wx.Panel(self)

        # Popup menu: Colors
        self.colorpopup = wx.Menu()
        colors = ["white", "grey", "black", "red", (255, 127, 0), "yellow", "green", "cyan", "blue", "navy", "purple"]
        for color in colors:
            coloritem = wx.MenuItem(self.colorpopup, wx.ID_ANY, " ")
            coloritem.SetBackgroundColour(color)
            self.colorpopup.AppendItem(coloritem)
            self.Bind(wx.EVT_MENU, self.set_color, coloritem)
        self.colorpopup.AppendSeparator()
        colorwheel = self.colorpopup.Append(wx.ID_ANY, "Color wheel...")
        self.Bind(wx.EVT_MENU, self.color_dialog, colorwheel)

        # Popup menu: Rooms
        self.roommenu = wx.Menu()
        room_delete = wx.MenuItem(self.roommenu, wx.ID_ANY, "Delete room")
        self.roommenu.AppendItem(room_delete)
        self.Bind(wx.EVT_MENU, self.delete_room, room_delete)

        # Menu bar
        menubar = wx.MenuBar()
        menu_settings = wx.Menu()
        menu_settings_afk = menu_settings.Append(wx.ID_ANY, "AFK...")
        menu_settings_avatar = menu_settings.Append(wx.ID_ANY, "Avatar...")
        menu_settings_emotes = menu_settings.Append(wx.ID_ANY, "Emotes...")
        if basename(split(getcwd())[0]) == "CharlieChat Dev":
            menu_settings_messages = menu_settings.Append(wx.ID_ANY, "Messages...")  # @UnusedVariable
            menu_settings_sounds = menu_settings.Append(wx.ID_ANY, "Sounds...")  # @UnusedVariable
            menu_settings_text = menu_settings.Append(wx.ID_ANY, "Text...")  # @UnusedVariable
        menu_account = wx.Menu()
        menu_account_switchuser = menu_account.Append(wx.ID_ANY, "Switch user...")
        menu_account_register = menu_account.Append(wx.ID_ANY, "Register new user...")
        menu_account_changepass = menu_account.Append(wx.ID_ANY, "Change password...")
        menu_account_delete = menu_account.Append(wx.ID_ANY, "Delete account")
        menu_connection = wx.Menu()
        self.menu_connection_disconnect = menu_connection.Append(wx.ID_ANY, "Disconnect")
        menu_connection_restart = menu_connection.Append(wx.ID_ANY, "Restart connection")
        menubar.Append(menu_settings, "Settings")
        menubar.Append(menu_account, "Account")
        menubar.Append(menu_connection, "Connection")
        self.SetMenuBar(menubar)

        # Toolbar
        self.toolbar = self.CreateToolBar()
        self.tool_sounds = self.toolbar.AddCheckLabelTool(1, "Seconds", wx.Bitmap("images/speaker.png"))
        self.tool_seconds = self.toolbar.AddCheckLabelTool(2, "Sounds", wx.Bitmap("images/seconds.png"))
        self.tool_afk = self.toolbar.AddCheckLabelTool(3, "AFK", wx.Bitmap("images/afk.png"))
        self.toolbar.Realize()

        self.toolbar.SetToolShortHelp(1, "Toggle sounds")
        self.toolbar.SetToolShortHelp(2, "Toggle display of seconds in chat window")
        self.toolbar.SetToolShortHelp(3, "Toggle whether you are shown as AFK or not")

        # Sizers
        box = wx.BoxSizer()
        grid = wx.FlexGridSizer(2, 1, 10, 10)
        header = wx.FlexGridSizer(1, 2, 10, 10)
        windows = wx.FlexGridSizer(1, 3, 10, 10)
        chat = wx.FlexGridSizer(0, 1, 10, 10)
        chatbuttons = wx.FlexGridSizer(1, 2, 10, 10)
        roomsettings = wx.FlexGridSizer(5, 1, 10, 10)
        conversation = wx.GridSizer(1, 0, 5, 5)

        # Widgets
        webcam = wx.ToggleButton(self.panel, label="Webcam")
        voice = wx.ToggleButton(self.panel, label="Voice")
        self.chattext = WebView.New(self.panel)
        self.add_msg("", HTML_WELCOME, now(), "black", self.currentroom, False)
        FILE_WRITE(self.paths["chatlog"](self.currentroom), HTML_LINE, "a")
        self.chatinput = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
        self.send = wx.Button(self.panel, label="SEND", size=(-1, 50))
        colorbutton = wx.BitmapButton(self.panel, bitmap=wx.Image("images/colorwheel.png", \
                                      wx.BITMAP_TYPE_PNG).ConvertToBitmap(), size=(50, 50))
        usercontainer = wx.Notebook(self.panel)
        users_online = PanelUsermode(self, usercontainer, self.paths["online"])
        self.users_contacts = PanelUsermode(self, usercontainer, "contacts")
        usercontainer.AddPage(users_online, "Online")
        usercontainer.AddPage(self.users_contacts, "Contacts")
        self.conv_info = wx.StaticText(self.panel, label=self.host + ": " + self.username)
        self.reconnect = wx.StaticText(self.panel, label="Reconnecting")
        self.servers = wx.ListBox(self.panel, style=wx.LB_SINGLE)
        server_add = wx.Button(self.panel, label="Add server")
        self.chatrooms = wx.TreeCtrl(self.panel, style=wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | \
                                     wx.TR_ROW_LINES | wx.TR_MULTIPLE)
        room_search = wx.SearchCtrl(self.panel)
        room_add = wx.Button(self.panel, label="Add room")

        # Fonts
        font = self.conv_info.GetFont()
        font.SetPointSize(14)
        self.conv_info.SetFont(font)
        font.SetPointSize(12)
        font.SetWeight(wx.BOLD)
        self.send.SetFont(font)
        font = self.chatinput.GetFont()
        font.SetPointSize(11)
        self.chatinput.SetFont(font)
        font = self.reconnect.GetFont()
        font.SetWeight(wx.BOLD)
        self.reconnect.SetFont(font)

        # Add servers to list widget
        if self.host not in self.serverdata:
            self.serverdata[self.host] = self.port
            FILE_WRITE(self.paths["servers"], self.serverdata)
            self.servers.Append(self.host)
        for lbl_server in self.serverdata:
            self.servers.Append(lbl_server)
        self.servers.SetSelection(self.servers.GetItems().index(self.host))

        # Global room
        root = self.chatrooms.AddRoot("")
        globalroom = self.chatrooms.AppendItem(root, "GLOBAL CHAT")
        self.chatrooms.SetItemBold(globalroom)

        # Loop: roomtypes
        for lbl_roomtype in self.GET_SERVER():
            roomtype = self.chatrooms.AppendItem(root, lbl_roomtype.title() + " rooms")
            self.chatrooms.SetItemBold(roomtype)
            self.roomtypes[lbl_roomtype] = roomtype

            # Loop: rooms
            for lbl_room in self.GET_ROOMTYPE(lbl_roomtype):
                self.chatrooms.AppendItem(roomtype, lbl_room)
                
                # Update HTML for each room
                FILE_WRITE(self.paths["chatlog"](lbl_room), HTML_CHAT)

        self.chatrooms.ExpandAll()
        self.chatrooms.SelectItem(globalroom)

        # Add widgets to sizers
        conversation.AddMany([webcam, voice])
        chat.AddMany([conversation, (self.chattext, 1, wx.EXPAND), (self.chatinput, 1, wx.EXPAND), (chatbuttons, 1, wx.EXPAND)])
        header.AddMany([self.conv_info, (self.reconnect, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)])
        chatbuttons.AddMany([(self.send, 1, wx.EXPAND), colorbutton])
        roomsettings.AddMany([(self.servers, 1, wx.EXPAND), (server_add, 1, wx.EXPAND), (self.chatrooms, 1, wx.EXPAND), \
                              (room_search, 1, wx.EXPAND), (room_add, 1, wx.EXPAND)])
        windows.AddMany([(usercontainer, 1, wx.EXPAND), (chat, 1, wx.EXPAND), (roomsettings, 1, wx.EXPAND)])
        grid.AddMany([(header, 1, wx.EXPAND), (windows, 1, wx.EXPAND)])
        box.Add(grid, 1, wx.ALL | wx.EXPAND, 20)
        self.panel.SetSizer(box)

        # Define growables and ratios
        chat.AddGrowableRow(1, 10)  # Chat height
        chat.AddGrowableRow(2, 2)  # Input height
        chat.AddGrowableCol(0)  # Chat width
        windows.AddGrowableRow(0)  # Users height
        windows.AddGrowableCol(0, 3)  # Users width
        windows.AddGrowableCol(1, 10)  # Chat + input + buttons width
        windows.AddGrowableCol(2, 1)  # Chatrooms width
        roomsettings.AddGrowableCol(0)  # Chatrooms width
        roomsettings.AddGrowableRow(0, 1)  # Chatrooms height
        roomsettings.AddGrowableRow(2, 5)  # Chatrooms height
        chatbuttons.AddGrowableCol(0)  # Send button width
        header.AddGrowableCol(1)  # Reconnect text
        grid.AddGrowableCol(0)  # Conversation info width
        grid.AddGrowableRow(1)  # Widgets height

        # Window size
        self.SetClientSize((1050, 518))
        self.SetMinSize((454, 413))

        # Binding events
        self.Bind(wx.EVT_MENU, self.settings_afk, menu_settings_afk)
        self.Bind(wx.EVT_MENU, self.settings_avatar, menu_settings_avatar)
        self.Bind(wx.EVT_MENU, self.settings_emotes, menu_settings_emotes)
        self.Bind(wx.EVT_MENU, self.switch_user, menu_account_switchuser)
        self.Bind(wx.EVT_MENU, self.register_user, menu_account_register)
        self.Bind(wx.EVT_MENU, self.change_password, menu_account_changepass)
        self.Bind(wx.EVT_MENU, self.delete_user, menu_account_delete)
        self.Bind(wx.EVT_MENU, self.disconnect, self.menu_connection_disconnect)
        self.Bind(wx.EVT_MENU, self.switch_server, menu_connection_restart)
        self.Bind(wx.EVT_TOOL, self.toggle_seconds, self.tool_seconds)
        self.Bind(wx.EVT_TOOL, self.toggle_sounds, self.tool_sounds)
        self.Bind(wx.EVT_TOOL, self.toggle_afk, self.tool_afk)
        self.Bind(wx.EVT_LISTBOX, self.switch_server, self.servers)
        self.Bind(wx.EVT_BUTTON, self.add_server, server_add)
        self.Bind(wx.EVT_TREE_SEL_CHANGING, self.switch_room, self.chatrooms)
        self.chatrooms.Bind(wx.EVT_RIGHT_DOWN, self.popup_room)
        self.Bind(wx.EVT_TEXT, self.search_rooms, room_search)
        room_search.Bind(wx.EVT_KEY_DOWN, ERASE_TEXT)
        self.Bind(wx.EVT_BUTTON, self.add_room, room_add)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.toggle_webcam, webcam)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.toggle_voice, voice)
        self.Bind(EVT_WEBVIEW_NAVIGATING, self.url_navigate, self.chattext)
        self.Bind(wx.EVT_BUTTON, self.popup_color, colorbutton)
        self.chatinput.Bind(wx.EVT_KEY_DOWN, self.chat_hotkeys)
        self.Bind(wx.EVT_BUTTON, self.msg_send, self.send)
        self.Bind(wx.EVT_CLOSE, self.quit)

        # Hiding reconnect (only show when actually reconnecting)
        self.reconnect.Hide()
#         self.contactlist.Hide()
        # Set focus to text input (start writing instantly)
        self.chatinput.SetFocus()

        # Applying settings
        self.apply_settings()
        self.chatinput.SetForegroundColour(self.settings["color"])
        
        # Loading contacts
        action_contacts = self.startup_data("contacts")
        if action_contacts == "FETCH":
            response = RECVMSG(self.clientsocket)
            if response == "NO-CONTACTS":
                if not isfile(self.paths["contacts"]):
                    with open(self.paths["contacts"], "w"):
                        pass
                with open(self.paths["contacts"]) as contactfile:
                    self._try_send(contactfile.read())
            else:
                with open(self.paths["contacts"], "w") as contactfile:
                    contactfile.write(response)
        else:
            if self.userdata["mtime-contacts"] == None:
                with open(self.paths["contacts"]) as contactfile:
                    self._try_send(contactfile.read())
        self.load_contacts()
        
        # Starting threads
        self.thread_stream = MultiThread(self.data_actions)
        self.thread_recv = MultiThread(self.msg_recv)
        self.thread_afk = MultiThread(self.afk_countdown)
        self.thread_stream.daemon = True
        self.thread_recv.daemon = True
        self.thread_afk.daemon = True
        self.thread_stream.start()
        self.thread_recv.start()
        if self.settings["autoafk"]:
            self.thread_afk.start()
        self.init_voice()
        MultiThread(self.empty_voicebuffer).start()

        # Load timestamp of last message (determine if log file needs new date header)
        self.lastmsg = FILE_LOAD(self.paths["lastmsg"], "'" + now().split(" ")[0] + "'")

        # Add users to list of connected users
        self.add_user(self.username, self.userdata["mtime-avatar"])
        for user in self.userdata["users"]:
            self.add_user(user, self.userdata["users"][user]["mtime-avatar"], user in self.userdata["afks"], \
                             self.userdata["users"][user]["color"])
        
        # Set icon (REMOVE set_appname WHEN .exe)
        set_appname()
        self.SetIcon(wx.Icon("images/testicon.ico"))
        
        self.hook_establish()

        # Showing window
        self.Center()
        self.Show()

    def url_navigate(self, event):
        '''Open web browser when clicking on HTML link'''
        url = event.GetURL()
        if not isfile(url):
            openwebbrowser(url)
            event.Veto()

    def quit(self, event, sendmsg=True):
        '''Quitting the application'''

        self.Hide()

        # Disconnecting
        if not self.disconnected:
            self.disconnect(None, sendmsg)

        # Handling files
        if event:
            FILE_WRITE(appdata + "new_server.txt", [None, None])
        DIR_DELETE(self.dirs["chatlogs"])
        DIR_DELETE(self.dirs["thumbs"])
        FILE_DELETE(self.paths["online"])

        # Destroy window
        self.Destroy()
