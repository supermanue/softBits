'''
Created on 19 oct. 2016

@author: supermanue
'''
from sys import argv, exit
import os
from macpath import split
from math import sqrt
from sys import maxint as MAXINT
import time

#######
#Format of input file:   prefix.numTasks
#format of created scripts: prefix.numTasks_nodesxcoresPerNode


combinationsACME=[[1,1,1],
              [2,1,2],
              [2,2,1],
              [4,1,4],
              [4,2,2],
              [4,4,1],
              [8,1,8],
              [8,2,4],
              [8,4,2],
              [8,8,1],
              [16,1,16],
              [16,2,8],
              [16,4,4],
              [16,8,2],
              [32,2,16],
              [32,4,8],
              [32,8,4],
              [32,4,8],
              [64,4,16],
              [64,8,8],
              [128,8,16]]


#having these as global vars highly simplyfies code
firstJobInit = MAXINT
lastJobEnd = 0
clusterSize = 128


def prepareDataStructures(dataStruct, appName):
    for combination in combinationsACME:
        numTasks = combination[0]
        numNodes = combination[1]
        numTasksPerNode = combination[2]
    
        if not dataStruct.has_key(appName):
            dataStruct[appName]={}
    
        if not dataStruct[appName].has_key(numTasks):
            dataStruct[appName][numTasks]={}
            
        if not dataStruct[appName][numTasks].has_key(numNodes):
            dataStruct[appName][numTasks][numNodes]={}

        if not dataStruct[appName][numTasks][numNodes].has_key(numTasksPerNode):
            dataStruct[appName][numTasks][numNodes][numTasksPerNode]={'count':0, 'avg':0.0, 'dev':0, 'accumDev':0}
            

def updateStats (dataStruct, appName, numTasks, numNodes, numTasksPerNode, initDate, endDate):
    
    if not appName in dataStruct.keys():
        prepareDataStructures(dataStruct, appName)
    
    elem=dataStruct[appName][numTasks][numNodes][numTasksPerNode]
    oldValue = elem['count'] * elem['avg']
    newValue = oldValue + endDate - initDate
    elem['count'] +=1    
    elem['avg'] = newValue / elem['count']
    
    
def accumulateDev (dataStruct, appName, numTasks, numNodes, numTasksPerNode, initDate, endDate):
    if not appName in dataStruct.keys():
        prepareDataStructures(dataStruct, appName)
    elem=dataStruct[appName][numTasks][numNodes][numTasksPerNode]
    elem['accumDev'] += (endDate - initDate - elem['avg'])**2 
    
def calculateDev (dataStruct):
    for appName in dataStruct.keys():
        for numTask in dataStruct[appName].keys():
            for numNode in dataStruct[appName][numTask].keys():
                for numTasksPerNode in dataStruct[appName][numTask][numNode].keys():
                    try:
                        dataStruct[appName][numTask][numNode][numTasksPerNode]['dev'] = sqrt(dataStruct[appName][numTask][numNode][numTasksPerNode]['accumDev']/dataStruct[appName][numTask][numNode][numTasksPerNode]['count']) 
                    except:
                        dataStruct[appName][numTask][numNode][numTasksPerNode]['dev'] = -1
                
def processLogs(dataStruct, dirName):
        ##CALCULATE AVERAGE
    for fileName in os.listdir(dirName):
        if "slurm-" not in fileName:
            continue
        
        numTasks = 0
        numNodes = 0
        numTasksPerNode = 0
        initDate = 0
        endDate = 0
        
        fullFileName = dirName + "/" + fileName
        fullFile = open(fullFileName, 'r')
        
        for line in fullFile.readlines():

            #NAME IS SOMETHING LIKE "lu.A.2" 
            if line.startswith("CODE="):
                splitLine = line.split("=")
                fullAppName = splitLine[1].strip()
                fullAppNameSplit= fullAppName.split(".")
                appName=fullAppNameSplit[0]+"." + fullAppNameSplit[1]
                
            elif line.startswith("WITH_DMTCP=TRUE"):
                appName+=".dmtcp"             
                            
            elif line.startswith("TASKS="):
                splitLine = line.split("=")
                numTasks = int(splitLine[1])
                
            elif line.startswith("NODES="):
                splitLine = line.split("=")
                numNodes = int(splitLine[1])
                
            elif line.startswith("TASKS_PER_NODE="):
                splitLine = line.split("=")
                numTasksPerNode = int(splitLine[1])
                
            elif line.startswith("INITDATE="):
                splitLine = line.split("=")
                initDate = int(splitLine[1])
                
            elif line.startswith("ENDDATE="):
                splitLine = line.split("=")
                endDate = int(splitLine[1])
                
        if (numTasks != 0) and (numNodes!=0) and (numTasksPerNode!=0) and (initDate != 0) and (endDate != 0):
            updateStats(dataStruct, appName, numTasks, numNodes, numTasksPerNode, initDate, endDate)
            global firstJobInit 
            firstJobInit = min(firstJobInit, initDate)
            global lastJobEnd
            lastJobEnd = max(lastJobEnd, endDate)
            
        
    ##CALCULATE STANDARD DEV
    for fileName in os.listdir(dirName):
        if "slurm-" not in fileName:
            continue
        
        numTasks = 0
        numNodes = 0
        numTasksPerNode = 0
        initDate = 0
        endDate = 0
        
        fullFileName = dirName + "/" + fileName
        fullFile = open(fullFileName, 'r')
        
        for line in fullFile.readlines():
            
            #NAME IS SOMETHING LIKE "lu.A.2" 
            if line.startswith("CODE="):
                splitLine = line.split("=")
                fullAppName = splitLine[1].strip()
                fullAppNameSplit= fullAppName.split(".")
                appName=fullAppNameSplit[0]+"." + fullAppNameSplit[1]
                
            elif line.startswith("WITH_DMTCP=TRUE"):
                appName+=".dmtcp"               
                
            elif line.startswith("TASKS="):
                splitLine = line.split("=")
                numTasks = int(splitLine[1])
                
            elif line.startswith("NODES="):
                splitLine = line.split("=")
                numNodes = int(splitLine[1])
                
            elif line.startswith("TASKS_PER_NODE="):
                splitLine = line.split("=")
                numTasksPerNode = int(splitLine[1])
                
            elif line.startswith("INITDATE="):
                splitLine = line.split("=")
                initDate = int(splitLine[1])
                
            elif line.startswith("ENDDATE="):
                splitLine = line.split("=")
                endDate = int(splitLine[1])
        if (numTasks != 0) and (numNodes!=0) and (numTasksPerNode!=0) and (initDate != 0) and (endDate != 0):
            accumulateDev(dataStruct, appName, numTasks, numNodes, numTasksPerNode, initDate, endDate)
    
    calculateDev(dataStruct) 



def printSimpleResults(dataStruct):
    print ("EXECUTION RESULTS")
    print ("APP    SIZE    TIME (s)    STDEV (%)    TESTS")
    for appName in sorted(dataStruct.keys()):
        for numTask in sorted(dataStruct[appName].keys()):
            for numNode in sorted(dataStruct[appName][numTask].keys()):
                for numTasksPerNode in sorted(dataStruct[appName][numTask][numNode].keys()):
                    elem=dataStruct[appName][numTask][numNode][numTasksPerNode]
                    lineToPrint=appName + "    " +  str(numTask)+"_" + str(numNode) +"x" + str(numTasksPerNode) + "    " + str(round(elem['avg'],2)) + "    " 
                    try:
                        lineToPrint += str(round((elem['dev']*100 /elem['avg']),2)) 
                    except:
                        lineToPrint += "N/A"
                    lineToPrint += "    " + str(elem['count'])
                    print (lineToPrint)
                
                
def printComparisonWithMostConcentrated(dataStruct):
    print ("COMPARISON WITH MOST CONCENTRATED EXPERIMENT")
    print ("APP    SIZE    %    TESTS")
    for appName in sorted(dataStruct.keys()):
        for numTask in sorted(dataStruct[appName].keys()):
            for numNode in sorted(dataStruct[appName][numTask].keys()):
                for numTasksPerNode in sorted(dataStruct[appName][numTask][numNode].keys()):
                    elem=dataStruct[appName][numTask][numNode][numTasksPerNode]
                    if numTask == 1:
                        referenceElement=dataStruct[appName][1][1][1]
                    elif numTask ==2:
                        referenceElement=dataStruct[appName][2][1][2]
                    elif numTask ==4:
                        referenceElement=dataStruct[appName][4][1][4]
                    elif numTask ==8:
                        referenceElement=dataStruct[appName][8][1][8]
                    elif numTask ==16:
                        referenceElement=dataStruct[appName][16][1][16]
                    elif numTask ==32:
                        referenceElement=dataStruct[appName][32][2][16]
                    elif numTask ==64:
                        referenceElement=dataStruct[appName][64][4][16]
                    elif numTask ==128:
                        referenceElement=dataStruct[appName][128][8][16]    
    
                    lineToPrint=appName + "    " + str(numTask)+"_" + str(numNode) +"x" + str(numTasksPerNode) + "    "
                    try:
                        lineToPrint += str(round((elem['avg'] /referenceElement['avg']),2)) 
                    except:
                        lineToPrint += "N/A"
                    lineToPrint += "    " + str(elem['count'])
                    print (lineToPrint)


#APP NAME can be "APP" or "APP.dmtcp"
def printDMTCPOverhead(dataStruct):
    print ("DMTCP OVERHEAD")
    print ("APP    SIZE    OVERHEAD % (dmtcp - no_dmtcp/no_dmtcp)")
    
    for appName in sorted(dataStruct.keys()):
        if "dmtcp" not in appName:
            for numTask in sorted(dataStruct[appName].keys()):
                for numNode in sorted(dataStruct[appName][numTask].keys()):
                    for numTasksPerNode in sorted(dataStruct[appName][numTask][numNode].keys()):
                        dmtcp_name=appName+".dmtcp"
                        elem=dataStruct[appName][numTask][numNode][numTasksPerNode]
                        try:
                            dmtcp_elem=dataStruct[dmtcp_name][numTask][numNode][numTasksPerNode]
                            overhead = (dmtcp_elem['avg']-elem['avg'])/elem['avg'] * 100
                            lineToPrint=appName + "    " +  str(numTask)+"_" + str(numNode) +"x" + str(numTasksPerNode) + "    " + str(round(overhead))
                            print (lineToPrint)
                        except:
                            continue
                                    
def printClusterUsage(dataStruct):
    print ("CLUSTER USAGE")
    
    print ("\nstart of the first job")
    print time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(firstJobInit))
    
    print ("\nend of the last job")
    print time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(lastJobEnd))
    
    seconds = lastJobEnd-firstJobInit
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)

    print ("\ntotal execution time")
    print ("%d:%02d:%02d" % (h, m, s))
    
    totalSeconds = 0
    for appName in sorted(dataStruct.keys()):
        for numTask in dataStruct[appName].keys():
            for numNode in dataStruct[appName][numTask].keys():
                for numTasksPerNode in dataStruct[appName][numTask][numNode].keys():
                    totalSeconds += dataStruct[appName][numTask][numNode][numTasksPerNode]['avg'] * dataStruct[appName][numTask][numNode][numTasksPerNode]['count'] * numTask
    
    CPUhours = round (totalSeconds / 3600,2)
    print ("\nCPU hours")
    print (str(CPUhours))
    
    usage = round (100 * totalSeconds / ( seconds * clusterSize),2)
    print ("\nCluster usage")
    print (str(usage) + "%")
    
    
    
    
                                
#INPUT PARAMETERS:
#$1: path of input files
#$2: path of output files (Slurm scripts)
#$3: prefix
if __name__ == '__main__':
    
    if len(argv) not in [2,3]:
        print ("Usage: executionAnalysis.py <work dir> [<reference dir>]")
        exit(0)
    
    work_dir=argv[1]
    reference_dir=None
    try:
        reference_dir=argv[2]
    except:
        pass
    
    executionResults={}
    referenceExecutionResults={}

    
    print ("experiment folder: " + work_dir)    
    print ("\nProcessing logs")
    processLogs(executionResults, work_dir)
    if reference_dir is not None:
        print ("\nProcessing reference logs")
        processLogs(referenceExecutionResults, reference_dir)

    printSimpleResults(executionResults)
    
    print ("\n\n\n")
    printComparisonWithMostConcentrated(executionResults)

    print ("\n\n\n")
    printDMTCPOverhead(executionResults)
    
        
    print ("\n\n\n")
    printClusterUsage(executionResults)
    
    
    