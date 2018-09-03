#!/bin/bash -l
#SBATCH --job-name="connectome_validation"
#SBATCH --account=proj64
#SBATCH --partition=prod
#SBATCH --nodes=1
#SBATCH --mem=4096
#SBATCH --time=1-00:00:00
#SBATCH --output=stdout.log
#SBATCH --error=stderr.err

module purge

module load nix/python/3.6-full
module load nix/hpc/flatindexer-py3

source ~/.bashrc
echo "Will launch" 
~/.vmgr_repo/nix36/bin/activate
python connectome.py
