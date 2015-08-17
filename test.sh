#!/bin/sh

export PATH=/usr/local/bin:/usr/bin:/usr/local/sbin:$PATH
export PATH=/usr/local/mysql/bin:$PATH
export PATH=/usr/local/bin:$PATH
# set PATH so it includes geni software if it exists
# set PATH so it includes geni software if it exists
if [ -d "/home/sedwards/gcf/src" ] ; then
    PATH="/home/sedwards/gcf/src:/home/sedwards/gcf/examples:$PATH"
    PATH="/home/sedwards/geni-lib/geni:$PATH"
    export PYTHONPATH="/home/sedwards/gcf/src:$PYTHONPATH"
    export PYTHONPATH="/home/sedwards/geni-lib:$PYTHONPATH"
fi

#echo $PATH
#echo
#echo $PYTHONPATH

now=$(date +"%Y%m%d_%H%M%S")
#echo $now

file=/tmp/vmavail-$now.out
echo Status Collected at $now > $file
python /home/sedwards/geni-lib/samples/checkvmavail.py 
#>> $file
