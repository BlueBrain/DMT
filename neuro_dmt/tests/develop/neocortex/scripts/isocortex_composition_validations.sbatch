#!/bin/bash
#SBATCH --partition=prod
#SBATCH --job-name=IsoCompVal
#SBATCH --output="isocortex_composition_validations-%j.out"
#SBATCH --time=16:00:00
#SBATCH --mem=32G
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --account=proj68

export ME=/gpfs/bbp.cscs.ch/home/sood
module load nix/python/3.6-full
module load nix/py36/ipython/6.2.1
module load nix/hpc/flatindexer-py3
source $ME/.vmgr_repo/nix36/bin/activate

#cd /gpfs/bbp.cscs.ch/home/sood/work/validations/dmt/neuro_dmt/tests/develop/neocortex/scripts
export SCRIPT=/gpfs/bbp.cscs.ch/home/sood/work/validations/dmt/neuro_dmt/tests/develop/neocortex/scripts/isocortex_composition_validations.py
export ISODIR=/gpfs/bbp.cscs.ch/project/proj68/circuits/Isocortex/20190307/connectome/functional
export NEOVALARXIV=/gpfs/bbp.cscs.ch/home/sood/work/validations/release/neocortex-2019/arxiv
python $SCRIPT --regions=isocortex_regions $ISODIR $NEOVALARXIV