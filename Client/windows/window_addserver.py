import wx

from ui.clear_input import ERASE_TEXT
from ui.error_handler import ErrorMsg
from ui.templates.widgets import ControlButtons


class AddServerWindow(wx.Dialog, ControlButtons, ErrorMsg):
    '''Window for adding a server'''

    def __init__(self, parent, servers):
        wx.Dialog.__init__(self, parent, title="Add server")

        self.servers = servers
        self.proceed = False

        # Panel
        self.panel = wx.Panel(self)

        # Sizers
        box = wx.BoxSizer()
        self.grid = wx.FlexGridSizer(1, 1, 10, 10)
        settings = wx.FlexGridSizer(2, 2, 7, 10)

        # Widgets
        self.UI_ERROR(self.panel, self.grid)
        lbl_addr = wx.StaticText(self.panel, label="Host/IP:")
        lbl_port = wx.StaticText(self.panel, label="Port:")
        self.addr = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
        self.port = wx.SpinCtrl(self.panel, value="25000", style=wx.SP_ARROW_KEYS | wx.TE_PROCESS_ENTER | \
                                wx.TE_LEFT, min=0, max=100000)

        # Adding widgets to sizers
        settings.AddMany([(lbl_addr, 0, wx.ALIGN_CENTER_VERTICAL), (self.addr, 0, wx.EXPAND), \
                          (lbl_port, 0, wx.ALIGN_CENTER_VERTICAL), self.port])
        self.grid.Add(settings, flag=wx.ALIGN_CENTER)
        box.Add(self.grid, 1, wx.ALL, 20)
        self.panel.SetSizer(box)

        add = self.CONTROL_BUTTONS("Add server", "Cancel")

        # Binding events
        self.addr.Bind(wx.EVT_KEY_DOWN, ERASE_TEXT)
        self.Bind(wx.EVT_TEXT_ENTER, self.add_server, self.addr)
        self.Bind(wx.EVT_TEXT_ENTER, self.add_server, self.port)
        self.Bind(wx.EVT_BUTTON, self.add_server, add[0])
        self.Bind(wx.EVT_CLOSE, self.quit)

        # Setting size and showing window
        self.SetClientSize(self.panel.GetBestSize())
        self.Center()
        self.ShowModal()

    def add_server(self, event):
        '''Adding server'''

        self.RESET_COLOR(self.addr)

        # Getting text from inputs
        addr = self.addr.GetValue()
        port = self.port.GetValue()

        # Show error messages
        if len(addr) == 0:
            self.SHOW_ERRORMSG("Please input a host/IP address.", self.addr)
        elif port == 0:
            self.SHOW_ERRORMSG("Please choose a port.")  # SetBackgroundColour not working on SpinCtrl
        elif addr in self.servers:
            self.SHOW_ERRORMSG("Server already exists!")

        # Proceed
        else:
            self.proceed = True
            self.serveraddr = addr
            self.serverport = port

            self.quit(None)

    def quit(self, event):
        '''Closing window'''
        self.Destroy()
