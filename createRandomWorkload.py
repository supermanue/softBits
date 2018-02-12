'''
Created on 31 aug. 2017

@author: supermanue

License: GPL
'''

'''
FUNCTIONALITY
----
This script creates a Slurm workload for a particular cluster.

This workload (trace) is exported into a tmp file for human read and to a pickle
 one, to it can be replayed if desired.

It can be executed in two ways:
- if several input arguments are used, the load is created and executed
- if only an input argument is used, it is considered to be a pickle file
from a past execution. It is loaded and replayed

INPUT PARAMETERS:
$1: base dir
$2: fraction of cluster employed
$3: desired experiment length in seconds

OR
$1: base dir
$2: name of the trace file to replay
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


    #creates a Slurm template and submits the job
    def submit(self, tmpDir):
        template = self.createJobTemplate(tmpDir)
        os.system("sbatch --output=" + tmpDir+ "/slurm-%j.out " + template)
        print ("job shuld be submitted now")

    def createJobTemplate(self, tmpDir):

        fileName = mkstemp(dir = tmpDir)[1]
        print (fileName)
        templateFile = open(fileName, 'w')

        templateFile.write("#!/bin/bash" + "\n")
        templateFile.write("#SBATCH --ntasks=" + str(self.jobSize)+ "\n")
        templateFile.write("sleep " + str(self.jobLength)+ "\n")
        templateFile.close()
        return fileName



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
            elif nodeState =="mix":
		        nodeStatus[nodeName] = 1
            else:
                nodeStatus[nodeName] = 2
    return nodeStatus

def readCPUStatus():
    a = Popen('sinfo -o %C -h', shell=True, stdout=PIPE)
    line = a.stdout.read()

    splittedVals=re.split("/", line)
    allocatedCPUs=splittedVals[0].strip()
    freeCPUs=splittedVals[1].strip()
    return (allocatedCPUs, freeCPUs)


def updateNodeStatus(fileName,  timestamp, nodeStatus, cpuStatus):
    newStatus=str(timestamp) + ","
    first=True
    for nodeName in sorted(nodeStatus.keys()):
        if first:
            first = False
        else:
            newStatus+=","

        newStatus += str(nodeStatus[nodeName])
    newStatus+=","+cpuStatus[0] +","+cpuStatus[1]
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
    newStatus +=",UsedCPUs,FreeCPUs"
    newStatus +="\n"
    templateFile = open(fileName, 'a')
    templateFile.write(newStatus)
    templateFile.close()

if __name__ == '__main__':
    jobList = []
    rootDir = sys.argv[1]
    experimentLength=0
    monitorTime=5

    if (len(sys.argv) ==3):
        pickleFileName = sys.argv[2]
        pickleFile = open (pickleFileName, 'r')
        jobList = pickle.load(pickleFile)
        pickleFile.close()
        print ("job trace imported from " + pickleFileName)

        #calculate experiment end
        #number 10 is just in case, to have a small margin
        experimentLength = 10 + reduce((lambda x, y: max(x,y)), map(lambda x: x.startOffset, jobList))
        experimentFolder=rootDir

        outputFileName = rootDir+"cluster_status.txt"
        print ("cluster status log saved in " + outputFileName)

    elif (len(sys.argv) == 4):
        fractionOfClusterEmployed = float(sys.argv[2])
        experimentLength = int(sys.argv[3])

        ########SOME CONSTANTS
        clusterSize = 128
        minJobSize = 1
        maxJobSize = clusterSize / 8
        minJobLength = 1000 #seconds
        maxJobLength = max (minJobLength * 50 ,experimentLength * 0.05)  # entre 50 veces el minimo y el 5% del tiempo total

        totalResourceAvailability = clusterSize * experimentLength * fractionOfClusterEmployed

        jobList = []
        jobCounter = 0
        while (totalResourceAvailability > 0):
            ##gausian distribution of jobs: most of them are small. This is truncated to 1 so it is not perfect, but it's good enough
            ##1.1 is to allow some values over 1, so jobSize can be maxJobSize sometimes.
            gaussian =2
            while gaussian >1.1:
                gaussian = (abs(normal()) / 3.0)  #normal returns values between 0 and 3. Aslo we want mostly small ones
            jobSize = int(max (1,  gaussian * float(maxJobSize)))

            gaussian =2
            while gaussian >1:
                gaussian = (abs(normal()) / 3.0)  #normal returns values between 0 and 3. Aslo we want mostly small ones

            jobLength = int(minJobLength + uniform (0, maxJobLength-minJobLength) * gaussian)

            startOffset = randint (0, experimentLength - jobLength)

            #check if the job is too big for the remaining resource availability, and trim it if so
            if jobSize * jobLength > totalResourceAvailability:
                jobSize = int(totalResourceAvailability / jobLength)
                totalResourceAvailability = 0  #to avoid problems with integer round and make sure that this is the last job


            newJob = Job(jobCounter, jobSize, jobLength, startOffset)
            jobList.append(newJob)
            jobCounter +=1
            totalResourceAvailability -= (jobSize * jobLength)
            print ("Created job: " + str(newJob))
            print ("remaining tresources = " + str(totalResourceAvailability))

        jobList.sort(key=lambda job: 0 - job.startOffset)


        #we want first job to start at time 0 and last job to end at time "experimentLength".
        jobList[len(jobList)-1].startOffset = 10 #not exactly at 0, in case of overheads...
        jobList[0].startTime  = experimentLength - jobList[len(jobList)-1].jobLength


        ####
        #FILE MANAGEMENT
        experimentFolder=rootDir+"/load"+str(fractionOfClusterEmployed)+"_lenght"+str(experimentLength)+"/"
        os.makedirs(experimentFolder)

        exportJobListName = experimentFolder+"jobList_human.txt"
        pickleFileName = experimentFolder+"jobList_pickle.txt"
        outputFileName = experimentFolder+"cluster_status.txt"

        print ("job list (for humans) saved in  " + exportJobListName)
        print ("job list (for computers) saved in " + pickleFileName)
        print ("cluster status log saved in " + outputFileName)

        exportJobList = open (exportJobListName, 'w')
        for job in jobList:
            exportJobList.write(str(job) +"\n")
        exportJobList.close()

        pickleFile = open (pickleFileName, 'w')
        pickle.dump(jobList, pickleFile)
        pickleFile.close()


    print ("SORTED LIST OF JOBS")
    for job in jobList:
        print (job)

    nodeStatus = readNodeStatus()
    writeFileHeaders(outputFileName, nodeStatus)

    elapsedTime = 0
    auxJob = jobList.pop()
    while elapsedTime < experimentLength:
        print (elapsedTime)
        if auxJob.startOffset <= elapsedTime:
            auxJob.submit(experimentFolder)
            try:
                auxJob = jobList.pop()
            except:
                break
        sleep(1)
        elapsedTime +=1

        if (elapsedTime %monitorTime ==0):
            now = int(time())
            nodeStatus = readNodeStatus()
            cpuStatus = readCPUStatus()
            updateNodeStatus(outputFileName, now, nodeStatus, cpuStatus)
