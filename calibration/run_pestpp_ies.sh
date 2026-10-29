#!/bin/bash
# Run PEST++ IES with local agents (adjust NAGENTS to your cores)
# usage: bash run_pestpp_ies.sh full_model [dataset ...]
#        bash run_pestpp_ies.sh reduced_setups [set-up ...]
set -e
ROOT=$(cd "$(dirname "$0")" && pwd)/$1; shift
EXE=${PESTPP_IES:-pestpp-ies}
NAGENTS=${NAGENTS:-2}
VARIANTS=${@:-$(ls $ROOT)}
for v in $VARIANTS; do
  T=$ROOT/$v
  M=$ROOT/$v/master
  rm -rf $M; mkdir -p $M; cp $T/* $M/ 2>/dev/null || true
  PORT=$((4100 + RANDOM % 500))
  (cd $M && $EXE $v.pst /h :$PORT > master.log 2>&1) &
  MPID=$!
  sleep 3
  for i in $(seq 1 $NAGENTS); do
    A=$ROOT/$v/agent_$i
    rm -rf $A; mkdir -p $A; cp $T/* $A/ 2>/dev/null || true
    (cd $A && $EXE $v.pst /h localhost:$PORT > agent.log 2>&1) &
  done
  wait $MPID
  pkill -f "$v.pst /h localhost:$PORT" || true
  rm -rf $ROOT/$v/agent_*
  echo "$v done"
done
