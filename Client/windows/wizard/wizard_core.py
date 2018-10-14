import wx

from core.global_vars import __appname__
from ui.templates.widgets import ControlButtons


class WizardPage(wx.Dialog, ControlButtons):
    '''Main page template'''
    def __init__(self, title, text=None, lbl_next="Next >"):
        wx.Dialog.__init__(self, None, title=__appname__)

        self.prevpage = None
        self.nextpage = None
        self.panel = wx.Panel(self)

        # Sizers
        box = wx.BoxSizer()
        self.grid = wx.FlexGridSizer(3, 1, 15, 15)

        # Headline
        headline = wx.StaticText(self.panel, label=title)

        # Setting headline font
        titlefont = headline.GetFont()
        titlefont.SetPointSize(16)
        titlefont.SetWeight(wx.BOLD)
        headline.SetFont(titlefont)

        # Adding to sizer
        self.grid.Add(headline, flag=wx.ALIGN_CENTER)
        if text:
            textbody = wx.StaticText(self.panel, label=text)
            textbody.Wrap(250)
            self.grid.Add(textbody, flag=wx.ALIGN_CENTER)
        self.grid.Add(self.UI(), flag=wx.ALIGN_CENTER)
        box.Add(self.grid, flag=wx.ALL, border=20)
        self.panel.SetSizer(box)

        back, self.next = self.CONTROL_BUTTONS("< Back", lbl_next)

        self.grid.AddGrowableCol(0)

        # Binding events
        if self.prevpage == None:
            back.Disable()
        else:
            self.Bind(wx.EVT_BUTTON, self.goback, back)
        if self.nextpage == None:
            self.next.SetLabel("Finish")
        self.Bind(wx.EVT_BUTTON, self.gonext, self.next)
        self.Bind(wx.EVT_CLOSE, self.quit)

        # Showing window
        self.SetClientSize(self.panel.GetBestSize())
        self.Center()
        self.ShowModal()

    def UI(self):
        '''Placeholder for main UI'''
        return (-1, -1)

    def goback(self, event):
        '''Going to previous page'''
        self.quit(None)
        self.prevpage()

    def gonext(self, event):
        '''Going to next page'''
        self.quit(None)
        self.nextpage()

    def quit(self, event):
        '''CLosing window'''
        self.Destroy()