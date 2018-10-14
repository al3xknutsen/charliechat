import wx


class KeyManager:
    def chat_hotkeys(self, event):
        '''Define hotkeys for text input'''
        keycode = event.GetKeyCode()
        modifiers = event.GetModifiers()

        # Return
        if keycode == wx.WXK_RETURN:
            # Return+Ctrl/Shift: New line
            if modifiers in [wx.MOD_CONTROL, wx.MOD_SHIFT]:
                text = self.chatinput.GetValue()
                marker = self.chatinput.GetInsertionPoint()

                self.chatinput.SetValue(text[:marker - text[:marker].count("\n")] + "\n" + \
                                        text[marker - text[:marker].count("\n"):])
                self.chatinput.SetInsertionPoint(marker + 2)
            # Send msg
            else:
                self.msg_send(None)

        # Ctrl+A: Select all
        elif keycode == 65 and modifiers == wx.MOD_CONTROL:
            self.chatinput.SetSelection(-1, -1)

        # Ctrl+Backspace: Erase word
        elif keycode == wx.WXK_BACK and modifiers == wx.MOD_CONTROL:
            marker = self.chatinput.GetInsertionPoint()

            len_erased = len(self.chatinput.GetValue()[:marker].rstrip(" ").split(" ")[-1])
            len_spaces = len(self.chatinput.GetValue()[:marker]) - len(self.chatinput.GetValue()[:marker].rstrip(" "))

            self.chatinput.SetValue(" ".join(self.chatinput.GetValue()[:marker].rstrip(" ").split(" ")[:-1]) + \
                                    self.chatinput.GetValue()[marker:])
            self.chatinput.SetInsertionPoint(marker - len_erased - len_spaces - 1)

        # Escape: Clear input
        elif keycode == wx.WXK_ESCAPE:
            self.chatinput.Clear()

        else:
            event.Skip()