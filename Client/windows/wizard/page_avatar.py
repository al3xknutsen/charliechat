from os import getcwd, getenv
from os.path import isdir, isfile, split

import wx
from wx.lib.imagebrowser import ImageDialog

from core.global_vars import appdata, host, port
from core.graphics import IMG_RESIZE
from core.network.connection import Connect
from ui.clear_input import ERASE_TEXT
from ui.error_handler import ErrorMsg
from wizard_core import WizardPage


class PageAvatar(WizardPage, Connect, ErrorMsg):
    '''Page for choosing avatar'''
    def __init__(self, username, password, clientsocket):
        self.username = username
        self.password = password
        self.clientsocket = clientsocket
        self._maxsize()

        WizardPage.__init__(self, "Avatar", "Here you can upload an image to use as avatar. \
                            Others will be able to see your avatar when you're connected. \
                            If you don't want an avatar, just ignore this window and press \"Finish\".")

    def _maxsize(self):
        '''Function for setting max size of images
        (Need this in separate function to make it work in settings_avatar.py!!)'''
        self.maxwidth = 300
        self.maxheight = 250

    def UI(self):
        # Supported image formats
        self.formats = ["PNG", "JPG", "GIF", "BMP", "TIFF", "TGA", "PCX", "PNM", "XPM", "IFF", "ICO", "CUR", "ANI"]

        # Sizers
        grid = wx.FlexGridSizer(4, 1, 25, 25)
        widgets = wx.FlexGridSizer(3, 1, 10, 10)
        buttons = wx.FlexGridSizer(1, 0, 10, 10)

        # Widgets
        self.image = wx.StaticBitmap(self.panel)
        self.UI_ERROR(self.panel, grid)
        lbl_filepath = wx.StaticText(self.panel, label="Image path:")
        self.pathinput = wx.TextCtrl(self.panel)
        browse = wx.Button(self.panel, label="Browse...")
        clear = wx.Button(self.panel, label="Clear")
        text_formats = wx.StaticText(self.panel, label="Supported formats:\n" + ", ".join(self.formats))
        text_formats.Wrap(250)
        self.UI_ERROR(self.panel, grid)

        # Adding to sizers
        widgets.AddMany([lbl_filepath, (self.pathinput, 1, wx.EXPAND), (buttons, 0, wx.ALIGN_CENTER)])
        buttons.AddMany([browse, clear])
        grid.AddMany([(self.image, 0, wx.ALIGN_CENTER), (widgets, 1, wx.EXPAND), (text_formats, 0, wx.ALIGN_CENTER)])

        widgets.AddGrowableCol(0)

        # Binding events
        self.pathinput.Bind(wx.EVT_TEXT, self.filepath_input)
        self.pathinput.Bind(wx.EVT_KEY_DOWN, ERASE_TEXT)
        self.Bind(wx.EVT_BUTTON, self.clear, clear)
        self.Bind(wx.EVT_BUTTON, self.browse_path, browse)
        return grid

    def _update_ui(self):
        '''Updating UI when choosing new image'''
        self.Refresh()
        self.panel.Layout()
        self.SetClientSize(self.panel.GetBestSize())
        self.Center(wx.VERTICAL)

    def browse_path(self, event):
        '''Browsing for image'''
        # Choose default folder location
        imginput = self.pathinput.GetValue()
        pictures = getenv("USERPROFILE") + "\\Pictures"
        if isdir(imginput):
            folder = imginput
        elif isfile(imginput) and isdir(split(imginput)[0]):
            folder = split(imginput)[0]
        elif isdir(pictures):
            folder = pictures
        else:
            folder = getcwd()

        # Open image dialog
        dialog = ImageDialog(self, folder)
        dialog.ChangeFileTypes([(f, "*." + f) for f in self.formats])
        dialog.Center()

        # Show image if valid
        if dialog.ShowModal() == wx.ID_OK:
            filepath = dialog.GetFile()
            self.pathinput.SetValue(filepath)
            self.set_image(filepath)

    def filepath_input(self, event):
        '''Function for manually writing image path'''
        path = self.pathinput.GetValue()
        if isfile(path) and path.split(".")[-1].upper() in self.formats:  # Check if format is supported
            self.set_image(path)
        else:
            if self.image.GetBitmap() != wx.NullBitmap:  # Clear if path is non-existent
                self.clear(None)

        # Show error message
        if self.errormsg.IsShown():
            self.errormsg.Hide()
            self.RESET_COLOR(self.pathinput)
            self.panel.Layout()
            self.panel.Refresh()
            self.SetClientSize(self.panel.GetBestSize())

    def set_image(self, path):
        '''Set image preview in UI'''
        self.image.SetBitmap(IMG_RESIZE(path, self.maxwidth, self.maxheight).ConvertToBitmap())
        self._update_ui()

    def clear(self, event):
        '''Clear image preview in UI'''
        if event:
            self.pathinput.Clear()
        self.image.SetBitmap(wx.NullBitmap)
        self._update_ui()

    def _save_avatar(self):
        '''Save avatar to file'''
        bitmap = self.image.GetBitmap()
        if bitmap != wx.NullBitmap:
            bitmap.SaveFile(appdata + "avatars\\" + self.username + ".png", wx.BITMAP_TYPE_PNG)

    def start_chat(self):
        '''Starting main window'''
        self._save_avatar()
        self.quit(None)
        self.CONNECT_LOGIN(host, port, self.username, self.password)

    def gonext(self, event):
        '''Function defining the main action'''
        path = self.pathinput.GetValue()
        if len(path) > 0:
            if not isfile(path):
                self.SHOW_ERRORMSG("Image does not exist!", self.pathinput)
            elif path.split(".")[-1].upper() not in self.formats:
                self.SHOW_ERRORMSG("Unsupported file type!", self.pathinput)
            else:
                self.start_chat()
        else:
            self.start_chat()