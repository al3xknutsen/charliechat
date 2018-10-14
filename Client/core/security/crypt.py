from Crypto.PublicKey import RSA

from core.thread import MultiThread


key = None

def _init_keygen():
    global key
    key = RSA.generate(2048)

def key_generate():
    '''Function for generating encryption key'''
    keygen = MultiThread(_init_keygen)
    keygen.start()
    return keygen

def key_return():
    global key
    return key