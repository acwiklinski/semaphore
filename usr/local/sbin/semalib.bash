########################################################################
# Function:     sema
# Description:  Calls control.py /usr/local/python/control.py
#               if not /mntmouted psses all parameters
# Output:
# Usage:
########################################################################
sema()
{
  local retMOUNT=7

  /usr/local/python/control.py "$1" "$2" "$3"
  semaStatus=$?

  if [ $semaStatus -ne 0 ]
  then
    echo "`date` : $jobName : Error when trying to $1 semaphore, return code = $semaStatus for $2" >> $4
    if [ $semaStatus -eq $retMOUNT ]
    then
      echo "`date` : $jobName : Semaphore will be remounted in 10m" >> $VLOGFILE
      sleep 10m
      sshfs root@backupmachine:/home/mrrobot/semaphore /mnt/semaphore
    fi

    /usr/local/python/control.py "$1" "$2" "$3"
    semaStatus=$?

    if [ $semaStatus -ne 0 ]
    then
          msg="`date` : $jobName : Error when trying to $1 semaphore, return code = $semaStatus for $2 for the second time, exiting"
          echo "`date` : $2 : $msg" >> $4
          exit 1
    fi
  fi
}
