import sys
from optparse import OptionParser
import random

def findQueue():
    q = hiQueue()
    while q > 0:
        if len(queue[q] > 0):
            return q
        q -= 1
    if len(queue[0] > 0):
        return 0
    return -1

def LowerQueue(currJob, currQueue, issuedIO):
    if currQueue > 0:
        job[currJob]['currPri'] = currQueue - 1
        if issuedIO == False:
            queue[currQueue - 1].append(currJob)
        job[currJob['ticksLeft']] = quantum[currQueue - 1]
        
def Abort(str):
    sys.stderr.write(str + '\n')
    exit(1)
    
parser = OptionParser()
parser.add_option('-s', '--seed', help='the random seed', 
                  default=0, action='store', type='int', dest='seed')
parser.add_option('-n', '--numQueues',
                  help='number of queues in MLFQ (if not using -Q)', 
                  default=3, action='store', type='int', dest='numQueues')
parser.add_option('-q', '--quantum', help='length of time slice (if not using -Q)',
                  default=10, action='store', type='int', dest='quantum')
parser.add_option('-Q', '--quantumList',
                  help='length of time slice per queue level, specified as ' + \
                  'x,y,z,... where x is the quantum length for the highest ' + \
                  'priority queue, y the next highest, and so forth', 
                  default='', action='store', type='string', dest='quantumList')
parser.add_option('-j', '--numJobs', default=3, help='number of jobs in the system',
                  action='store', type='int', dest='numJobs')
parser.add_option('-m', '--maxlen', default=100, help='max run-time of a job ' +
                  '(if randomly generating)', action='store', type='int',
                  dest='maxlen')
parser.add_option('-M', '--maxio', default=10,
                  help='max I/O frequency of a job (if randomly generating)',
                  action='store', type='int', dest='maxio')
parser.add_option('-B', '--boost', default=0,
                  help='how often to boost the priority of all jobs back to ' +
                  'high priority', action='store', type='int', dest='boost')
parser.add_option('-i', '--iotime', default=5,
                  help='how long an I/O should last (fixed constant)',
                  action='store', type='int', dest='ioTime')
parser.add_option('-S', '--stay', default=False,
                  help='reset and stay at same priority level when issuing I/O',
                  action='store_true', dest='stay')
parser.add_option('-I', '--iobump', default=False,
                  help='if specified, jobs that finished I/O move immediately ' + \
                  'to front of current queue',
                  action='store_true', dest='iobump')
parser.add_option('-l', '--jlist', default='',
                  help='a comma-separated list of jobs to run, in the form ' + \
                  'x1,y1,z1:x2,y2,z2:... where x is start time, y is run ' + \
                  'time, and z is how often the job issues an I/O request',
                  action='store', type='string', dest='jlist')
parser.add_option('-c', help='compute answers for me', action='store_true',
                  default=False, dest='solve')

(options, args) = parser.parse_args()

random.seed(options.seed)

numQueues = options.numQueues

quantum = {}
if options.quantumList != '':
    quantumLengths = options.quantumList.split(',')
    numQueues = len(quantumLengths)
    qc = numQueues - 1
    for i in range(numQueues):
        quantum[qc] = int(quantumLengths[i])
        qc -= 1
else:
    for i in range(numQueues):
        quantum[i] = int(options.quantum)
        
hiQueue = numQueues - 1
ioTime = int(options.ioTime)
ioDone = {}
job = {}
random.seed(options.seed)

jobCnt = 0
if options.jlist != '':
    allJobs = options.jlist.split(':')
    for j in allJobs:
        jobInfo = j.split(',')
        if len(jobInfo) != 3:
            sys.stderr.write('Badly formatted job string. Should be x1,y1,z1:x2,y2,z2:...\n')
            sys.stderr.write('where x is the startTime, y is the runTime, and z is the I/O frequency.\n')
            exit(1)
        assert(len(jobInfo) == 3)
        startTime = int(jobInfo[0])
        runTime = int(jobInfo[1])
        ioFreq = int(jobInfo[2])
        job[jobCnt] = {'currPri':hiQueue, 'ticksLeft':quantum[hiQueue], 'startTime':startTime,
                       'runTime':runTime, 'timeLeft':runTime, 'ioFreq':ioFreq, 'doingIO':False,
                       'firstRun':-1}
        if startTime not in ioDone:
            ioDone[startTime] = []
        ioDone[startTime].append((jobCnt, 'JOB BEGINS'))
        jobCnt += 1
else:
    for j in range(options.numJobs):
        startTime = 0
        runTime = int(random.random() * (options.maxlen - 1) + 1)
        ioFreq = int(random.random() * (options.maxio - 1) + 1)  
        job[jobCnt] = {'currPri':hiQueue, 'ticksLeft':quantum[hiQueue], 'startTime':startTime,
                       'runTime':runTime, 'timeLeft':runTime, 'ioFreq':ioFreq, 'doingIO':False,
                       'firstRun':-1}
        if startTime not in ioDone:
            ioDone[startTime] = []
        ioDone[startTime].append((jobCnt, 'JOB BEGINS'))
        jobCnt += 1
        
numJobs = len(job)

print('Here is the list of inputs:')
print('OPTIONS jobs', numJobs)
print('OPTIONS queues', numQueues)
for i in range(len(quantum)-1,-1,-1):
    print('OPTIONS quantum length for queue %2d is %3d' % (i, quantum[i]))
print('OPTIONS boost', options.boost)
print('OPTIONS ioTime', options.ioTime)
print('OPTIONS stayAfterIO', options.stay)
print('OPTIONS iobump', options.iobump)

print('\n')
print('For each job, three defining characteristics are given:')
print('  startTime : at what time does the job enter the system')
print('  runTime   : the total CPU time needed by the job to finish')
print('  ioFreq    : every ioFreq time units, the job issues an I/O')
print('              (the I/O takes ioTime units to complete)\n')

print('Job List:')
for i in range(numJobs):
    print('  Job %2d: startTime %3d - runTime %3d - ioFreq %3d' % (i, job[i]['startTime'],
                                                                   job[i]['runTime'], job[i]['ioFreq']))
print('')

if options.solve == False:
    print('Compute the execution trace for the given workloads.')
    print('If you would like, also compute the response and turnaround')
    print('times for each of the jobs.')
    print('')
    print('Use the -c flag to get the exact results when you are finished.\n')
    exit(0)
    
queue = {}
for q in range(numQueues):
    queue[q] = []
    
currTime = 0
totalJobs = len(job)
finishedJobs = 0
print('\nExecution Trace:\n')

while finishedJobs < totalJobs:
    #Priority boost
    if options.boost > 0 and currTime != 0:
        print('[ time %d ] BOOST ( every %d )' % (currTime, options.boost))
        if currTime % options.boost == 0:
            for q in range(numQueues-1):
                for j in queue[q]:
                    if job[j]['doingIO'] == False:
                        queue[hiQueue].append(j)
                queue[q] = []
                for j in range(numJobs):
                    if job[j]['timeLeft'] > 0:
                        job[j]['currPri']   = hiQueue
                        job[j]['ticksLeft'] = quantum[hiQueue]
        
        # Check for any I/Os done
        if currTime in ioDone:
            for (j, type) in ioDone[currTime]:
                q = job[j]['currPri']
                job[j]['doingIO'] = False
                print('[ time %d ] %s by JOB %d' % (currTime, type, j))
                if options.iobump == False or type == 'JOB BEGINS':
                    queue[q].append(j)
                else:
                    queue[q].insert(0, j)
                
        currQueue = FindQueue()
        if currQueue == -1:
            print('[ time %d ] IDLE' % (currTime))
            currTime += 1
            continue
        
        currJob = queue[currQueue][0]
        if job[currJob]['currPri'] != currQueue:
            Abort('currPri[%d] does not match currQueue[%d]' % (job[currJob]['currPri'], currQueue))

        job[currJob]['timeLeft']  -= 1
        job[currJob]['ticksLeft'] -= 1

        if job[currJob]['firstRun'] == -1:
            job[currJob]['firstRun'] = currTime

        runTime   = job[currJob]['runTime']
        ioFreq    = job[currJob]['ioFreq']
        ticksLeft = job[currJob]['ticksLeft']
        timeLeft  = job[currJob]['timeLeft']

        print('[ time %d ] Run JOB %d at PRIORITY %d [ TICKSLEFT %d RUNTIME %d TIMELEFT %d ]' % \
            (currTime, currJob, currQueue, ticksLeft, runTime, timeLeft))

        if timeLeft < 0:
            Abort('Error: should never have less than 0 time left to run')
            
        currTime += 1
        if timeLeft == 0:
            print('[ time %d ] FINISHED JOB %d' % (currTime, currJob))
            finishedJobs += 1
            job[currJob]['endTime'] = currTime
            done = queue[currQueue].pop(0)
            assert(done == currJob)
            continue
        
        # Check for I/O
        issuedIO = False
        if ioFreq > 0 and (((runTime - timeLeft) % ioFreq) == 0):
            # time for an IO!
            print('[ time %d ] IO_START by JOB %d' % (currTime, currJob))
            issuedIO = True
            desched = queue[currQueue].pop(0)
            assert(desched == currJob)
            job[currJob]['doingIO'] = True
            # this does the bad rule -- reset your tick counter if you stay at the same level
            if options.stay == True:
                job[currJob]['ticksLeft'] = quantum[currQueue]
            # add to IO Queue: but which queue?
            futureTime = currTime + ioTime
            if futureTime not in ioDone:
                ioDone[futureTime] = []
            print('IO DONE')
            ioDone[futureTime].append((currJob, 'IO_DONE'))
            
        if ticksLeft == 0:
            if issuedIO == False:
                desched = queue[currQueue].pop(0)
            assert(desched == currJob)
            LowerQueue(currJob, currQueue, issuedIO)
            
print('')
print('Final statistics:')
responseSum   = 0
turnaroundSum = 0
for i in range(numJobs):
    response = job[i]['firstRun'] - job[i]['startTime']
    turnaround = job[i]['endTime'] - job[i]['startTime']
    print('  Job %2d: startTime %3d - response %3d - turnaround %3d' % (i, job[i]['startTime'],
                                                                        response, turnaround))
    responseSum += response
    turnaroundSum += turnaround

print('\n  Avg %2d: startTime n/a - response %.2f - turnaround %.2f' % (i, 
                                                                        float(responseSum)/numJobs,
                                                                        float(turnaroundSum)/numJobs))

print('\n')
