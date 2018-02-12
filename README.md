# softBits
small scripts for different stuff

This is the place where I store small things used on my dialy work. It is not documented and probably has no utility for anybody but me.

## File description

### createRandomWorkload
- creates a random workload for slurm

- executes the workload

- monitors the execution and creates a couple of files with the info, which can later be analyzed with statsFromExecutionAnalysis

- workload description:
  - normal distribution of job size
  - normal distribution of job lenght
  - random execution on time

- exports job distribution in a .pickle file, so it can be re-run. To do so you have to employ a different input parameter


## statsFromExecutionAnalysis

- analyzes the results of a workload created with createRandomWorkload

## statisticalDescriptionOfWorkload
- some stats about a paticular workload (pickle file): job lenght, distribution and so


## slurm benchmarking (folder)
- some files to execute a benchmark and analyze the results.
