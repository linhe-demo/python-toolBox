# 文件读取类
import json
import os
import pandas as pd


class File:
    def __init__(self, path=None, row=None, fileData=None, sheetName=None, sheetTitle=None, txtData=None):
        self.path = path
        self.fileData = fileData
        self.sheetName = sheetName
        self.sheetTitle = sheetTitle
        self.row = row
        self.txtData = txtData

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

    def writeTxt(self):
        if not os.path.exists(self.path):
            open(self.path, 'w', encoding='utf-8').close()

        with open(self.path, 'w', encoding='utf-8') as f:
            for i in self.txtData:
                f.write(i + "\n")

    def writeTxtInline(self):
        if not os.path.exists(self.path):
            open(self.path, 'w', encoding='utf-8').close()

        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(self.txtData + "\n")

    def readRow(self):
        feature = []
        lists = []
        data = self.read_excl()  # 文件位置
        if self.row == 1:
            feature = data[:, 0:1]  # 取第一列
        elif self.row == 2:
            feature = data[:, 1:2]  # 取第二列

        m = 0
        for i in feature:
            tmpKey = str(feature[m][0])
            lists.append(tmpKey)
            m += 1
        return lists

    def writeExcel(self):
        # 检查文件夹是否存在，不存在直接创建
        path = "/".join(self.path.split("/")[:-1])
        if not os.path.exists(path):
            os.makedirs(path)
        writer = pd.ExcelWriter(path=self.path)
        for num in self.fileData:
            if len(self.fileData[num]) == 0:
                continue
            data = pd.DataFrame(self.fileData[num])
            data = data[self.sheetTitle[num]]
            data.to_excel(writer, self.sheetName[num], index=False, header=True)

        if hasattr(writer, 'save'):
            writer.save()
        elif hasattr(writer, '_save'):
            writer._save()

        writer.close()
