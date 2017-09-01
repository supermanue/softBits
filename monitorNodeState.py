'''
Created on 31 aug. 2017

@author: supermanue

License: GPL
'''

import sys, os
from subprocess import Popen, PIPE
import re
from time import time, sleep
import signal
import sys
from tempfile import mkstemp

def readNodeStatus():
    nodeStatus={}

    a = Popen('sinfo -Nh', shell=True, stdout=PIPE)
    b = a.stdout.read()
    for line in b.split("\n"):
        splittedLine = re.split(' *', line) #elements are separated by a variable number of spaces
        if len(splittedLine) ==1 :
            break
        nodeName = splittedLine[0]
        nodeState = splittedLine[3]

        if nodeName not in nodeStatus.keys(): #in case the same node is in several queueues, take only one
            if nodeState =="idle":
                nodeStatus[nodeName] = 0
            else:
                nodeStatus[nodeName] = 1
    return nodeStatus

def updateNodeStatus(fileName,  timestamp, nodeStatus):
    newStatus=str(timestamp) + ","
    first=True
    for nodeName in sorted(nodeStatus.keys()):
        if first:
            first = False
        else:
            newStatus+=","

        newStatus += str(nodeStatus[nodeName])

    newStatus +="\n"
    templateFile = open(fileName, 'a')
    templateFile.write(newStatus)
    templateFile.close()

def writeFileHeaders(fileName, nodeStatus):
    newStatus="Timestamp,"
    first=True
    for nodeName in sorted(nodeStatus.keys()):
        if first:
            first = False
        else:
            newStatus+=","

        newStatus += str(nodeName)

    newStatus +="\n"
    templateFile = open(fileName, 'a')
    templateFile.write(newStatus)
    templateFile.close()


def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        print ("Output file stored in " + outputFileName) #esto es una cutrez pero mala suerte
        sys.exit(0)


if __name__ == '__main__':


    outputFileName = mkstemp()[1]
    print ("Saving cluster status every 5 seconds. Result will be saved in " + outputFileName)
    print ("Press CTRL+C to stop")
    signal.signal(signal.SIGINT, signal_handler)

    nodeStatus = readNodeStatus()
    writeFileHeaders(outputFileName, nodeStatus)

    while (True):
        now = int(time())
        nodeStatus = readNodeStatus()
        updateNodeStatus(outputFileName, now, nodeStatus)
        sys.stdout.write('.')
        sys.stdout.flush()
        sleep(5)
