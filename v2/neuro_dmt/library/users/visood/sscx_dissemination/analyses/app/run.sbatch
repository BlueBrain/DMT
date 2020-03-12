#!/bin/bash -l
#SBATCH --job-name=sscx-dissemination-analysis
#SBATCH --nodes=1
#SBATCH --time=24:00:00
#SBATCH --exclusive
#SBATCH --constraint=cpu
#SBATCH --mem=0
#SBATCH --partition=prod
#SBATCH --account=proj83
#SBATCH --output="sscxdiss-analysis-number_afferent_connections"

#module list
#module load archive/2020-02
#module load py-bluepy/0.14.6
#which python

venv=$1
name_circuit=$2
path_output_folder=$3
target=$4

source $venv

srun \
     python number_afferent_connections.py \
       $name_circuit \
       $path_output_folder \
       $target
