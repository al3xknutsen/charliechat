import wx

from ui.clear_input import ERASE_TEXT
from ui.error_handler import ErrorMsg
from ui.templates.widgets import ControlButtons


class AddRoomWindow(wx.Dialog, ControlButtons, ErrorMsg):
    '''Window for adding a chat room'''

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title="Add room")

        # Creating empty variables (for settings)
        self.proceed = False
        self.roompassword = None
        self.roomwhitelist = None

        # Panel
        self.panel = wx.Panel(self)

        # Sizers
        box = wx.BoxSizer()
        self.grid = wx.FlexGridSizer(4, 1, 10, 10)
        settings = wx.FlexGridSizer(0, 2, 5, 5)
        roomtype = wx.GridSizer(1, 2, 5, 5)
        whitelist = wx.FlexGridSizer(1, 3, 5, 5)
        add_remove = wx.GridSizer(2, 1, 5, 5)

        addremsize = (30, -1)  # Size of "add" and "remove" buttons

        # Widgets
        self.UI_ERROR(self.panel, self.grid)
        self.public = wx.RadioButton(self.panel, label="Public")
        self.private = wx.RadioButton(self.panel, label="Private")
        line = wx.StaticLine(self.panel)
        lbl_name = wx.StaticText(self.panel, label="Name:")
        self.name = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
        self.lbl_password = wx.RadioButton(self.panel, label="Password", style=wx.RB_GROUP)
        self.password = wx.TextCtrl(self.panel, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        self.lbl_whitelist = wx.RadioButton(self.panel, label="Whitelist")
        self.whitelist_input = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
        whitelist_add = wx.Button(self.panel, label=">>", size=addremsize)
        whitelist_remove = wx.Button(self.panel, label="<<", size=addremsize)
        self.whitelist = wx.ListBox(self.panel, size=(-1, 100))

        # Adding widgets to sizers
        roomtype.AddMany([(self.public, 0, wx.ALIGN_CENTER), (self.private, 0, wx.ALIGN_CENTER)])
        settings.AddMany([(lbl_name, 0, wx.ALIGN_CENTER_VERTICAL), (self.name, 0, wx.EXPAND), \
                          (self.lbl_password, 0, wx.ALIGN_CENTER_VERTICAL), (self.password, 0, wx.EXPAND), \
                          (self.lbl_whitelist, 0, wx.ALIGN_CENTER_VERTICAL)])
        add_remove.AddMany([whitelist_add, whitelist_remove])
        whitelist.AddMany([(self.whitelist_input, 0, wx.ALIGN_CENTER_VERTICAL), \
                           (add_remove, 0, wx.ALIGN_CENTER_VERTICAL), self.whitelist])
        self.grid.AddMany([(roomtype, 0, wx.EXPAND), (line, 0, wx.EXPAND), (settings, 0, wx.EXPAND), whitelist])
        box.Add(self.grid, flag=wx.ALL, border=20)
        self.panel.SetSizer(box)

        self.add = self.CONTROL_BUTTONS("Add room", "Cancel")

        settings.AddGrowableCol(1)

        self.widgets_all = list(self.panel.GetChildren())  # List of all widgets

        # Binding events
        self.name.Bind(wx.EVT_KEY_DOWN, ERASE_TEXT)
        self.password.Bind(wx.EVT_KEY_DOWN, ERASE_TEXT)
        self.whitelist_input.Bind(wx.EVT_KEY_DOWN, ERASE_TEXT)
        self.Bind(wx.EVT_RADIOBUTTON, self.change_roomtype, self.public)
        self.Bind(wx.EVT_RADIOBUTTON, self.change_roomtype, self.private)
        self.Bind(wx.EVT_RADIOBUTTON, self.change_protection, self.lbl_password)
        self.Bind(wx.EVT_RADIOBUTTON, self.change_protection, self.lbl_whitelist)
        self.Bind(wx.EVT_TEXT_ENTER, self.add_user, self.whitelist_input)
        self.Bind(wx.EVT_BUTTON, self.add_user, whitelist_add)
        self.Bind(wx.EVT_BUTTON, self.remove_user, whitelist_remove)
        self.Bind(wx.EVT_BUTTON, self.add_room, self.add[0])
        self.Bind(wx.EVT_TEXT_ENTER, self.add_room, self.name)
        self.Bind(wx.EVT_TEXT_ENTER, self.add_room, self.password)
        self.Bind(wx.EVT_CLOSE, self.quit)

        self.name.SetFocus()

        # Setting size and showing window
        self.SetClientSize(self.panel.GetBestSize())
        self.Center()
        self.ShowModal()

    def _update_ui(self):
        '''Function for updating UI and resizing window'''
        self.panel.Layout()
        self.SetClientSize(self.panel.GetBestSize())

    def change_roomtype(self, event):
        '''Showing and hiding widgets when changing roomtype'''

        widgets = self.widgets_all[self.widgets_all.index(self.lbl_password):-3]  # List of widgets to be toggled

        # Hide widgets if roomtype is public
        if self.public.GetValue():
            for widget in widgets:
                widget.Hide()

        # Show widgets if roomtype is private (more settings available)
        elif self.private.GetValue():
            if self.lbl_password.GetValue():
                for widget in widgets[:widgets.index(self.lbl_whitelist) + 1]:
                    widget.Show()
                self.password.Show()
            elif self.lbl_whitelist.GetValue():
                for widget in widgets:
                    widget.Show()
                self.password.Hide()

        self._update_ui()

    def change_protection(self, event):
        '''Function for changing protection type (password or whitelist)'''
        widgets = self.widgets_all[self.widgets_all.index(self.lbl_whitelist) + 1:-3]  # List of widgets to be toggled

        # Hide whitelist widgets if password is enabled
        if self.lbl_password.GetValue():
            for widget in widgets:
                widget.Hide()
            self.password.Show()

        # Show whitelist widgets if whitelist is enabled
        elif self.lbl_whitelist.GetValue():
            for widget in widgets:
                widget.Show()
            self.password.Hide()

        self._update_ui()

    def add_user(self, event):
        '''Adding user to whitelist'''

        self.RESET_COLOR(self.name, self.password, self.whitelist_input, self.whitelist)

        # Error handling
        newuser = self.whitelist_input.GetValue()
        if len(newuser) == 0:
            self.SHOW_ERRORMSG("Can't add empty username!", self.whitelist_input)
        elif newuser in self.whitelist.GetItems():
            self.SHOW_ERRORMSG("User already in whitelist!", self.whitelist)
        else:
            # Add user to whitelist
            self.whitelist.Append(newuser)
            self.whitelist_input.Clear()

    def remove_user(self, event):
        '''Removing user from whitelist'''
        selection = self.whitelist.GetSelection()
        if selection != wx.NOT_FOUND:
            self.whitelist.Delete(selection)

    def add_room(self, event):
        '''Adding room when pressing the "Add button'''

        self.RESET_COLOR(self.name, self.password, self.whitelist_input, self.whitelist)

        # Get text from inputs
        name = self.name.GetValue()
        password = self.password.GetValue()
        whitelist = self.whitelist.GetItems()

        if len(name) == 0:
            self.SHOW_ERRORMSG("Please input a name.", self.name)
        elif name in ["GLOBAL CHAT", "Public rooms", "Private rooms"]:
            self.SHOW_ERRORMSG("Cannot create a room with that name!")
        else:
            self.roomname = name
            if self.private.GetValue():
                self.roomtype = "private"

                # Password handling
                if self.lbl_password.GetValue():
                    if len(password) == 0:
                        self.SHOW_ERRORMSG("Please input a password.", self.password)
                    else:
                        self.roompassword = password
                        self.proceed = True

                # Whitelist handling
                elif self.lbl_whitelist.GetValue():
                    if len(whitelist) == 0:
                        self.SHOW_ERRORMSG("Please add users to whitelist.", self.whitelist)
                    else:
                        self.roomwhitelist = whitelist
                        self.proceed = True
                else:
                    self.proceed = True

            else:
                self.roomtype = "public"
                self.proceed = True

            if self.proceed:
                self.quit(None)

    def quit(self, event):
        '''Closing window'''
        self.Destroy()
