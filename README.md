# android_cpu_monitor
calculate cpu usage percentage on each core of a process's threads

# Author:
zhang hui <zhanghui9@le.com;zhanghuicuc@gmail.com>
LeEco BSP Multimedia / Communication University of China

Basic Design Idea is as follows:
```
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
```

run CpuWatcher.py -h for helps