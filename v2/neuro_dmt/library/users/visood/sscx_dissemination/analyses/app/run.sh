#!/bin/bash

echo LOGLEVEL=$LOGLEVEL
venv=$1
name_circuit=$2
path_output_folder=$3
target=$4

source $venv

python number_afferent_connections.py \
    $name_circuit \
    $path_output_folder \
    $target
