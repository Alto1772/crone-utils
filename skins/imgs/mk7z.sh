#!/bin/sh
del=0
dir="../../backups"
if [ -n "$3" ]; then dir="$3"; fi
if [ "$1" = "-d" ]; then
    del=1
    shift
fi
[ -d "$1" ] || exit 1
cd "$1"
7z a -x\!conf -x\!missing "$dir"/"$1"-"$(date +%Y%m%d%H%M%S)".7z .
[ "$del" = "1" ] && rm *.png
