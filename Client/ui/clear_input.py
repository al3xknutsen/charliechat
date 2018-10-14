import wx


def ERASE_TEXT(event):
    '''Function for erasing input on Ctrl+Backspace or Esc'''
    keycode = event.GetKeyCode()
    modifiers = event.GetModifiers()

    if (keycode == wx.WXK_BACK and modifiers == wx.MOD_CONTROL) or keycode == wx.WXK_ESCAPE:
        event.GetEventObject().Clear()
    else:
        event.Skip()
