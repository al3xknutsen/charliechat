from copy import deepcopy
from datetime import datetime
from math import ceil
from os import getpid, kill
from os.path import getmtime, getsize, isfile
from shutil import copyfile
from signal import SIGTERM
from ssl import PROTOCOL_TLSv1, wrap_socket
from socket import error as socketerror, SHUT_RDWR, gethostname, socket
from sqlite3 import connect as sqlconnect
import sys
from time import sleep

from serverclasses import FileHandler, MultiThread

FileHandler = FileHandler()

sys.stderr = open("error.log", "a") # Opening error log

recvsize = 1024
codec = "utf-8"
logout_codes = [10053, 10054] # Error codes returned when client disconnects
users = {}

# Creating socket
server = socket()
server = wrap_socket(server, certfile="cert.pem", server_side=True, ssl_version=PROTOCOL_TLSv1)
server.bind((gethostname(), 25000))
server.listen(20)

def dbconnect():
    '''Connect to database'''
    dbfile = sqlconnect("logindata.db")
    database = dbfile.cursor()
    return [dbfile, database]

def dbclose(dbfile):
    '''Closing database'''
    dbfile.commit()
    dbfile.close()

def socketclose(socket):
    '''Closing socket'''
    socket.shutdown(SHUT_RDWR)
    socket.close()

# Create database for user data
dbfile, database = dbconnect()
if getsize("logindata.db") == 0:
    database.execute("CREATE TABLE users (username text unique, password text)")
    dbfile.commit()
dbfile.close()

def now():
    '''Return timestamp of now'''
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# Creating dirs
FileHandler.DIR_CREATE("settings")
FileHandler.DIR_CREATE("avatars")
FileHandler.DIR_CREATE("contacts")

# Loading files
afks = FileHandler.FILE_LOAD("afks.txt", [])
rooms = FileHandler.FILE_LOAD("rooms.txt", {"private": {}, "public": {}})
roomaccess = FileHandler.FILE_LOAD("roomaccess.txt", {})
lastmsg = FileHandler.FILE_LOAD("lastmsg.txt", "'"+now().split(" ")[0]+"'")

print "Server started."

def manage_userdata(infotype, datafile, client):
    recvdata = recvmsg(client)
    if recvdata == "FETCH-" + infotype.upper():
        if isfile(datafile):
            sendmsg(FileHandler.FILE_READ(datafile), client)
        else:
            sendmsg("NO-" + infotype.upper(), client)
            MSG = recvmsg(client)
            FileHandler.FILE_WRITE(datafile, MSG)
    else:
        if not isfile(datafile):
            MSG = recvmsg(client)
            FileHandler.FILE_WRITE(datafile, MSG)

def write_log(time, msg, room=None):
    '''Writing to log file'''
    global lastmsg
    
    datestamp, timestamp = time.split(" ") # Split into date and time
    
    if lastmsg != datestamp:
        # Print new date
        header = "--- "+datestamp+" ---"
        FileHandler.FILE_WRITE("log.log", header+"\n", "a")
        print header
            
        # Save date of last message
        lastmsg = datestamp
        FileHandler.FILE_WRITE("lastmsg.txt", "'"+lastmsg+"'")
    
    # Print message
    message = ("["+timestamp+("|"+room if room else "")+"] "+msg).encode(codec)
    FileHandler.FILE_WRITE("log.log", message+"\n", "a")
    print message

def register(dbfile, db, user, password, client, force=False):
    '''Registering new user'''
    db.execute("SELECT * FROM users WHERE username = ?", [user])
    
    if db.fetchone() == None:
        # Register
        db.execute("INSERT INTO users VALUES (?, ?)", [user, password])
        if not force:
            dbclose(dbfile)
            write_log(now(), user+" registered.")
            sendmsg(client, "PROCEED")
        return True
    else:
        # User already exists
        if not force:
            sendmsg(client, "USER-ALREADY-EXISTS")
            client.close()
        return False

def broadcast(recipients, msg, client=None):
    '''Function for broadcasting messages to clients'''
    msg = str(msg)
    
    # Don't send to current user
    if client != None and client in recipients:
        recipients.remove(client)
    
    for r in recipients:
        sendmsg(msg, r)

def disconnect(user, clientsocket):
    '''Disconnecting a user'''
    global users, afks, roomaccess
    write_log(now(), user+" disconnected.")
    
    socketclose(clientsocket)
    
    # Remove user from lists
    if user in users:
        del users[user]
    if user in afks:
        afks.remove(user)
    
    FileHandler.FILE_WRITE("afks.txt", afks)
    
    # Remove user from access file
    update_access = False
    for room in roomaccess:
        if user in roomaccess[room]:
            roomaccess[room].remove(user)
            update_access = True
        if len(roomaccess[room]) == 0:
            del roomaccess[room]
            update_access = True
            break
    
    if update_access:
        FileHandler.FILE_WRITE("roomaccess.txt", roomaccess)
    
    # Broadcast disconnect
    for c in users.values():
        sendmsg({"datatype": "disconnect", "time": now(), "user": user}, c)

def close():
    '''Function for cleaning up and terminating server'''
    for c in users.values():
        socketclose(c)
    sys.stderr.close()
    copyfile("error.log", "error-copy.log")
    kill(getpid(), SIGTERM)


def sendmsg(msg, client):
    '''Sending message with msg length'''
    msg = "|"+str(msg)
    msglength = str(len(msg))
    msgpluslength = len(msglength+msg)
    finallength = msgpluslength+len(str(msgpluslength))-len(msglength)
    client.send(str(finallength)+msg)

def recvmsg(client):
    '''Receiving message with msg length'''
    rawmsg = client.recv(recvsize)
    length, data = rawmsg.split("|", 1)
    for x in range(int(ceil(float(length)/recvsize))-1):  # @UnusedVariable
        data += client.recv(recvsize)
    return data



# #### CONNECTION #### #
def connection():
    '''Creating a connection (one per client)'''
    global users, roomaccess
    
    # Accept client
    try:
        client = server.accept()[0]
    except socketerror:
        sys.stderr.write("["+now()+"] Forcibly closed\n")
        return
    
    # Sending current version
    print FileHandler.FILE_READ("last_update.txt")
    sendmsg(FileHandler.FILE_READ("last_update.txt"), client)
    if recvmsg(client) == True:
        socketclose(client)
        return
    
    # Init msg
    try:
        initmsg = recvmsg(client)
    except socketerror:
        sys.stderr.write("["+now()+"] Forcibly closed\n")
        return
    
    # Get login data, or cancel if client is a web browser
    try:
        logindata = eval(initmsg)
    except KeyError:
        print "Web browser detected."
        if initmsg.startswith("GET / HTTP/"):
            client.send("Sorry, web browsers are not supported yet!")
        socketclose(client)
        return
    
    # Vars
    actiontype = logindata["actiontype"]
    user = logindata["user"]
    file_avatar = "avatars\\" + user + ".png"
    file_contacts = "contacts\\" + user + ".txt"
    file_settings = "settings\\" + user + ".txt"
    
    # Connect to database
    dbfile, database = dbconnect()

    
    # ## REGISTER ## #
    if actiontype == "register":
        register(dbfile, database, user, logindata["password"], client)
        socketclose(client)
        return
    
    
    
    # ## LOGIN ## #
    elif actiontype == "login":
        if "forcereg" in logindata: # Register
            register(dbfile, database, user, logindata["password"], client, True)
        
        # Select user
        database.execute("SELECT * FROM users WHERE username = ?", [user])
        userdata = database.fetchone()
        dbfile.close()
        
        # Wrong username
        if userdata == None:
            sendmsg("WRONG-USERNAME", client)
            return
        # Wrong username
        if logindata["password"] != userdata[1]:
            sendmsg("WRONG-PASSWORD", client)
            return
        # User already logged in
        if user in users:
            sendmsg("USER-ALREADY-LOGGED-IN", client)
            return
        sendmsg("PROCEED", client)
    
    
    
    # ## CHANGE PASSWORD ## #
    elif actiontype == "changepass":
        print "Changing password"
        dbfile, database = dbconnect()
        database.execute("SELECT * FROM users WHERE username = ?", [user])
        userdata = database.fetchone()
        
        # Wrong password
        if userdata[1] != logindata["old_pass"]:
            dbfile.close()
            sendmsg("WRONG-PASSWORD", client)
            return
        
        # Update password
        database.execute("UPDATE users SET password = ? WHERE username = ?", [logindata["new_pass"], user])
        dbclose(dbfile)
        
        write_log(now(), user+" changed their password.")
        sendmsg("PROCEED", client)
    
    
    
    # ## LOGIN INFO - ROOMS AND SETTINGS ## #
    if actiontype not in ["reconnect", "register"]:
        write_log(now(), user+" connected.")
        
        userinfo = {}
        
        # Collecting information about every logged in user (avatar change date + text color)
        for u in users:
            useravatar = "avatars\\" + u + ".png"
            usersettings = "settings\\" + u + ".txt"
            userinfo.update({u: {"mtime-avatar": getmtime(useravatar) if isfile(useravatar) else None, \
                                 "color": eval(FileHandler.FILE_READ(usersettings))["color"] \
                                 if isfile(usersettings) else [0, 0, 0]}})
        
        # Send startup info to client
        sendmsg({"users": userinfo, "afks": afks, "mtime-rooms": getmtime("rooms.txt"), \
                 "mtime-avatar": getmtime(file_avatar) if isfile(file_avatar) else None, \
                 "mtime-contacts": getmtime(file_contacts) if isfile(file_contacts) else None, \
                 "mtime-settings": getmtime(file_settings) if isfile(file_settings) else None}, client)
        
        # Send list of rooms if client needs it
        if recvmsg(client) == "SEND-ROOMS":
            rooms_copy = deepcopy(rooms) # Needs deepcopy to avoid editing main var
            
            # Remove owner field if not necessary
            for roomtype in rooms:
                for room in rooms[roomtype]:
                    if rooms[roomtype][room]["owner"] == user:
                        rooms_copy[roomtype][room]["owner"] = True
                    else:
                        del rooms_copy[roomtype][room]["owner"]
            
            # Modify data to be sent
            for room in rooms["private"]:
                roomdata = rooms_copy["private"][room]
                
                # Modify if whitelist
                if "whitelist" in roomdata:
                    if user not in roomdata["whitelist"]:
                        del rooms_copy["private"][room]
                        continue
                    del roomdata["whitelist"]
                
                # Modify if password
                elif "password" in roomdata:
                    roomdata["password"] = True
            
            sendmsg(rooms_copy, client) # Send room data to cilent
        
        # Managing user data
        manage_userdata("settings", file_settings, client)
        manage_userdata("contacts", file_contacts, client)
    
    
    # ## COLOR ## #
    if logindata["actiontype"] != "register":
        color = eval(FileHandler.FILE_READ(file_settings))["color"]
    
    # ## BROADCAST LOGIN ## #
    if logindata["actiontype"] not in ["reconnect", "register"]:
        # Broadcast that user has connected
        broadcast(users.values(), {"datatype": "connect", "time": now(), "user": user, "color": color, \
                                   "mtime-avatar": getmtime(file_avatar) if isfile(file_avatar) else None})
    
    users[user] = client
    
    
    
    # ## START RECV MSG LOOP ## #
    while True:
        try:
            DATA = eval(recvmsg(client))
            datatype = DATA["datatype"]
            
            
            # /die command #
            if datatype == "command" and DATA["msg"] == "/die":
                close()
            else:
                DATA_SEND = deepcopy(DATA)
                DATA_SEND.update({"time": now(), "user": user})
            
            
            # ## AVATAR SEND ## #
            if datatype == "avatar-send":
                if "value" in DATA:
                    FileHandler.FILE_WRITE(file_avatar, DATA["value"], "wb")
                else:
                    sendmsg({"datatype": datatype, "value": not isfile(file_avatar)}, client)
            
            
            # ## AVATAR FETCH ## #
            elif datatype == "avatar-fetch":
                filepath = "avatars\\"+DATA["user"]+".png"
                DATA["value"] = FileHandler.FILE_READ(filepath, True) if isfile(filepath) else False
                sendmsg(DATA, client)
            
            
            # ## AVATAR ## #
            elif datatype == "avatar-change":
                if DATA["value"] == "delete":
                    write_log(now(), user+" deleted their avatar.")
                    FileHandler.FILE_DELETE(file_avatar)
                else:
                    write_log(now(), user+" changed their avatar.")
                    FileHandler.FILE_WRITE(file_avatar, DATA["value"], "wb")
                DATA["user"] = user
                broadcast(users.values(), DATA, client)
            
            
            # ## ADD CONTACT ## #
            elif datatype == "contact-add":
                contact = DATA["contact"]
                
                dbfile, database = dbconnect()
                database.execute("SELECT * FROM users WHERE username = ?", [contact])
                dbdata = database.fetchone()
                dbclose(dbfile)
                
                if dbdata != None:
                    write_log(now(), user + " added a contact: " + contact)
                    with open("contacts\\" + user + ".txt", "a") as contactfile:
                        contactfile.write(contact + "\n")                
                sendmsg({"datatype": "contact-exists", "contact": contact, "value": bool(dbdata)}, client)
            
            
            # ## CHANGE TEXT COLOR ## #
            if datatype == "color":
                settings = eval(FileHandler.FILE_READ(file_settings))
                settings["color"] = color = DATA["value"]
                FileHandler.FILE_WRITE(file_settings, settings)
                
                DATA["user"] = user
                broadcast(users.values(), DATA, client)
            
            
            # ## CHAT ## #
            elif datatype in ["chat", "command"]:
                write_log(now(), user+": "+DATA["msg"], DATA.get("room"))
                
                private = rooms["private"]
                room = DATA.get("room")
                users_send = users.values()
                
                if room != None and room in private and "password" in private[room]:
                    users_send = [users[u] for u in users if u in roomaccess["room"]]
                broadcast(users_send, DATA_SEND, client)
            
            
            # ## AFK ## #
            elif datatype == "afk":
                # User if AFK
                if DATA["status"]:
                    status = "AFK"
                    if user not in afks:
                        afks.append(user)
                
                # User is back
                else:
                    status = "back"
                    if user in afks:
                        afks.remove(user)
                
                write_log(now(), user+" is "+status+".")
                FileHandler.FILE_WRITE("afks.txt", afks)
                broadcast(users.values(), DATA_SEND, client)
            
            
            # ## ADD ROOM ## #
            elif datatype == "add_room":
                roomtype = DATA["type"]
                roomname = DATA["name"]
                room_unique = {"datatype": "room_unique"}
                
                if roomname in rooms["public"].keys()+rooms["private"].keys():
                    room_unique["value"] = False # Don't add room if one with same name already exists
                    sendmsg(room_unique, client)
                else:
                    write_log(now(), user+" added "+roomtype+" room: "+roomname)
                    
                    # Add data
                    roomdata = {"owner": user}
                    if "password" in DATA: # Password
                        roomdata.update({"password": DATA["password"]})
                    elif "whitelist" in DATA: # Whitelist
                        roomdata.update({"whitelist": DATA["whitelist"]})
                    rooms[roomtype][roomname] = roomdata
                    
                    FileHandler.FILE_WRITE("rooms.txt", rooms)
                    
                    room_unique["value"] = True # Clients can add room
                    sendmsg(room_unique, client)
                    
                    # Manipulate data to be sent
                    if DATA["type"] == "private":
                        if "password" in DATA:
                            DATA_SEND["password"] = True
                        if "whitelist" in DATA:
                            del DATA_SEND["whitelist"]
                            # Broadcast message (whitelist aware)
                            broadcast([users[c] for c in users if c in DATA["whitelist"]], DATA_SEND, client)
                    
                    # Broadcast message (without whitelist)
                    if DATA["type"] == "public" or (DATA["type"] == "private" and "whitelist" not in DATA):
                        broadcast(users.values(), DATA_SEND, client)
            
            
            # ## ROOM PASSWORD ## #
            elif datatype == "roompass":
                room = DATA["room"]
                access = DATA["password"] == rooms["private"][room]["password"]
                update_access = True
                
                sendmsg({"datatype": "roompass", "proceed": access}, client) # Send result: Access granted/denied
                
                # If access granted: Update access permission
                if access:
                        if room in roomaccess:
                            if user not in roomaccess[room]:
                                roomaccess[room].append(user)
                        else:
                            roomaccess[room] = [user]
                
                # If access denied: Remove user from access permissions
                else:
                    if room in roomaccess:
                        if user in roomaccess[room]:
                            roomaccess[room].remove(user)
                        else:
                            update_access = False
                        if len(roomaccess[room]) == 0:
                            del roomaccess[room]
                    else:
                        update_access = False
                    
                # Update access file
                if update_access:
                    FileHandler.FILE_WRITE("roomaccess.txt", roomaccess)
            
            
            # ## NO ACCESS ## #
            elif datatype == "noaccess":
                if user in roomaccess:
                    roomaccess.remove(user)
                    FileHandler.FILE_WRITE("roomaccess.txt", roomaccess)
            
            
            # ## DELETE ROOM ## #
            elif datatype == "del_room":
                write_log(now(), user+" deleted "+DATA["type"]+" room: "+DATA["name"])
                
                # Get recipients (whitelist aware)
                roomname = DATA["name"]
                roomtype = DATA["type"]
                users_send = users.values()
                
                if roomtype == "private" and "whitelist" in rooms["private"][roomname]:
                    users_send = [users[c] for c in rooms["private"][roomname]["whitelist"] if c in users]
                broadcast(users_send, DATA_SEND, client)
                
                # Remove entry from room data, and update file
                del rooms[roomtype][roomname]
                FileHandler.FILE_WRITE("rooms.txt", rooms)
            
            
            # ## WEBCAM ## #
            elif datatype in ["voice", "webcam"]:
                broadcast(users.values(), DATA, client)
            
            
            # ## DISCONNECT ## #
            elif datatype == "disconnect":
                if "settings" in DATA:
                    FileHandler.FILE_WRITE(file_settings, DATA["settings"])
                disconnect(user, client)
                return
            
            # ## DELETE USER ## #
            elif datatype == "del_user":
                disconnect(user, client)
                write_log(now(), user+" deleted their account.")
                
                dbfile, database = dbconnect()
                database.execute("DELETE FROM users WHERE username = ?", [user])
                dbclose(dbfile)
                
                rooms_copy = deepcopy(rooms)
                for roomtype in rooms_copy:
                    for room in rooms_copy[roomtype]:
                        if rooms_copy[roomtype][room]["owner"] == user:
                            del rooms[roomtype][room]
                            broadcast(users, {"datatype": "del_room", "type": roomtype, "name": room})
                FileHandler.FILE_WRITE("rooms.txt", rooms)
                
                FileHandler.FILE_DELETE(file_settings)
                FileHandler.FILE_DELETE(file_avatar)
                return
        
        
        # ## ERROR HANDLING ## #
        except socketerror, errormsg:
            # Forced disconnect
            if " ".join(str(errormsg).split(" ")[0:2]) in ["[Errno "+str(e)+"]" for e in logout_codes]:
                disconnect(user, client)
                return
            else:
                # Write to error log
                sys.stderr.write("["+now()+"] "+str(errormsg)+"\n")
                close()

def reset():
    '''Countdown for restarting server'''
    sleep(270)
    close()

# Start connections
for x in range(20):
    MultiThread(connection).start()

# Start restart countdown
MultiThread(reset).start()