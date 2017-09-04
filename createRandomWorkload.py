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
$1: fraction of cluster employed
$2: cluster size
$3: min job size
$4: max job size
$5: min job length, in seconds
$6: max job length, in seconds
$7: desired experiment length in seconds

OR
$1: name of the trace file to replay
'''

import sys
from random import randint
from time import sleep
import tempfile
import shutil
import os
from numpy.random import normal
import pickle

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
        os.system("sbatch " + template)
        print ("job shuld be submitted now")

    def createJobTemplate(self, tmpDir):

        fileName = tempfile.mkstemp(dir = tmpDir)[1]
        print (fileName)
        templateFile = open(fileName, 'w')

        templateFile.write("#!/bin/bash" + "\n")
        templateFile.write("#SBATCH --ntasks=" + str(self.jobSize)+ "\n")
        templateFile.write("sleep " + str(self.jobLength)+ "\n")
        templateFile.close()
        return fileName



if __name__ == '__main__':


    jobList = []
    experimentLength = 0

    if (len(sys.argv) ==2):
        pickleFileName = sys.argv[1]
        pickleFile = open (pickleFileName, 'r')
        jobList = pickle.load(pickleFile)
        pickleFile.close()
        print ("job trace imported from " + pickleFileName)

        #calculate experiment end
        #number 10 is just in case, to have a small margin
        experimentLength = 10 + reduce((lambda x, y: max(x,y)), map(lambda x: x.startOffset, jobList))
        print experimentLength



    elif (len(sys.argv) == 8):

        fractionOfClusterEmployed = float(sys.argv[1])
        clusterSize = int(sys.argv[2])
        minJobSize = int(sys.argv[3])
        maxJobSize = int(sys.argv[4])
        minJobLength = int(sys.argv[5])
        maxJobLength = int(sys.argv[6])
        experimentLength = int(sys.argv[7])


        totalResourceAvailability = clusterSize * experimentLength * fractionOfClusterEmployed

        jobList = []
        jobCounter = 0
        while (totalResourceAvailability > 0):
            ##gausian distribution of jobs: most of them are small. This is truncated to 1 so it is not perfect, but it's good enough
            ##1.1 is to allow some values over 1, so jobLength can be maxJobLength sometimes.
            gaussian =2
            while gaussian >1.1:
                gaussian = abs(normal())
            print gaussian
            jobSize = int(max (1,  gaussian * float(maxJobSize)))
            jobLength = randint (minJobLength, maxJobLength)
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
        exportJobListName = tempfile.mkstemp()[1]

        exportJobList = open (exportJobListName, 'w')

        for job in jobList:
            exportJobList.write(str(job) +"\n")
        exportJobList.close()
        print ("job list exported to " + exportJobListName)

        pickleFileName = tempfile.mkstemp()[1]
        pickleFile = open (pickleFileName, 'w')
        pickle.dump(jobList, pickleFile)
        pickleFile.close()
        print ("job trace exported to " + pickleFileName)
        exit


    print ("SORTED LIST OF JOBS")
    for job in jobList:
        print (job)

    tmpDir = tempfile.mkdtemp()

    time = 0
    auxJob = jobList.pop()
    while time < experimentLength:
        print (time)
        if auxJob.startOffset <= time:
            auxJob.submit(tmpDir)
            try:
                auxJob = jobList.pop()
            except:
                break
        sleep(1)
        time +=1
    shutil.rmtree(tmpDir)
