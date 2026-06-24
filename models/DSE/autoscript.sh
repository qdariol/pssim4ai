#!/bin/bash
cd ../MessageLevelSystemCModel

if test -f out.csv; then
    rm out.csv
fi
if test -f model; then
    rm model
fi

./build.sh
#~ estimation_start=`date +%s.%N`
./model >> out.csv
