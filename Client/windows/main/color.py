import wx

from core.file_manager import FILE_WRITE


class ColorManager:
    def set_color(self, event):
        '''Set and apply color to your messages'''
        # Get color and convert to hex
        if event:
            newcolor = self.colorpopup.FindItemById(event.GetId()).GetBackgroundColour()
        else:
            newcolor = self.colorpicker.GetColourData().GetColour()
        newcolor = newcolor.GetAsString(wx.C2S_HTML_SYNTAX)

        # Save color
        self.settings["color"] = color = newcolor
        FILE_WRITE(self.paths["settings"], self.settings)
        self.datastream.put(("send", {"datatype": "color", "value": color}))

        # Apply color
        self.chatinput.SetForegroundColour(color)
        if event:
            self.chatinput.SetFocus()

    def popup_color(self, event):
        '''Popup menu for color list'''
        self.panel.PopupMenu(self.colorpopup)

    def color_dialog(self, event):
        '''Color picker'''

        # Show color picker
        self.colorpicker = wx.ColourDialog(self, self.colordata)

        # Apply color and corresponding settings, and update settings file
        if self.colorpicker.ShowModal() == wx.ID_OK:
            self.set_color(None)

        self.chatinput.SetFocus()