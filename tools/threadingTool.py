# python3 线程类
import os
import threading
import time

from threading import Thread


class MyThreading:
    def __init__(self, num=4, func=None, data=None):
        self.num = num
        self.func = func
        self.data = data
        self.semaphore = threading.BoundedSemaphore(self.num)

    def init(self):
        total = []
        print("该机器是 {} 核 CPU".format(os.cpu_count()))
        start = time.time()
        for i in range(self.num):
            p = Thread(target=self.func)  # 多进程
            total.append(p)
            p.start()
        for p in total:
            p.join()
        stop = time.time()
        print("本次多线程 耗时：{}".format(start - stop))

    # （信号量限流）
    def semaphoreJob(self):
        thread_list = []
        k = 0
        for i in self.data:  # 创建工作线程
            t = threading.Thread(target=self.func, args=(
                i, "{}---{}".format(k, k+len(i)), self.semaphore))
            thread_list.append(t)
            k = k + len(i)

        for thread in thread_list:  # 启动线程
            thread.start()

        for thread in thread_list:  # 等待所有线程结束
            thread.join()
