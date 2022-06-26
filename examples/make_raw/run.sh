#!/bin/bash

#export ISOTOPES="/rds/homes/b/bxp912/apps/python/data/isotopes.pz"
#export TALYS="/rds/homes/b/bxp912/apps/talys/bin/talys"
#export TALYS_RUN="/rds/homes/b/bxp912/apps/python/make_talys_data.py"

export PYBIN="python3"
export MAKE_TALYS_DATA="../../src/make_talys_data.py"

export PROC_COUNT=8
export ISOTOPES="../../data/isotopes.pz"
export TALYS_BIN="/DATA/disk1/talys/bin/talys"

export PROJECTILES="n"
export LOWER_Z=3
export UPPER_Z=18

export LOWER_E=0.01
export UPPER_E=0.20
export INC_E=0.01

$PYBIN $MAKE_TALYS_DATA 0 &   PIDAA=$!
$PYBIN $MAKE_TALYS_DATA 1 &   PIDAB=$!
$PYBIN $MAKE_TALYS_DATA 2 &   PIDAC=$!
$PYBIN $MAKE_TALYS_DATA 3 &   PIDAD=$!
$PYBIN $MAKE_TALYS_DATA 4 &   PIDAD=$!
$PYBIN $MAKE_TALYS_DATA 5 &   PIDAD=$!
$PYBIN $MAKE_TALYS_DATA 6 &   PIDAD=$!
$PYBIN $MAKE_TALYS_DATA 7 &   PIDAD=$!
wait

