#!/bin/bash
#SBATCH --partition=prod
#SBATCH --job-name=IsoCortexConnAnalysis
#SBATCH --output="isocortex_conn_analysis-%j.out"
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

#echo "Launch pathway synapse count analysis, heatmap" (must have been done in a previous run)
#python $SCRIPT --analyze --region=$REGION --phenomenon=pair_synapse_count --sample-size=100 --cache-size=100 $ISOCIRCUIT $NEOVALARXIV
echo "Launch bouton density analysis, bars" 
python $SCRIPT --analyze --region=$REGION --phenomenon=bouton_density --sample-size=100 --cache-size=100 $ISOCIRCUIT $NEOVALARXIV
#echo "Launch connection probability analysis, heatmap"
#python $SCRIPT --analyze --region=$REGION --phenomenon=pathway_connection_probability --sample-size=100 --cache-size=100 $ISOCIRCUIT $NEOVALARXIV
