#!/usr/bin/python
import sys
import re
import datetime
import time
import os
import ConfigParser

retGO=0
retWAIT=1
retADMIN=2
retCONF=3
retCONST=4
retSYNT=5
retERROR=6
retMOUNT=7

TIMEOUTDEFAULT=15

LOG="/var/log/semaphore.log"

def printInfo():
    print(var)
    for theLine in Jobs:
        print(theLine.rstrip())

def Timeouted(pSemaphoreJobTimeoutDateTime):
    # compares current time againts timeout datatime for job currently running
    if pSemaphoreJobTimeoutDateTime <= datetime.datetime.now():
        pLine("Timeout detected ...")
        return 1
    else:
        return 0

def nextSemaphore(pCurrentIndex, pJobs, pSemaphore, pJobStatus):
    #build line to write to
    pNumberOfJobs = len(pJobs)
    if pCurrentIndex >= 0:
        pCurrentIndex += 1
        if pCurrentIndex >= pNumberOfJobs:
            pCurrentIndex = 0
        pNewJob = re.split('\s+', pJobs[pCurrentIndex])[0]
    else:
        # init semaphore by taking first job name to init semaphore
        pNewJob = re.split('\s+', pJobs[0])[0]
    # sets next job for semaforJobs
    pCurrentJobLine = pNewJob + " " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + str(pJobStatus)
    pLine("New semaphore line: " + pCurrentJobLine)
    testMount()
    with open(pSemaphore, 'w') as f:
        f.write(pCurrentJobLine)
    return pCurrentJobLine

def setStatusSemaphore(pCurrentJobLine, pSemaphore, pJobStatus):
    line = re.split('\s+', pCurrentJobLine)
    pCurrentJobLine = line[0] + " " + line[1] + " " + line[2] + " " + str(pJobStatus)
    pLine("New semaphore line: " + pCurrentJobLine)
    testMount()
    with open(pSemaphore, 'w') as f:
        f.write(pCurrentJobLine)
    return pCurrentJobLine

def parseSemaphore(pCurrentJobLine):
    # retries parameters form the line specified in argument
    semaphoreDetails=re.split('\s+', pCurrentJobLine)
    assert len(semaphoreDetails) >= 1, "Data wrong in semaphore.txt"
    pSemaphoreJob=semaphoreDetails[0]
    semaphoreTimestamp=""
    if len(semaphoreDetails) >= 4 :
        pSemaphoreTimestampString=semaphoreDetails[1] + " " + semaphoreDetails[2]
        pSemapforeDateTime=datetime.datetime.strptime( pSemaphoreTimestampString, "%Y-%m-%d %H:%M:%S")
        pJobStatus= semaphoreDetails[3]
    else:
        exitControl(retCONF)
    return pSemaphoreJob, pSemapforeDateTime, pJobStatus

def readParams(pJobs):
    if numberOfArgs != 4 :
        printInfo()
        exitControl(retSYNT)
    pCommand=str(sys.argv[1])
    pJobName=str(sys.argv[2])
    pMount=str(sys.argv[3])
    pLine("Command: " + pCommand)
    pLine("Job: " + pJobName)
    pLine("Remote Mount: " + pMount)
    if pCommand not in ['start', 'stop']:
        exitControl(retSYNT, "Wrong command: " + pCommand + " given")
    jobValid, CurrentIndex = validateGetJobDetails(pJobName, pJobs)
    if not jobValid:
        exitControl(retSYNT, pJobName)
    if pMount not in ['y', 'n']:
        exitControl(retSYNT, "Wrong remote mount parameter: " + pMount + " given")
    return pCommand, pJobName, pMount

def readSemaphore(pSemaphore):
    testMount()
    try:
        with open(pSemaphore) as f2:
            pCurrentJobLine = f2.readline()
    except IOError:
        pLine("There was an error opening: " + pSemaphore + " initiating it.")
        pCurrentJobLine=""
    return pCurrentJobLine

def validateGetJobDetails(pJobName, pJobs):
    # test if job is valid (in the list)
    jobValid = False
    i=0
    pCurrentIndex=-1
    for job in pJobs :
        jobDetails=re.split('\s+', job)
        assert len(jobDetails) >= 2, "Data wrong in semaphoreJobs.txt"
        jobDetails[0]
        if jobDetails[0] == pJobName :
            jobValid = True
            pCurrentIndex = i
        i += 1
    return jobValid, pCurrentIndex

def readJobs(pSemaphoreJobs):
#read jobs into table
    testMount()
    with open(pSemaphoreJobs) as f1:
        pJobs = f1.readlines()
    return pJobs

def calculateTimeout(pSemaphoreJob, pSemapforeDateTime, pJobs):
    foundJob = False
    for job in pJobs:
        jobDetails=re.split('\s+', job)
        assert len(jobDetails) >= 4, "Data corrupted in semaphoreJobs.txt" + str(jobDetails)
        if pSemaphoreJob == jobDetails[0]:
            foundJob = True
            semaphoreJobTimeoutMinutes = jobDetails[1]
            pFrom = int(jobDetails[2])
            pTo = int(jobDetails[3])
    if not foundJob :
        exitControl(retCONF, "Data corrupted, could not find job from semaphore in definition file, reset semaphore file.")
    if not isInt(semaphoreJobTimeoutMinutes):
        semaphoreJobTimeoutMinutes = TIMEOUTDEFAULT
    pTime=setNextDateTimePeriod(pSemapforeDateTime, semaphoreJobTimeoutMinutes, pFrom, pTo)
    return pTime, pFrom, pTo

def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

# returns True when job can be run based on from to with compare with current goHour
def goHour(sHour, pFrom, pTo):
    iHour = int(sHour)
    if pTo > pFrom :
        return iHour >= pFrom and iHour < pTo
    elif pTo < pFrom :
        return not (iHour >= pTo and iHour < pFrom)
    else :
        return True

def setNextDateTimePeriod(pSemapforeDateTime, pSemaphoreJobTimeoutMinutes, iFrom, iTo):
    # iFrom - iTo is period to testagainst current date time
    # when time is valid for job to run use currnet datetime otherwise set date time to be beginning of allowed period
    if goHour(pSemapforeDateTime.strftime("%H"),iFrom, iTo):
        # awaiting for job initated within valid period, so there was ok for job to start work
        tTime=pSemapforeDateTime + datetime.timedelta(0,0,0,0,int(pSemaphoreJobTimeoutMinutes))
    else:
        # awaiting for job was started after valid period
        # timeout as pSemaphoreJobTimeoutMinutes after first From hour directltly after pSemapforeDateTime
        # calulate following From hour after pSemapforeDateTime
        pSemaphoreMorningStr = pSemapforeDateTime.strftime('%Y-%m-%d ') + "00:00:00"
        pSemaphoreMorning = datetime.datetime.strptime( pSemaphoreMorningStr, "%Y-%m-%d %H:%M:%S")
        iDayOffset=0
        if int(pSemapforeDateTime.strftime("%H")) > iFrom:
            iDayOffset+=1
        tTime = pSemaphoreMorning + datetime.timedelta(iDayOffset,0,0,0,iFrom*60+int(pSemaphoreJobTimeoutMinutes))
    return tTime

def modificationDate(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

def pLine(pLineStr):
    with open(LOG, "a") as lf:
        lf.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " : " + Command + " : " + JobName + " : " + remoteMount + " : " + pLineStr + "\n")

def pHLine(pLineStr):
    pLine(pLineStr)
    with open(HISTORY_LOG, "a") as lf:
        lf.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " : " + Command + " : " + JobName + " : " + remoteMount + " : " + pLineStr + "\n")

def testMount():
    if remoteMount in ['y']:
        if not os.path.ismount(SEFAPHORE_FOLDER):
            exitControl(retMOUNT)

def exitControl(pRetCode, pComment=""):
    if pRetCode == retGO :
        pHLine("Opening semaphore: " + JobName + " " + pComment + ".")
    elif pRetCode == retWAIT :
        pHLine("RED light for: " + JobName + " " + pComment + ".")
    elif pRetCode == retADMIN :
        pHLine("Admin intervation error" + " " + pComment + ".")
    elif pRetCode == retCONF :
        pHLine("Configuration error" + " " + pComment + ".")
    elif pRetCode == retCONST :
        pHLine("ERROR NUMBER RESERVED" + " " + pComment + ".")
    elif pRetCode == retSYNT :
        pHLine("Job: " + JobName + " is not valid" + " " + pComment + ".")
    elif pRetCode == retERROR :
        pHLine("Job: " + JobName + " is ERROR" + " " + pComment + ".")
    elif pRetCode == retMOUNT :
        pHLine("Job: " + JobName + " MOUNT error" + " " + pComment + ".")
    else:
        pHLine("Unexpected exit code: " + str (pRetCode) + " " + pComment + ".")
    sys.exit(pRetCode)

SEFAPHORE_FOLDER="/mnt/semaphore"
Semaphore=SEFAPHORE_FOLDER+"/semaphore.txt"
SemaphoreJobs=SEFAPHORE_FOLDER+"/semaphoreJobs.txt"
SemaphoreConfig=SEFAPHORE_FOLDER+"/semaphore.cfg"
HISTORY_LOG=SEFAPHORE_FOLDER+"/semaphoreHistory.log"
numberOfArgs=len(sys.argv)

var = '''
Program controls flow of backups jobs. It finds semaphore in: ''' + SEFAPHORE_FOLDER + '''
folder.
parameter 1:
    start   wait for go, the process will pause till go is given,
            status in semaphore will be set to "running"
    stop    to indicate finish of the process, next job will be given option to
            run, the process will be timeouted anyway after timeoutPeriod has
            been reached, status of semaphore will be set to awaiting
parameter 2:
    unique job name

parameter 3:
            y - for /mnt/semaphore remote mount check
            n - for local /mnt/semaphore without mount

Returns:
0, retGO, when it gives OK for starting that should be confired with start command and ended with stop command
1, retWAIT, no go
2, retADMIN, control proceess has found a problem that requires admin intervention
3, retCONF
4, retCONST
5, retSYNT
6, retERROR
7, retMOUNT

Following parameters are passed: ''' + str(sys.argv) + '''
Please specify all arguments, for example: control.py <start|stop> <job name>

Following is a list of valid jobs, it is taken from''' + SemaphoreJobs + ''' file'''

Command=""
JobName=""
remoteMount=""

Jobs=readJobs(SemaphoreJobs)
Command, JobName, remoreMount = readParams(Jobs)
testMount()
config = ConfigParser.RawConfigParser()
config.read(SemaphoreConfig)
minutesWait = config.getint('Global', 'minuteswait')

retCode=retERROR
if Command == 'start':
    pHLine("Waiting for semaphore to be openned.")
    while retCode != retGO:
        currentJobLine = readSemaphore(Semaphore)
        if len(currentJobLine) == 0:
            currentJobLine = nextSemaphore(-1, Jobs, Semaphore, "awaiting")
        semaphoreJob, semapforeDateTime, jobStatus = parseSemaphore(currentJobLine)
        jobValid, CurrentIndex = validateGetJobDetails(semaphoreJob, Jobs)
        semaphoreTimeoutDateTime, From, To = calculateTimeout(semaphoreJob, semapforeDateTime, Jobs)
        if Timeouted(semaphoreTimeoutDateTime):
            currentJobLine = nextSemaphore(CurrentIndex, Jobs, Semaphore, "awaiting")
            semaphoreJob, semapforeDateTime, jobStatus = parseSemaphore(currentJobLine)
            semaphoreTimeoutDateTime, From, To = calculateTimeout(semaphoreJob, semapforeDateTime, Jobs)
        if semaphoreJob == JobName:
            if jobStatus == "running" or not goHour(time.strftime("%H"), From, To):
                retCode=retWAIT
            else:
                currentJobLine=setStatusSemaphore(currentJobLine, Semaphore, "running")
                semaphoreJob, semapforeDateTime, jobStatus = parseSemaphore(currentJobLine)
                semaphoreTimeoutDateTime, From, To = calculateTimeout(semaphoreJob, semapforeDateTime, Jobs)
                retCode=retGO
        else:
            retCode=retWAIT
        if retCode != retGO:
            seconds=60
            pLine("Sleeping " + str(minutesWait) + " minute(s) to run: " + str(JobName))
            time.sleep(minutesWait*seconds)
            Jobs=readJobs(SemaphoreJobs)

elif Command == 'stop':
    currentJobLine = readSemaphore(Semaphore)
    if len(currentJobLine) == 0 :
        currentJobLine = nextSemaphore(-1, Jobs, Semaphore,"awaiting")
    semaphoreJob, semapforeDateTime, jobStatus = parseSemaphore(currentJobLine)
    jobValid, CurrentIndex = validateGetJobDetails(semaphoreJob, Jobs)
    semaphoreTimeoutDateTime, From, To = calculateTimeout(semaphoreJob, semapforeDateTime, Jobs)
    if Timeouted(semaphoreTimeoutDateTime):
        currentJobLine = nextSemaphore(CurrentIndex, Jobs, Semaphore,"awaiting")
        semaphoreJob, semapforeDateTime,  jobStatus = parseSemaphore(currentJobLine)
        semaphoreTimeoutDateTime, From, To = calculateTimeout(semaphoreJob, semapforeDateTime, Jobs)
        retCode=retGO
    if semaphoreJob == JobName:
        currentJobLine=nextSemaphore(CurrentIndex, Jobs, Semaphore,"awaiting")
        semaphoreJob, semapforeDateTime, jobStatus = parseSemaphore(currentJobLine)
        semaphoreTimeoutDateTime, From, To = calculateTimeout(semaphoreJob, semapforeDateTime, Jobs)
        retCode=retGO
    else:
        retCode=retWAIT
else:
    retCode=retSYNT

pLine("Job: " + semaphoreJob + " has OK from: " + semapforeDateTime.strftime("%Y-%m-%d %H:%M:%S") + ", with timeout set to: " + semaphoreTimeoutDateTime.strftime("%Y-%m-%d %H:%M:%S"))

exitControl(retCode)
