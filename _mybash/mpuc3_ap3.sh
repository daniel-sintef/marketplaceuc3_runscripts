#!/usr/bin/env sh
set -u

UUID=$1
WORKDIR=/home/$USER/flamespray_runs/$UUID 
mkdir $WORKDIR 

SUBMIT_SCRIPT=_submit_ap3.sh
cp /home/$USER/_mybash/$SUBMIT_SCRIPT  $WORKDIR/$SUBMIT_SCRIPT
cd $WORKDIR
sbatch $SUBMIT_SCRIPT
cd -
