from os import mkdir, remove
from os.path import isfile, getsize, isdir
from threading import Thread

class FileHandler:
	'''Class for loading from file, or creating one if it doesn\'t exist'''
	
	def FILE_READ(self, filename, binary=False):
		'''Reading file'''
		if isfile(filename) and getsize(filename) > 0:
			with open(filename, "r"+("b" if binary else "")) as f:
				return f.read()
		else:
			return False
	
	def FILE_LOAD(self, filename, initvalue):
		'''Loading file, or using default value'''
		content = self.FILE_READ(filename)
		
		if content:
			return eval(content)
		else:
			self.FILE_WRITE(filename, initvalue)
			return initvalue
	
	def FILE_WRITE(self, filename, value, mode="w"):
		'''Writing or appending to a file (also creating it if it doesn\'t exist'''
		with open(filename, mode) as f:
			f.write(str(value))
	
	def FILE_DELETE(self, filename):
		'''Deleting file'''
		if isfile(filename):
			remove(filename)
	
	def DIR_CREATE(self, dirname):
		'''Create directory'''
		if not isdir(dirname):
			mkdir(dirname)

class MultiThread(Thread):
	'''Class for handling threading'''
	def __init__(self, func):
		self.func = func
		Thread.__init__(self)
	
	def run(self):
		self.func()