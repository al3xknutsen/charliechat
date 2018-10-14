emote_patterns = {
    "smile": r"([:=]-?[\)\}]$)|([\(\{]-?[:=]$)",
    "smile_ultra": r"([cC]-?[:=]$)|([oO0]u[oO0]$)",
    "smile_square": r"([:=]-?\]$)|(\[-?[:=]$)",
    "smile_kitty": r"[:=]-?3$",

    "grin": r"[:=]-?D$",
    "tongue": r"[:=]-?[Pp]$",
    "laugh": r"[xX]-?D$",
    "laugh_tongue": r"[xX]-[pP]$",
    "laugh_smile": r"([xX]-?[\)\}]$)|([\[\{]-?[xX]$)",
    "laugh_smile_square": r"([xX]-?\]$)|(\[-?[xX]$)",
    "laugh_kitty": r"[xX]-?3$",
    "laugh_ultra": r"[cC]-?[xX]$",

    "wink": r"(;-?[\)\}]$)|([\(\{]-?;$)",
    "wink_square": r"(;-?\]$)|(\[-?;$)",
    "wink_ultra": r"[cC]-?;$",

    "sad": r"([:=]-?[\(\{]$)|([\)\}]-?[:=]$)",
    "sad_square": r"([:=]-?\[$)|(\]-=[:=]$)",
    "sad_ultra": r"([:=]-?[cC]$)|([oO0]n[oO0]$)",

    "cry": r"((;|[:=]')-?[\(\{]$)|([\)\}]-?(;|'[:=])$)|(T[\._n]T$)",
    "cry_square": r"((;|[:=]')-?\[$)|(\]-?(;|'[:=])$)",
    "cry_ultra": r"(;|[:=][',])-?[cC]$",

    "dead": r"([xX]-?[\(\{cC]$)|([\)\}]-?[xX]$)",
    "dead_square": r"([xX]-?\[$)|(\]-?[xX]$)",
    "dead_square_double": r"[xX][\[\]][xX]$",
    "dead_ultra": r"[xX]-?[cC]$",

    "angry": r"(>[:=]-?[\(\{]$)|([\)\}]-?[:=]<$)",
    "angry_ultra": r">[:=]-?[cC]",
    "grumpy": r"(>[:=]-?\[$)|(\]-?[:=]<$)",

    "evil": r"(>[:=]-?[\)\}]$)|([\(\{]-?[:=]<$)",
    "evil_ultra": r"[cC]-?[:=]<",
    "evil_square": r"(>[:=]-?\]$)|(\[-?[:=]<$)",

    "sceptical": r"([:=]-?[/\\]$)|([/\\]-?[:=]$)",
    "scared": r"([:=]-?[sS]$)|([sS]-?[:=]$)",
    "surprised": r"([:=]-?[oO0]$)|([oO0]-?[:=]$)",
    "neutral": r"([:=]-?\|$)|(\|-?[:=]$)",
    "thinking": r"([:=]-?\?$)|(\?-?[:=]$)|((?i)\(think\)$)",
    "sleeping": r"(\|-?[\)\}]$)|([\(\{]-?\|$)|((?i)\(zzz\)$)",
    "sleeping_square": r"(\|-?\]$)|(\[-?\|$)",
    "teeth": r"[:=]-?B$",

    "gazing": r"[oO0]_[oO0]$",
    "doh": r"(>[\._]<$)|((?i)\(doh\)$)",
    "sigh": r"-[\._]-$",
    "sigh_drop": r"-[\._]-'$",

    "happy": r"\^[_\.-]?\^$",

    "thumbs_up": r"\([Yy]\)$",
    "thumbs_down": r"\([Nn]\)$",
    "heart": r"<3$",

    "lol": r"(?i)\(lol\)$",
    "rofl": r"(?i)\(rofl\)$",

    "cheese": r"(?i)\(cheese\)$",
    "facepalm": r"(?i)\(facepalm\)$",
    "headbang": r"(?i)\(headbang\)$",
    "handshake": r"(?i)\(handshake\)$",
    "soclose": r"(?i)(\(soclose\)$)|(\(sc\)$)",
    "trollface": r"(?i)(\(trollface\)$)|(\(troll\)$)",
    "charliechat": r"(?i)(\(charliechat\)$)|(\(cc\)$)",
    "mystic": r"(?i)\(mystic\)$",
    "pizza": r"(?i)\(pizza\)$",
    "cake": r"(?i)\(cake\)$",
    "headset": r"(?i)\(headset\)$|\(headphones?\)$|\(earplugs?\)$"
}
