#!/bin/bash
#SBATCH --partition=prod
#SBATCH --job-name=IsoCortexConnProb
#SBATCH --output="isocortex_connprob-%j.out"
#SBATCH --time=16:00:00
#SBATCH --mem=32G
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --account=proj68

export REGION=$1
export ISOCIRCUIT=$2

export SCRIPT=/gpfs/bbp.cscs.ch/home/sood/work/validations/dmt/neuro_dmt/tests/develop/neocortex/scripts/validation_suite.py
export NEOVALARXIV=/gpfs/bbp.cscs.ch/home/sood/work/validations/release/neocortex-2019/arxiv
echo "Analyze circuit "$ISOCIRCUIT
echo "Region "$REGION
echo "Save results at"$NEOVALARXIV

echo "Launch connection probability analysis, by distance"
python $SCRIPT --analyze --region=$REGION --phenomenon=pathway_connection_probability --by-distance --sample-size=100 --cache-size=100 --pathways=to_pc_pathways $ISOCIRCUIT $NEOVALARXIV
echo "Launch connection probability analysis, by distance"
python $SCRIPT --analyze --region=$REGION --phenomenon=pathway_connection_probability --by-distance --sample-size=100 --cache-size=100 --pathways=from_pc_pathways $ISOCIRCUIT $NEOVALARXIV
echo "Launch afferent connection count analysis"
