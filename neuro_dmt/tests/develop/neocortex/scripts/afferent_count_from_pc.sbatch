#!/bin/bash
#SBATCH --partition=prod
#SBATCH --job-name=AffCountFromPC
#SBATCH --output="aff_count_from_pc-%j.out"
#SBATCH --time=24:00:00
#SBATCH --mem=32G
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --account=proj68

REGION=$1
ISOCIRCUIT=$2

WORK=/gpfs/bbp.cscs.ch/home/sood/work
DMT=$WORK/validations/dmt
SCRIPT=$DMT/neuro_dmt/tests/develop/neocortex/scripts/validation_suite.py
NEOVALARXIV=$WORK/validations/release/neocortex-2019/arxiv
echo "Analyze circuit "$ISOCIRCUIT
echo "Region "$REGION
echo "Save results at"$NEOVALARXIV

echo "Launch afferent connection count analysis from PC pathways"
python $SCRIPT\
       --analyze\
       --region=$REGION\
       --phenomenon=afferent_connection_count\
       --sample-size=100\
       --cache-size=100\
       --pathways=from_pc_pathways\
       --by-distance\
       $ISOCIRCUIT\
       $NEOVALARXIV