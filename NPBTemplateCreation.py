'''
Created on 19 oct. 2016

@author: supermanue
'''
from sys import argv, exit
import os
from Queue import Full

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


npbApps =["bt", 
          "cg",
          "ep",
          "ft",
          "is", 
          "lu",
          "mg"]

npbClasses=["A", 
          "B",
          "C"]

forbiddenCombinations=[["bt", "A", 2],
                       ["bt", "B", 2],
                       ["bt", "C", 2],
                       
                       ["bt", "A", 8],
                       ["bt", "B", 8],
                       ["bt", "C", 8],
                       
                       ["bt", "A", 32],
                       ["bt", "B", 32],
                       ["bt", "C", 32],
                       
                       ["bt", "A", 128],
                       ["bt", "B", 128],
                       ["bt", "C", 128],
                       
                       ]

#INPUT PARAMETERS:
#$1: path of input files
if __name__ == '__main__':
    
    if len(argv) != 2:
        print ("Usage: templateCreation.py <work dir>")
        exit(0)
    work_dir=argv[1]
    
    
    for appName in npbApps:
        for className in npbClasses:
            for combination in combinationsACME:
                for with_dmtcp in [True, False]:
                    numTasks = combination[0]
                    numNodes = combination[1]
                    numTasksPerNode = combination[2]
                    
                    if [appName, className, numTasks] in forbiddenCombinations:
                        continue
                    
                    file_prefix= appName + "." + className + "." + str(numTasks)
                                           
                    fullApp="/home/localsoft/NPB/bin/" + file_prefix
                    
                    if with_dmtcp:
                        output_file_name = work_dir + "/" + file_prefix + "_dmtcp_" + str(numNodes) + "x" + str(numTasksPerNode) + ".sh"
                    else:
                        output_file_name = work_dir + "/" + file_prefix + "_" + str(numNodes) + "x" + str(numTasksPerNode) + ".sh"
                        
                    output_file = open(output_file_name, 'w')
                    
                    output_file.write("#!/bin/bash" + "\n")
                    output_file.write("#SBATCH --nodes=" + str(numNodes)+ "\n")
                    output_file.write("#SBATCH --ntasks-per-node=" + str(numTasksPerNode)+ "\n")
                    
                    if with_dmtcp: 
                        output_file.write("#SBATCH --with-dmtcp \n")
                    
                    output_file.write("TASKS=" + str(numTasks)+ "\n")
                    output_file.write("NODES=" + str(numNodes)+ "\n")
                    output_file.write("TASKS_PER_NODE=" + str(numTasksPerNode)+ "\n")
                    if with_dmtcp:
                        output_file.write("WITH_DMTCP=TRUE\n")
                        
                    output_file.write(""+ "\n")
                    output_file.write("echo \"TASKS=" + str(numTasks)+"\""+ "\n")
                    output_file.write("echo \"NODES=" + str(numNodes)+"\""+ "\n")
                    output_file.write("echo \"TASKS_PER_NODE=" + str(numTasksPerNode)+"\""+ "\n")
                    output_file.write("echo \"CODE=" + file_prefix+"\""+ "\n")
                    if with_dmtcp:
                        output_file.write("echo \"WITH_DMTCP=TRUE\"\n")
                    output_file.write("echo \"INITDATE=`date +%s`\""+ "\n")
                    output_file.write(""+ "\n")
                    output_file.write("srun " + fullApp+ "\n")
                    output_file.write(""+ "\n")
                    output_file.write("echo \"ENDDATE=`date +%s`\""+ "\n")
                    
                    output_file.close()