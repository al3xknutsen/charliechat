from os import listdir, mkdir, remove, rmdir, walk
from os.path import isdir, isfile, getsize


def FILE_READ(filename, binary=False):
    '''Reading file'''
    if isfile(filename) and getsize(filename) > 0:
        with open(filename, "r" + ("b" if binary else "")) as f:
            return f.read()
    else:
        return False

def FILE_LOAD(filename, initvalue):
    '''Loading file, or using default value'''
    content = FILE_READ(filename)

    if content:
        try:
            return eval(content)
            init = False
        except TypeError:  # If contains null bytes
            init = True
    else:
        init = True

    if init:
        FILE_WRITE(filename, initvalue)
        return initvalue

def FILE_WRITE(filename, value, mode="w"):
    '''Writing or appending to a file (also creating it if it doesn\'t exist)'''
    with open(filename, mode) as f:
        f.write(str(value))

def FILE_DELETE(filename):
    '''Deleting file'''
    if isfile(filename):
        remove(filename)

def DIR_CREATE(dirname):
    '''Create directory'''
    if not isdir(dirname):
        mkdir(dirname)

def DIR_DELETE(dirname):
    '''Delete directory'''
    if isdir(dirname):
        if listdir(dirname) > 0:
            alldirs = []

            for path, folders, files in walk(dirname):
                for f in files:
                    remove(path + "\\" + f)
                for d in folders:
                    alldirs.append(path + "\\" + d)

            for d in reversed(alldirs):
                rmdir(d)
        rmdir(dirname)