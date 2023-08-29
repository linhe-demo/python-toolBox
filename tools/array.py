class Array:
    def __init__(self, target=None, step=None):
        self.target = target
        self.step = step

    # 将列表拆分成n个包含step个元素的列表的大列表
    def ArrayChunk(self):
        if len(self.target) == 0:
            return []

        return [self.target[i:i + self.step] for i in range(0, len(self.target), self.step)]
