from datetime import datetime
from ftplib import Error as ftperror, FTP
from os import getcwd, getenv, listdir, mkdir, remove, rmdir, walk
from os.path import isdir, isfile
from socket import error as socketerror


currentdir = getcwd()

def connect():
	global ftp
	ftp = FTP("mystic.ddns.net", "CC-Client", "CHS1yFl4N1X92hJj")

if currentdir != "CharlieChat Dev":
	alldirs = [""]

	# Remove all existing content
	for x in listdir(currentdir):
		if isfile(x) and x.split(".")[0] == "CharlieChat" and x.split(".")[-1] in ["py", "pyw"]:
			remove(x)
		elif isdir(x) and x in ["core", "images", "lib", "ui", "util", "windows"]:
			deldirs = []
			for path, folders, files in walk(x):
				for f in files:
					remove(path + "\\" + f)
				for d in folders:
					deldirs.append(path + "\\" + d)
			for d in reversed(deldirs):
				rmdir(d)
			rmdir(x)

	connect()

	for folder in alldirs:
		content = []
		succeed = False

		while not succeed:
			try:
				ftp.retrbinary("MLSD " + folder, content.append)  # DOWNLOAD OVERVIEW
				succeed = True
			except (ftperror, socketerror):
				continue

		items = "".join(content).split("\r\n")[:-1]  # Join content if split in several blocks

		for x in items:
			# Parse data
			itemdata = x.split(";")
			name = itemdata[-1].lstrip(" ").strip("\r\n")
			itemtype = itemdata[0].split("=")[1]

			partpath = folder + "\\" + name
			fullpath = currentdir + partpath

			# Create new folders and files
			if itemtype == "dir":
				mkdir(fullpath)
				alldirs.append(partpath)
			elif itemtype == "file":
				with open(fullpath, "wb") as f:
					try:
						print partpath.lstrip("\\")
						ftp.retrbinary("RETR " + partpath, f.write)
					except (ftperror, EOFError):
						items.append(x)
					except socketerror:
						connect()

	with open(getenv("APPDATA") + "\\last_update.txt", "w") as file_update:
		file_update.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
