'''
Created on 19 oct. 2016

@author: supermanue
'''
from sys import argv, exit
import os

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


#INPUT PARAMETERS:
#$1: path of input files
#$2: prefix
if __name__ == '__main__':
    
    if len(argv) != 3:
        print ("Usage: templateCreation.py <work dir> <input file prefix>")
        exit(0)
    work_dir=argv[1]
    file_prefix=argv[2]
    

        
    for combination in combinationsACME:
        numTasks = combination[0]
        numNodes = combination[1]
        numTasksPerNode = combination[2]
        
        
        input_file_name = file_prefix + "." + str(numTasks)
        output_file_name = work_dir + "/" + input_file_name + "_" + str(numNodes) + "x" + str(numTasksPerNode) + ".sh"
        output_file = open(output_file_name, 'w')
        
        output_file.write("#!/bin/bash" + "\n")
        output_file.write("#SBATCH --nodes=" + str(numNodes)+ "\n")
        output_file.write("#SBATCH --ntasks-per-node=" + str(numTasksPerNode)+ "\n")
        output_file.write("TASKS=" + str(numTasks)+ "\n")
        output_file.write("NODES=" + str(numNodes)+ "\n")
        output_file.write("TASKS_PER_NODE=" + str(numTasksPerNode)+ "\n")
        output_file.write(""+ "\n")
        output_file.write("echo \"TASKS=" + str(numTasks)+"\""+ "\n")
        output_file.write("echo \"NODES=" + str(numNodes)+"\""+ "\n")
        output_file.write("echo \"TASKS_PER_NODE=" + str(numTasksPerNode)+"\""+ "\n")
        output_file.write("echo \"CODE=" + file_prefix+"\""+ "\n")
        output_file.write("echo \"INITDATE=`date +%s`\""+ "\n")
        output_file.write(""+ "\n")
        output_file.write("mpiexec lmp_mpi < " + input_file_name+ "\n")
        output_file.write(""+ "\n")
        output_file.write("echo \"ENDDATE=`date +%s`\""+ "\n")
        
        output_file.close()