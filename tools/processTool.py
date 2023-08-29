# python3 进程类
import os
import time
from multiprocessing import Process


class MyProcess:
    def __init__(self, func=None, num=4):
        self.func = func
        self.num = num

    def init(self):
        total = []
        print("该机器是 {} 核 CPU".format(os.cpu_count()))
        startTime = time.time()
        for i in range(self.num):
            p = Process(target=self.func)  # 多进程初始化
            total.append(p)
            p.start()

        for m in total:
            m.join()
        endTime = time.time()
        print("本次多进程 耗时：{}".format(endTime - startTime))
