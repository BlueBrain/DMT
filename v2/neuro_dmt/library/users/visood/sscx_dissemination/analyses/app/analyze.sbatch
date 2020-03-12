#!/bin/bash

echo ANALYZE
echo LOGLEVEL=$LOGLEVEL
name_analysis=$1
name_circuit=$2
path_output_folder=$3
target=$4
venv=~/.vmgr_repo/nix36/bin/activate

sbatch -J $name_circuit-$name_analysis \
       analyze \
       $venv \
       $name_analysis \
       $name_circuit \
       $path_output_folder \
       $target

