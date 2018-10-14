from threading import Thread


class MultiThread(Thread):
    '''Class for handling threading'''
    def __init__(self, func, *args):
        self.func = func
        self.args = args
        Thread.__init__(self)

    def run(self):
        if len(self.args) == 0:
            self.func()
        else:
            self.func(*self.args)