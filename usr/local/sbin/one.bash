#!/bin/bash
################################################################################
# File:    one.bash
# Descr:
#         This script is to present how to run handle and run control.py
#
# Param:
# Req.:
# Call:
#
# Author:  Aleksander Cwiklinski
# Date:
#
# Changes:
# Date:
# Descr:
################################################################################

jobName="one.bash"
LOGFILENAME="/var/log/""$jobName""log"

#include library
LIBSCRIPT="/usr/local/sbin/semalib.bash"
source "$LIBSCRIPT"
if [ $? -gt 0 ]
then
  echo "`date`: Missing library $LIBSCRIPT"
  exit 1
fi

# infinite loop
while [[ True ]]; do
  sema "start" "$jobname" "n" "$LOGFILENAME"
  echo "Start doing some processing of $jobName"
  sleep 5m
  echo "End processing"
  sema "stop" "$jobname" "n" "$LOGFILENAME"
done
