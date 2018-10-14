from core.security.hash import HASH


def LOGIN(username, password, forcereg=False):
    '''Message: Login'''
    data = {"actiontype": "login", "user": username, "password": HASH(password)}
    if forcereg:
        data.update({"forcereg": True})
    return str(data)

def REGISTER(username, password):
    '''Message: Register'''
    return str({"actiontype": "register", "user": username, "password": HASH(password)})

def RECONNECT(username):
    '''Message: Reconnect'''
    return str({"actiontype": "reconnect", "user": username})

def DISCONNECT():
    '''Message: Disconnect'''
    return str({"datatype": "disconnect"})