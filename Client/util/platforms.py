from os import getenv
from platform import system

import wx

from core.global_vars import __appname__


platform_name = system()
if platform_name == "Windows":
    from ctypes import windll
    from pyHook import HookManager


def set_appname():
    if platform_name == "Windows":
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(__appname__)

class Hook:
    def hook_create(self):
        if platform_name == "Windows":
            self.hook.HookMouse()
            self.hook.HookKeyboard()
    
    def hook_remove(self):
        if platform_name == "Windows":
            self.hook.UnhookMouse()
            self.hook.UnhookKeyboard()
        
    def hook_establish(self):
        if platform_name == "Windows":
            self.hook = HookManager()
            self.hook.MouseAll = self.afk_reset
            self.hook.KeyDown = self.afk_reset
            self.hook_create()

def flash_window(windowhandle, sound):
    def play_sound(sound):
        if sound:
            wx.Sound.PlaySound(getenv("WINDIR") + "/Media/tada.wav")
    
    if platform_name == "Windows":
        user32 = windll.user32
        if user32.GetForegroundWindow() != windowhandle:
            user32.FlashWindow(windowhandle, 0)
        play_sound(sound) ## INDENT TO REMOVE SOUND WHEN WINDOW IS ACTIVE
    else:
        play_sound(sound)