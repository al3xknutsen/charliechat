import wx

from core.file_manager import FILE_DELETE
from core.graphics import IMG_RESIZE
from core.time_manager import now


class AvatarManager:
    def avatar_delete(self, user):
        '''Function for deleting avatar'''
        time_now = now()
        
        # Write to log
        if user == self.username:
            self.write_log(time_now, "You deleted your avatar.")
        else:
            self.write_log(time_now, user + " deleted their avatar.")

        # Update user list
        self.edit_userlist(user, avatar=False)
        wx.CallAfter(self.userlist.LoadURL, self.paths["online"])

        # Delete avatar files
        filename = "\\" + user + ".png"
        FILE_DELETE(self.dirs["thumbs"] + filename)
        FILE_DELETE(self.dirs["avatars"] + filename)

    def avatar_thumb(self, user):
        '''Function for creating avatar thumb in user list'''
        filename = "\\" + user + ".png"
        thumbpath = self.dirs["thumbs"] + filename

        # Resize and sace
        thumb = IMG_RESIZE(self.dirs["avatars"] + filename, 50, 50)
        thumb.ConvertToBitmap()
        thumb.SaveFile(thumbpath, wx.BITMAP_TYPE_PNG)
