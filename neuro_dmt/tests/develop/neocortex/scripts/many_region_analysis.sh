#!/bin/bash
export ME=/gpfs/bbp.cscs.ch/home/sood
module load nix/python/3.6-full
module load nix/py36/ipython/6.2.1
module load nix/hpc/flatindexer-py3
source $ME/.vmgr_repo/nix36/bin/activate

export ISODIR=/gpfs/bbp.cscs.ch/project/proj68/circuits/Isocortex/20190307/connectome/functional

ANALYSIS=$1

regions_one="ACAd ACAv AId AIp AIv AUDd AUDp AUDv ECT FRP GU ILA MOp MOs ORBl"
regions_two="ORBm ORBvl PERI PL RSPagl RSPd RSPv SSp-ll SSp-m SSp-n SSp-tr SSp-ul"
regions_thr="SSp-un SSs TEa TEa VISC VISa VISal VISam VISl VISli VISp VISpl VISpm VISpor VISrl"

for region in $regions_one; do
    echo "run for region "$region@left
    sbatch $ANALYSIS.sbatch $region@left $ISODIR/$region@left/CircuitConfig-eff
    echo "run for region "$region@right
    sbatch $ANALYSIS.sbatch $region@right $ISODIR/$region@right/CircuitConfig-eff
done
for region in $regions_two; do
    echo "run for region "$region@left
    sbatch $ANALYSIS.sbatch $region@left $ISODIR/$region@left/CircuitConfig-eff
    echo "run for region "$region@right
    sbatch $ANALYSIS.sbatch $region@right $ISODIR/$region@right/CircuitConfig-eff
done
for region in $regions_thr; do
    echo "run for region "$region@left
    sbatch $ANALYSIS.sbatch $region@left $ISODIR/$region@left/CircuitConfig-eff
    echo "run for region "$region@right
    sbatch $ANALYSIS.sbatch $region@right $ISODIR/$region@right/CircuitConfig-eff
done
