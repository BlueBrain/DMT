#!/bin/bash
#SBATCH --partition=prod
#SBATCH --job-name=IsoCortexCompVal
#SBATCH --output="isocortex_comp_val-%j.out"
#SBATCH --time=16:00:00
#SBATCH --mem=32G
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --account=proj68

REGION=$1
ISOCIRCUIT=$2

SCRIPT=/gpfs/bbp.cscs.ch/home/sood/work/validations/dmt/neuro_dmt/tests/develop/neocortex/scripts/validation_suite.py
NEOVALARXIV=/gpfs/bbp.cscs.ch/home/sood/work/validations/release/neocortex-2019/arxiv
echo "Analyze circuit "$ISOCIRCUIT
echo "Region "$REGION
echo "Save results at"$NEOVALARXIV

echo "Launch cell density validation" 
python $SCRIPT --validate --region=$REGION --phenomenon=cell_density --sample-size=100 $ISOCIRCUIT $NEOVALARXIV
echo "Launch cell ratio validation"
python $SCRIPT --validate --region=$REGION --phenomenon=cell_ratio   --sample-size=100 $ISOCIRCUIT $NEOVALARXIV