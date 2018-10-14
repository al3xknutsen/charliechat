from hashlib import sha512


def HASH(password):
    '''Function for creating SHA-512 hashes'''
    hashgen = sha512()
    hashgen.update(password)
    hashpass = hashgen.hexdigest()
    return hashpass