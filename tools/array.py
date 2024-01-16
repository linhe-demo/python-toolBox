class Array:
    def __init__(self, target=None, step=None, data=None):
        self.target = target
        self.step = step
        self.data = data

    # 将列表拆分成n个包含step个元素的列表的大列表
    def ArrayChunk(self):
        if len(self.target) == 0:
            return []

        return [self.target[i:i + self.step] for i in range(0, len(self.target), self.step)]

    def InArray(self):
        for i in self.data:
            if self.target == i:
                return True

        return False

    def ArrayUniq(self):
        if len(self.data) == 0:
            return []
        tmp = {}
        backInfo = []
        for i in self.data:
            if tmp.get(i) is not None:
                continue
            else:
                backInfo.append(i)
                tmp[i] = i
        return backInfo

    def ArrayFilter(self):
        if len(self.data) == 0:
            return []

        backInfo = []
        for i in self.data:
            if len(i) == 0:
                continue
            else:
                backInfo.append(i)

        return backInfo
