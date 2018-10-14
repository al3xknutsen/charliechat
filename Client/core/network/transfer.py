from math import ceil


recvsize = 1024

def SENDMSG(msg, client):
    '''Sending messages with msg length'''
    # Manipulating data
    msg = "|" + str(msg)
    msglength = str(len(msg))
    msgpluslength = len(msglength + msg)
    finallength = msgpluslength + len(str(msgpluslength)) - len(msglength)
    msgsend = str(finallength) + msg

    # Sending data
    client.send(msgsend)

def RECVMSG(client):
    # Receiving data
    rawmsg = client.recv(recvsize)
    
    # Finding times needed to repeat
    length, data = rawmsg.split("|", 1)
    repeat = int(ceil(float(length) / recvsize)) - 1

    # Repeating recv for entire message
    for x in range(repeat):  # @UnusedVariable
        data += client.recv(recvsize)

    return data
