#!/bin/bash

base="$PWD"
dirs=$(find $PWD -type d)
for d in $dirs;
do
    if [ -d "$d/.git" ]; then
        echo $d
        cd $d
        git pull
        cd $base
    fi
done
