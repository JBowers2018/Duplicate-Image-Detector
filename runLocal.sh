#!/bin/bash
if [ $# -ne 1 ];
then
echo "Usage: ./runLocal.sh <image_file>"
exit 2
fi

eval "mpiexec -mca btl ^openib -n 4 python -m mpi4py did_mpi.py $1"
#eval "mpiexec -mca btl ^openib -n 4 python -m mpi4py did_mpi.py"
#eval "mpiexec -mca btl ^openib -n 4 python -m mpi4py did_mpi.py"
#eval "mpiexec -mca btl ^openib -n 4 python -m mpi4py did_mpi.py"
