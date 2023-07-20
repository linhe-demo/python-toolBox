# 文件读取类
import json
import os
import pandas as pd


class File:
    def __init__(self, path=None):
        self.path = path

    def read_json_config(self):
        with open(os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + self.path, 'r') as json_file:
            return json.load(json_file)

    def read_excl(self):
        raw_data = pd.read_excel(self.path, header=0)  # header=0表示第一行是表头，就自动去除了
        return raw_data.values

    def read_txt(self):
        data = []
        with open(self.path, 'r', encoding='utf-8') as f:
            for line in f:
                data_line = line.strip("\n").split("\r")  # 去除首尾换行符，并按换行划分
                data.append(data_line)
        return data

    def readRow(self, row):
        feature = []
        lists = []
        data = self.read_excl()  # 文件位置
        if row == 1:
            feature = data[:, 0:1]  # 取第一列
        elif row == 2:
            feature = data[:, 1:2]  # 取第二列

        m = 0
        for i in feature:
            tmpKey = str(feature[m][0])
            lists.append(tmpKey)
            m += 1
        return lists
