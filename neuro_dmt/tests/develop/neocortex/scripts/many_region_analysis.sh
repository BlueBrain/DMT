#!/bin/bash
ME=/gpfs/bbp.cscs.ch/home/sood
module load nix/python/3.6-full
module load nix/py36/ipython/6.2.1
module load nix/hpc/flatindexer-py3
source $ME/.vmgr_repo/nix36/bin/activate

ANALYSIS=$1
HEMISPHERE=$2
CONNECTOMEDIRECTION=$3

PROJ68=/gpfs/bbp.cscs.ch/project/proj68
ISODIR=$PROJ68/circuits/Isocortex/20190307/connectome/functional


REGIONS="ACAd ACAv AId AIp AIv AUDd AUDp AUDv ECT FRP GU ILA MOp MOs ORBl 
ORBm ORBvl PERI PL RSPagl RSPd RSPv SSp-ll SSp-m SSp-n SSp-tr SSp-ul
SSp-un SSs TEa TEa VISC VISa VISal VISam VISl VISli VISp VISpl VISpm"

for REGION in $REGIONS; do
    echo "run for region "$REGION@$HEMISPHERE
    sbatch $ANALYSIS.sbatch\
           $REGION@$HEMISPHERE\
           $ISODIR/$REGION@$HEMISPHERE/CircuitConfig-$CONNECTOMEDIRECTION
done
