# semaphore
<<<<<<< HEAD
Controls multiple jobs to be executed in sequence and in defined daily time
frame. It requires handling of the return it’s codes on the requester side.
Originally it was used to control backup process to prevent the process from
mass matrix access at the same time but it can be used to prevent two jobs to
run in the same time to prevent corruption by two jobs writing to the same data.
The script was used in production system in Python 2.6.6.

Files included:
1. /usr/local/python/control.py
  In order to control flow of jobs the python script control.py should be called
  with parameters.

  parameter 1:
    start wait for go, the process will pause till go is given, status in
          semaphore will be set to "running"
    stop  to indicate finish of the process, next job will be given option to
          run, the process will be timeouted anyway after timeoutPeriod has
          been reached, status of semaphone will be set to awaiting
  parameter 2: unique job name
  parameter 3:
    y - for /mnt/semaphore remote mount check
    n - for local /mnt/semaphore without mount

  Control.py can control jobs running from one or more local or remote machines.
  You must however define /mnt/semaphore that refer to the same remote network
  folder.
  Every local or remote machine needs to have control.py installed and
  /mnt/semaphore folder mounted.

  It returns:
    0 (retGO), when it gives OK for starting that should be confired with start
      command and ended with stop command
    1 (retWAIT), no go
    2 (retADMIN), control proceess has found a problem that requires admin
      intervention
    3 (retCONF)
    4 (retCONST)
    5 (retSYNT)
    6 (retERROR)
    7 (retMOUNT)

    It writes log to /var/log/semaphore.log. You can change location by
    finding and replacing definition in the code.

2. in /usr/local/bash folder there are files: one.bash, two.bash, three.bash
  These are example scripts to show how to handle and call control.py script.

3. in /usr/local/bash/lib.bash – this is example library containing sema bash
  function

4. /mnt/semaphore folder keeps files

  semaphore.cfg it - used for configuration, currently it keeps only time to
  wait for next prompt

  semaphoreHistory.log - this file is created and information is appended,
  it keeps history presenting when semaphore was started and stopped

  semaphoreJobs.txt - it keeps configuration for semaphore jobs

  Example:
  one.bash 1400 0 0
  two.bash 1000 11 13
  three.bash 1000 20 8

  The first column defines the job name under control.

  Second column is used for timeout. It defines number of minutes control.py
  will allow job completion before giving access to next job.
  Keep it high enough to prevent from unintended aborting.

  Third and forth column define time frame in hours for the job to allow it's
  start. When for example there is 8 16 it allows job to be allowed started
  during business hours, whet it has 16 8 it will allow running after business
  hours, when there is 0 0 it will allow the job to run without time limits.

  semaphore.txt - it keeps the name, date and time and status of job that is
  allowed, for example it can look like:
  one.bash 2018-10-31 11:48:21 running
  If control.py finds semaphore.txt to be missing or corrupted it recreates it
  starting form first job definition from semaphoreJobs.txt.

Prerequisits:
1. Python 2.6 or other version must be installed with modules:
import sys, re, datetime, time, os

2. Mount to /mnt/semaphore including configuration files as defined above
=======
Controls multiple jobs to be executed in sequence and in defined time frame
>>>>>>> 8e7bbea02c7ca96bd9559db1a3e9b8b61a25158b
