from datetime import datetime


def now():
    '''Get timestamp of now'''
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")