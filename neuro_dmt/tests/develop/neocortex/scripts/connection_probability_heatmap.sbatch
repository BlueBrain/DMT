#!/bin/bash
#SBATCH --partition=prod
#SBATCH --job-name=ConnProbHeatMap
#SBATCH --output="connprob_heatmap-%j.out"
#SBATCH --time=16:00:00
#SBATCH --mem=32G
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --account=proj68

export REGION=$1
export ISOCIRCUIT=$2

WORK=/gpfs/bbp.cscs.ch/home/sood/work
DMT=$WORK/validations/dmt
SCRIPT=$DMT/neuro_dmt/tests/develop/neocortex/scripts/validation_suite.py
NEOVALARXIV=$WORK/validations/release/neocortex-2019/arxiv
echo "Analyze circuit "$ISOCIRCUIT
echo "Region "$REGION
echo "Save results at"$NEOVALARXIV

echo "Launch connection probability analysis, between cells within 100um"
python $SCRIPT\
       --analyze\
       --region=$REGION\
       --phenomenon=pathway_connection_probability\
       --upper-bound-soma-distance=100\
       --sample-size=100\
       --cache-size=100\
       $ISOCIRCUIT\
       $NEOVALARXIV
# echo "Launch connection probability analysis, between cells within 200um"
# python $SCRIPT\
#        --analyze\
#        --region=$REGION\
#        --phenomenon=pathway_connection_probability\
#        --upper-bound-soma-distance=200\
#        --sample-size=1000\
#        --cache-size=1000\
#        $ISOCIRCUIT\
#        $NEOVALARXIV
