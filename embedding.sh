#!/bin/bash

if [ -z "$1" ]; then
    echo "Error: Please provide text as an argument"
    echo "Usage: ./embedding.sh 'your text here'"
    exit 1
fi

python commands.py --command embedding --text "$1" 