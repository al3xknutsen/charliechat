from core.file_manager import FILE_READ
from core.global_vars import __appname__, __version__


HTML_CHAT = FILE_READ("ui\\html\\html_chat.html")
HTML_SESSION = FILE_READ("ui\\html\\html_users.html")

HTML_WELCOME = "Welcome to " + __appname__ + " " + __version__ + "! <br />" + \
'''<a href='http://mystic.ddns.net/project/CharlieChat/Suggestions' \
    title='http://mystic.ddns.net/project/CharlieChat/Suggestions'>Suggest feature</a> &ndash; \
<a href='http://mystic.ddns.net/project/CharlieChat/Bugs' \
    title='http://mystic.ddns.net/project/CharlieChat/Bugs'>Report bug</a> &ndash; \
<a href='http://mystic.ddns.net/projects/extra/' \
    title='http://mystic.ddns.net/projects/extra/'>Submit error</a> &ndash; \
<a href='http://mystic.ddns.net/project/CharlieChat/Changelog' \
    title='http://mystic.ddns.net/project/CharlieChat/Changelog'>Changelog</a>'''



HTML_LINE = "<tr><td colspan=3><hr /></td></tr>\n"

def HTML_USER(user, afk=False):
    '''User HTML without avatar'''
    return "\n<div><span style='color: " + ("grey" if afk else "black") + "'>" + user + "</span></div>"

def HTML_USER_AVATAR(user, thumbpath, afk=False):
    '''User HTML with avatar'''
    return "\n<div><img src=" + thumbpath + "\\" + user + ".png /><span style='color: " + \
        ("grey" if afk else "black") + "'>" + user + "</span></div>"

def HTML_ROOM_WELCOME(room):
    '''Welcome message when entering room'''
    return "Welcome to " + room + "!"
