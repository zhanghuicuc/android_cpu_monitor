# android_cpu_monitor
calculate cpu usage percentage on each core of a process's threads

Android cpu占用率监视器，精细到每个线程、每个核

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

欢迎关注我的公众号灰度五十，分享各类音视频、移动开发知识，以及名企内推信息~

![在这里插入图片描述](https://img-blog.csdnimg.cn/20181222184847599.jpg)
