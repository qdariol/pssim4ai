#
# File: autoscript.sh
# Author: Quentin Dariol
# Description: This script automatically cleans the model folder, builds the SystemC model, runs the simulation, and use the
#              trace_decoder.py script to estimate power and energy.
#
# Optional arguments:
#   => "-m" or "--mode":     polling without clock gating or interrupt with clock gating.
#                            Default value: P (polling). Other possible value: CG (clock gating)
#   => "-p" or "--platform": allows to specify platform dimensions among a list of pre-sets (see trace_decoder.py)
#                            Default value: 1 (default 7 tiles platform). Other possible values: 2a, 2b, 2c, 3, 4, 5.
#
# Examples: (Use without " character)
# "./autoscript.sh"
# "./autoscript.sh -m CG"
# "./autoscript.sh -m P -p 5"
#
# License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
#          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
#

# Start time recording
start=`date +%s.%N`
if test -f out.csv; then
    rm out.csv
fi
if test -f model; then
    rm model
fi

./build.sh
estimation_start=`date +%s.%N`
./model >> out.csv

# If mode (polling or clockgating) is specified for tracedecoder, use the specified mode. Else use default mode.
# Same with platform index (-p PLATFORM_INDEX)
if ! [ -z $1 ]; then
    if ! [ -z $3 ]; then
        python3 trace_decoder.py -f out.csv $1 $2 $3 $4
    else
        python3 trace_decoder.py -f out.csv $1 $2
    fi
else
    python3 trace_decoder.py -f out.csv
fi

# Stop time recording
end=`date +%s.%N`
runtime1=$( echo "$end - $start" | bc -l )
runtime2=$( echo "$end - $estimation_start" | bc -l )
echo "Total evaluation time (compilation included): $runtime1 s"
echo "Evaluation time (compilation excluded): $runtime2 s"

