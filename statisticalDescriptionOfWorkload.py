'''
Created on 10 Jan. 2018

@author: supermanue

License: GPL
'''

'''
FUNCTIONALITY
----
This script shows stats for a particular workload

$1: name of the trace file to replay
'''
import sys
from random import randint,uniform
from time import time, sleep
import tempfile
import shutil
import os
from numpy.random import normal
import pickle
from subprocess import Popen, PIPE
import re
import signal
from tempfile import mkstemp
from math import ceil



class Job:
    jobId = -1
    jobSize = 0
    jobLength = 0
    startOffset = 0

    def __init__(self, jobId, jobSize, jobLength, startOffset):
        self.jobId = jobId
        self.jobSize = jobSize
        self.jobLength = jobLength
        self.startOffset = startOffset

    def __str__(self):
        return ("Job %d: size=%d, length=%d, startOffset=%d") %(self.jobId, self.jobSize, self.jobLength, self.startOffset)


def createOrIncreaseCount(elem, dict):
    if elem in dict:
        dict[elem] = dict[elem]+1
    else:
        dict[elem] = 1


if __name__ == '__main__':
    jobList = []
    rootDir = sys.argv[1]
    experimentLength=0
    monitorTime=5


    pickleFileName = sys.argv[1]
    pickleFile = open (pickleFileName, 'r')
    jobList = pickle.load(pickleFile)
    pickleFile.close()
    print ("job trace imported from " + pickleFileName)

    jobSizes={}
    jobLengths=[]
    for job in jobList:
        #minutes = (int)(ceil(job.jobLength / 60.0))
        createOrIncreaseCount(job.jobSize, jobSizes)
        jobLengths.append(job.jobLength)

    print ("size, count")
    for elem in sorted(jobSizes.keys()):
        print (str(elem) + "," + str(jobSizes[elem]))
    print ("\n\n\n")
    print("length")
    for elem in sorted(jobLengths):
        print (str(elem))
