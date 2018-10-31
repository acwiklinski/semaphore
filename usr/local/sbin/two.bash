#!/bin/bash
################################################################################
# File:    two.bash
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

jobName="two.bash"
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
  echo "Start loop for $jobName"
  sema "start" "$jobName" "n" "$LOGFILENAME"
  echo "Start doing some processing of $jobName"
  sleep 10s
  echo "End processing"
  sema "stop" "$jobName" "n" "$LOGFILENAME"
  echo "End loop for $jobName"
done
