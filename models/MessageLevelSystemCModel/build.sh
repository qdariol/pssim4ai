#!/bin/bash
# ########################################
# File: build.sh
# Authors: Ralf Stemmer, Quentin Dariol
# Description: This script builds the executable model by compiling and linking all the SystemC sources in the project.
#
# Optional arguments:
#   => "--clean": removes all object files
#
# Examples: (Use without " character)
# "./build.sh"
# "./build.sh --clean"
# If anything is specified in argument ("--clean", but in fact it can be anything - I was too lazy to implement further checks)
# Then we build everything anew.
#
# License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
#          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
#

if ! [ -z $1 ]; then
    OBJECTS=$(find obj/ -type f -name "*.o")
    rm $OBJECTS obj/lastbuild
fi

SYSTEMC="/usr/local/systemc-2.3.2"
APPS="./apps"
HEADER="-I. -I$SYSTEMC/include -I$APPS"
LIBS="-L$SYSTEMC/lib-linux64 -lsystemc $(pkg-config --libs gsl)"
CPP="g++"
CPPFLAGS="-g3 -O0 -std=c++14"

# Find sources that have been modified since last build
SOURCE=$(find . -type f -name "*.cpp" -newer obj/lastbuild) || SOURCE=$(find . -type f -name "*.cpp")

# Find .hpp files that have been modified since last build and from them, find the .cpp files that must be recompiled.
NoLastBuild=false
HPP_FILES=""
HPP_FILES=$(find . -type f -name "*.hpp" -newer obj/lastbuild) || NoLastBuild=true
if [[ $NoLastBuild = false ]]; then
    while [[ $HPP_FILES == *".hpp"* ]]
    do
        HPP_FILES_TEMP=$HPP_FILES
        for file in $HPP_FILES_TEMP;
        do
            file="$file"
            if [[ $file == *".hpp"* ]]; then
                if [[ $file == "./"* ]]; then
                    char="./"
                    tmp_file="${file//$char}"
                fi
                OTHER_FILES_WHICH_QUOTE_FILE=$(grep -l --include=\*.{cpp,hpp} -Rnw '.' -e "$tmp_file")
                char=$'\n'
                OTHER_FILES_WHICH_QUOTE_FILE="$char$OTHER_FILES_WHICH_QUOTE_FILE"
                HPP_FILES+=$OTHER_FILES_WHICH_QUOTE_FILE
                HPP_FILES=${HPP_FILES[@]/$file}
            fi
        done
    done
    for file in $HPP_FILES;
    do
        if [[ $file == "./"* ]]; then
            HPP_FILES=${HPP_FILES[@]/$file}
            char="./"
            file="${file//$char}"
            char=$'\n'
            file="$char$file"
            HPP_FILES+=$file
        fi
    done
    HPP_FILES=$(printf "%s\n" "${HPP_FILES[@]}" | sort -u)
fi

SOURCE+=$HPP_FILES

for c in $SOURCE ;
do
    >&2 echo -e "\e[1;34mCompiling $c …\e[0m"
    $CPP $HEADER $CPPFLAGS -c -o "./obj/${c%.*}.o" $c
done
touch obj/lastbuild

OBJECTS=$(find obj/ -type f -name "*.o")

$CPP -o model $OBJECTS $LIBS
