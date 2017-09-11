#!/usr/bin/python
#coding:utf-8


###
# This script can calculate cpu usage percentage on each core of a process's threads
# Author:
# zhang hui <zhanghui9@le.com;zhanghuicuc@gmail.com>
# LeEco BSP Multimedia / Communication University of China

###Basic Design Idea is as follows:
'''
input pid
list threads by ls /proc/pid/task
struct thread_info{
	thread.name
	thread.priority
	thread.cpudata
}
struct thread.cpudata{
	core0_percentage[]
	core1_percentage[]
	core2_percentage[]
	core3_percentage[]
}
for i in threads{
	calculate_core_percentage(){
		running core has data, other core's data is 0
	}
}
for i in threads{
	write plot data
}
'''


import os
import sys
import subprocess
import time
import commands
from optparse import OptionParser
from time import sleep
from subprocess import check_output, CalledProcessError

global Options
global Pid
global Interval

Threads = []

class Cpudata:
    def __init__(self):
        self.percents = []
        self.core0_percent = []
        self.core1_percent = []
        self.core2_percent = []
        self.core3_percent = []
        self.percents.append(self.core0_percent)
        self.percents.append(self.core1_percent)
        self.percents.append(self.core2_percent)
        self.percents.append(self.core3_percent)
        self.proc_utime_old = -1
        self.proc_stime_old = -1
        self.proc_utime_new = -1
        self.proc_stime_new = -1
        self.proc_time_delta = 0
        self.cpu_times_old = []
        self.cpu_times_new = []

    def addData(self, coreID, percent):
        self.percents[coreID].append(percent)

    def getData(self, coreID):
        return self.percents[coreID]

    def getProcUtimeOld(self):
        return self.proc_utime_old

    def getProcStimeOld(self):
        return self.proc_stime_old

    def getProcUtimeNew(self):
        return self.proc_utime_new

    def getProcStimeNew(self):
        return self.proc_stime_new

    def getCpuTimesOld(self):
        return self.cpu_times_old

    def getCpuTimesNew(self):
        return self.cpu_times_new

    def getProcTimeDelta(self):
        return self.proc_time_delta

    def getPercents(self):
        return self.percents

    def setProcUtimeOld(self, utime):
        self.proc_utime_old = utime

    def setProcStimeOld(self, stime):
        self.proc_stime_old = stime

    def setProcUtimeNew(self, utime):
        self.proc_utime_new = utime

    def setProcStimeNew(self, stime):
        self.proc_stime_new = stime

    def setCpuTimesOld(self, cputimes):
        self.cpu_times_old = cputimes

    def setCpuTimesNew(self, cputimes):
        self.cpu_times_new = cputimes

    def calProcTimeDelta(self):
        new = (int)(self.proc_utime_new) + (int)(self.proc_stime_new)
        old = (int)(self.proc_utime_old) + (int)(self.proc_stime_old)
        self.proc_time_delta = new - old

    def calPercentage(self, which_cpu):
        cpu_time_delta = self.cpu_times_new[which_cpu] - self.cpu_times_old[which_cpu]
        if cpu_time_delta == 0:
            percentage = 0
        else:
            percentage = self.proc_time_delta * 100 / cpu_time_delta
        for i in range(0,4):
            if i == which_cpu:
                self.percents[i].append(percentage)
            else:
                self.percents[i].append(0)

class Thread:
    def __init__(self, tid):
        self.tid = tid
        self.name = ''
        self.priority = 0
        self.cpudata = Cpudata()

    def getName(self):
        return self.name

    def getTid(self):
        return (int)(self.tid)

    def getPrio(self):
        return self.priority

    def getCpudata(self):
        return self.cpudata

    def setName(self, name):
        self.name = name

def run_command(options, cmd):
    if options.debug:
        print 'COMMAND: ', cmd
    try:
        out_bytes = subprocess.check_output(cmd, shell=True)
        out_text = out_bytes.decode('utf-8')
        return out_text
    except CalledProcessError, e:
        message = "binary tool failed with error %d" % e.returncode
        if options.verbose:
            message += " - " + str(cmd)
        raise Exception(message)

def list_threads(options, pid):
    cmd = 'adb shell ls /proc/' + pid + '/task'
    result = run_command(options, cmd)
    result = result.rstrip()
    tids = result.split('\n')
    for i in range(len(tids)):
        thread = Thread((int)(tids[i]))
        Threads.append(thread)

def cal_percent(options, pid, thread, cputimes):
    cmd = 'adb shell cat /proc/%d/task/%d/stat' % ((int)(pid), thread.getTid())
    #something like:
    #18368 (Loader:HlsSampl) S 1761 1760 0 0 -1 1077936192 5301 5158 0 0 936 475 4 0 39 19 44 0 1562463 1030127616 23832 18446744073709551615 2871582720 2871600504 4292793808 3748864648 4141267120 0 4612 0 38136 18446743798832713004 0 0 -1 1 0 0 0 0 0 2871606488 2871607296 2875428864 4292795327 4292795414 4292795414 4292796382 0
    result = run_command(options, cmd)
    datas = result.split(' ')
    thread.setName(datas[1])
    which_cpu = (int)(datas[38])
    if thread.getCpudata().getProcUtimeOld() == -1 or thread.getCpudata().getProcStimeOld() == -1:
        thread.getCpudata().setProcUtimeOld((int)(datas[13]))
        thread.getCpudata().setProcStimeOld((int)(datas[14]))
        thread.getCpudata().setCpuTimesOld(cputimes)
    else:
        thread.getCpudata().setProcUtimeNew((int)(datas[13]))
        thread.getCpudata().setProcStimeNew((int)(datas[14]))
        thread.getCpudata().calProcTimeDelta()
        thread.getCpudata().setCpuTimesNew(cputimes)
        thread.getCpudata().calPercentage(which_cpu)
        thread.getCpudata().setProcUtimeOld(thread.getCpudata().getProcUtimeNew())
        thread.getCpudata().setProcStimeOld(thread.getCpudata().getProcStimeNew())
        thread.getCpudata().setCpuTimesOld(thread.getCpudata().getCpuTimesNew())

def get_cputime(options):
    cmd = 'adb shell cat /proc/stat'
    #something like:
    #cpu1 9167 717 5062 11946 132 0 12 0 0 0
    result = run_command(options, cmd)#subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout
    cpu_raw_datas = result.split('\n')
    cpu_times = []
    for i in range (1,5):
        cpu_info = cpu_raw_datas[i].split(' ')
        cpu_one_core_total_time = 0
        for j in range (1,8):
            cpu_one_core_total_time += (int)(cpu_info[j])
        cpu_times.append(cpu_one_core_total_time)
    return cpu_times

def draw_plot(options):
    for i in range(len(Threads)):
        print 'ThreadName: ', Threads[i].getName()
        print 'Cpu#0: ',
        print Threads[i].getCpudata().getPercents()[0]
        print 'Cpu#1: ',
        print Threads[i].getCpudata().getPercents()[1]
        print 'Cpu#2: ',
        print Threads[i].getCpudata().getPercents()[2]
        print 'Cpu#3: ',
        print Threads[i].getCpudata().getPercents()[3]

if __name__=='__main__':
    parser = OptionParser(usage="%prog -d -p pid -t interval")
    parser.add_option('-d', '--debug', dest="debug", action='store_true', default=False,
                          help="Print out debugging information")
    parser.add_option('-p', '--pid', dest="process_id",
                          help="Process id")
    parser.add_option('-t', '--interval', dest="time_interval",
                          help="Time interval for data collecting, in seconds ex.(0.1 means 100ms)")
    (options, args) = parser.parse_args()
    if options.process_id:
        Pid = options.process_id
    if options.time_interval:
        Interval = (float)(options.time_interval)

    list_threads(options, Pid)
    print 'start collecting data...'
    while True:
        try:
            CpuTimes = get_cputime(options)
            for i in range(len(Threads)):
                cal_percent(options, Pid, Threads[i], CpuTimes)
            sleep(Interval)
        except KeyboardInterrupt:
            print 'stop collecting data...'
            print 'start generating report...'
            draw_plot(options)
            print 'report exported'
            sys.exit("Finished")