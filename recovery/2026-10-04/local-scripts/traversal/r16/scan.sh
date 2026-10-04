#!/bin/bash
# usage: scan.sh <tag> "<CTUNE args>" [seq:quit ...]   -> probes into r16/scan/<tag>
TAG=$1; CT=$2; shift 2
export OUTD=/Users/midir/sm2-n1/_scratch/traversal/r16/scan/$TAG
mkdir -p $OUTD
CTUNE="$CT" /Users/midir/sm2-n1/_scratch/traversal/r16/probe_all.sh "$@" > /dev/null
