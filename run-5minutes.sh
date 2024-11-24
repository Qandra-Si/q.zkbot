#!/bin/bash

NOW_ALL=$(date --utc)
echo "Start ALL at $NOW_ALL"
START_TIME_ALL=$(date +%s)
RUN_DIR=$(dirname -- "$0")

echo
echo "<<<               >>>"
echo "<<< run-killmails >>>"
echo "<<<               >>>"
for pilot_name in "$@"; do
  $RUN_DIR/.venv/bin/python3 $RUN_DIR/q_loader.py --pilot="$pilot_name" --online --cache_dir=$RUN_DIR/.q_zkbot
done

/usr/bin/df -h

END_TIME_ALL=$(date +%s)
DIFF_ALL=$(( $END_TIME_ALL - $START_TIME_ALL ))
echo "ALL took $DIFF_ALL seconds"
