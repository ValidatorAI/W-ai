#!/usr/bin/env bash
# snapshot.sh — DB snapshot before gates; FREEZE marker management.
set -e
DB=~/Documents/codes/Pavel/W/pwr/storage/db/development.sqlite3
T2=~/Documents/codes/Pavel/W/W-ai/"pwr tests"/"test 2"
case "${1:-snap}" in
  snap) ts=$(date +%Y%m%d-%H%M%S); cp "$DB" "$T2/t2-snap-$ts.sqlite3"; echo "snapshot: $T2/t2-snap-$ts.sqlite3";;
  freeze) touch "$T2/FREEZE"; echo "FREEZE set (10-min graded-write guard)";;
  release) rm -f "$T2/FREEZE"; echo "FREEZE cleared";;
esac
