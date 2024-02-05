#!/bin/bash

set -e

usage() {
  echo "Usage: $0 [-d maxdepth] [-e exclude-path] STARTING-POINT QUERY-STRING"
  echo "STARTING-POINT : Location from where search should start"
  echo "QUERY-STRING : UNIX pattern used for matching and selecting results. Needs to be \"quoted\""
  echo "max-depth : Descend at most max-depth levels from STARTING-POINT"
  echo "exclude-string : Exclude paths matching this UNIX pattern from final result. Needs to be \"quoted\""
  echo "-----"
  echo "Example: $0 -d 3 . \"*.xosc\""
}

args=()

while getopts "hd:e:" flag; do
case "$flag" in
  h) 
    usage
    exit 0
    ;;
  d) args=(-maxdepth "$OPTARG" "${args[@]}");;
  e) args+=(-not -path "$OPTARG");;
esac
done

shift $(($OPTIND-1)) # return to usual handling of positional args
if [ $# -lt 2 ]; then
  usage
  exit 1
fi
startingPoint=$1
queryStr=$2

matrixArray=$(find ~+/$startingPoint "${args[@]}" -name "$queryStr")

printf %"s\n" "Selected paths:" "$matrixArray"
echo "$matrixArray" | \
  jq --slurp --raw-input 'split("\n")[:-1]' | \
  jq  "{\"filepath\": .[] }" | \
  jq -c '(.filepath / "/" | {filedir: (.[0:-1] | join("/")),filename: .[-1]})' | \
  jq -sc "{ \"include\": . }" \
  > matrix.tmp
echo "MATRIX=$(cat ./matrix.tmp)" >> "$GITHUB_OUTPUT"
