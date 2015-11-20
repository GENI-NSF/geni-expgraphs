#!/bin/sh

now=$(date +"%Y%m%d_%H%M%S")
file=/tmp/vmavail-$now.out
echo Status Collected at $now > $file
python /path/to/geni-expgraphs/checkvmavail.py
