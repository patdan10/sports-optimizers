#!/bin/bash
### Job Parameters:
#SBATCH --job-name  "BEN" # display name
#SBATCH --output    "%j noneout.log"   # where to log terminal output 
#SBATCH --error     "%j noneerr.log"   #  .. and error messages
#SBATCH --open-mode truncate    # always overwrite log files 

# Resources required
#SBATCH --ntasks 1          # number of tasks we'll perform
#SBATCH --cpus-per-task 1   # num. cpus each task will require
#SBATCH --mem-per-cpu 1024   # memory required per cpu (in megabytes)

source /opt/conda/bin/activate py37 

echo -e 'R\nS\nN\nN\n' | python mainSoc.py 

