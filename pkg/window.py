# python gui 窗口类
import tkinter as tk
import re
from tkinter import *
from tkinter import filedialog

from PIL import ImageTk, Image

STR_FORMAT = 'str_format'
STR_COMPARE = 'str_compare'
OCR = 'ocr'


class Window:
    def __init__(self, title=None, width=900, height=770, label1=None, label2=None, radio=None, btn1=None, btn2=None,
                 resultName=None, toolType=None, callback=None):
        self.title = title + "-linHeToolBox"
        self.width = width
        self.height = height
        self.label1 = label1
        self.label2 = label2
        self.radio = radio
        self.btn1 = btn1
        self.btn2 = btn2
        self.resultName = resultName
        self.callBack = callback
        self.toolType = toolType
        self.root = tk.Tk()
        self.filePath = None

    def initWindow(self):
        self.root.geometry(str(self.width) + "x" + str(self.height))
        self.root.title(self.title)
        self.root.resizable(False, False)  # 横纵均不允许调整

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - self.width) / 2
        y = (sh - self.height) / 2
        self.root.geometry("%dx%d+%d+%d" % (self.width, self.height, x, y))

        if self.toolType == STR_FORMAT:
            self.createStrFormat()
        elif self.toolType == STR_COMPARE:
            self.createStrCompare()
        elif self.toolType == OCR:
            self.createOcr()

        tk.mainloop()

    def createStrFormat(self):
        label1 = tk.Label(self.root, text=self.label1, fg="#67c23a")
        label1.grid(row=0, column=1, sticky=tk.W, padx=8)

        inputText = tk.Text(self.root, width=125, height=13, bg='#F8F8F8', fg='black', font=('宋体', 10), spacing1=2,
                            spacing2=2,
                            spacing3=2)
        inputText.grid(row=1, column=1, columnspan=10, sticky=tk.W, padx=10, pady=4)
        index = IntVar(value=1)  # index，并预先选中value为1的单选按钮
        if self.radio is True:
            ra1 = Radiobutton(self.root, text='数字', variable=index, value=1, fg="#cd2828")
            ra1.grid(row=3, column=1, columnspan=10, sticky=tk.W, padx=100, pady=4)
            ra2 = Radiobutton(self.root, text='字符串', variable=index, value=2, fg="#67c23a")
            ra2.grid(row=3, column=1, columnspan=10, sticky=tk.W, padx=160, pady=4)
            ra3 = Radiobutton(self.root, text='json', variable=index, value=3, fg="#409eff")
            ra3.grid(row=3, column=1, columnspan=10, sticky=tk.W, padx=230, pady=4)

        tk.Button(self.root, text=self.btn1, width=10,
                  command=lambda: self.showStrFormatRes(inputText=inputText, callBack=self.callBack, result=result,
                                                        radio=self.radio, index=index),
                  bg='#409eff',
                  fg='white').grid(
            row=3,
            column=10,
            sticky=tk.E,
            padx=95,
            pady=5)
        tk.Button(self.root, text=self.btn2, width=10, command=lambda: self.reset(input1=inputText, result1=result),
                  bg='#67c23a',
                  fg='white').grid(row=3, column=10,
                                   sticky=tk.E,
                                   padx=10,
                                   pady=5)
        # 创建结果文本
        label3 = tk.Label(self.root, text=self.resultName, fg='#409eff')
        label3.grid(row=3, column=1, sticky=tk.W, padx=8, pady=10)

        result = tk.Text(self.root, width=125, height=27, bg='#fff', fg='black', font=('宋体', 10), spacing1=2,
                         spacing2=2,
                         spacing3=2)
        result.grid(row=4, column=1, columnspan=10, sticky=tk.W, padx=10)

    def createStrCompare(self):
        label1 = tk.Label(self.root, text=self.label1, fg="#67c23a")
        label1.grid(row=0, column=1, sticky=tk.W, padx=8)

        inputText1 = tk.Text(self.root, width=125, height=5, bg='#F8F8F8', fg='black', font=('宋体', 10), spacing1=2,
                             spacing2=2,
                             spacing3=2)
        inputText1.grid(row=1, column=1, columnspan=10, sticky=tk.W, padx=10, pady=4)

        label2 = tk.Label(self.root, text=self.label2, fg="#67c23a")
        label2.grid(row=2, column=1, sticky=tk.W, padx=8)

        inputText2 = tk.Text(self.root, width=125, height=5, bg='#F8F8F8', fg='black', font=('宋体', 10), spacing1=2,
                             spacing2=2,
                             spacing3=2)
        inputText2.grid(row=3, column=1, columnspan=10, sticky=tk.W, padx=10, pady=4)

        tk.Button(self.root, text=self.btn1, width=10,
                  command=lambda: self.showStrCompareRes(inputText1=inputText1, inputText2=inputText2,
                                                         callBack=self.callBack, res1=result1, res2=result2),
                  bg='#409eff',
                  fg='white').grid(
            row=4,
            column=10,
            sticky=tk.E,
            padx=95,
            pady=5)
        tk.Button(self.root, text=self.btn2, width=10,
                  command=lambda: self.reset(input1=inputText1, input2=inputText2, result1=result1, result2=result2),
                  bg='#67c23a',
                  fg='white').grid(row=4, column=10,
                                   sticky=tk.E,
                                   padx=10,
                                   pady=5)
        # 创建结果文本
        label3 = tk.Label(self.root, text=self.resultName, fg='#409eff')
        label3.grid(row=4, column=1, sticky=tk.W, padx=8, pady=10)
        result1 = tk.Text(self.root, width=63, height=28, bg='#fff', fg='black', font=('宋体', 10), spacing1=2,
                          spacing2=2,
                          spacing3=2)
        result1.grid(row=5, column=0, columnspan=10, sticky=tk.W, padx=10)
        result2 = tk.Text(self.root, width=63, height=28, bg='#fff', fg='black', font=('宋体', 10), spacing1=2,
                          spacing2=2,
                          spacing3=2)
        result2.grid(row=5, column=3, columnspan=10, sticky=tk.E, padx=10)

    def createOcr(self):
        label1 = tk.Label(self.root, text=self.label1, fg="#67c23a")
        label1.grid(row=0, column=1, sticky=tk.W, padx=8)

        label = tk.Label(self.root, text="", fg="#3872e0")
        label.grid(row=1, column=3)
        tk.Button(self.root, text="选择图片", width=8,
                  command=lambda: self.selectImage(label=label),
                  bg='#3872e0',
                  fg='white').grid(
            row=1,
            column=2,
            sticky=tk.E,
            padx=95,
            pady=5)

        tk.Button(self.root, text=self.btn1, width=10,
                  command=lambda: self.showOcrRes(callBack=self.callBack, res=result, label=label),
                  bg='#409eff',
                  fg='white').grid(
            row=2,
            column=10,
            sticky=tk.E,
            padx=95,
            pady=5)
        tk.Button(self.root, text=self.btn2, width=10, command=lambda: self.reset(result1=result, label=label),
                  bg='#67c23a',
                  fg='white').grid(row=2, column=10,
                                   sticky=tk.E,
                                   padx=10,
                                   pady=5)
        # 创建结果文本
        label3 = tk.Label(self.root, text=self.resultName, fg='#409eff')
        label3.grid(row=2, column=1, sticky=tk.W, padx=8, pady=10)

        result = tk.Text(self.root, width=125, height=27, bg='#fff', fg='black', font=('宋体', 10), spacing1=2,
                         spacing2=2,
                         spacing3=2)
        result.grid(row=3, column=1, columnspan=10, sticky=tk.W, padx=10)

    def selectImage(self, label=None):
        # 打开文件选择对话框
        self.filePath = filedialog.askopenfilename()
        label.config(text="图片已成功上传！")

    def showOcrRes(self, callBack=None, res=None, label=None):
        if self.filePath is None:
            res.delete(1.0, END)
            res.insert(INSERT, "请上传需要提取文字的图片")
            return
        info = callBack(self.filePath)
        res.insert(INSERT, info)
        label.config(text="")
        self.filePath = None

    @staticmethod
    def showStrCompareRes(inputText1=None, inputText2=None, callBack=None, res1=None, res2=None):
        textA = inputText1.get(1.0, END)
        textB = inputText2.get(1.0, END)

        str1, str2 = callBack(textA.strip(), textB.strip())
        res1.insert(INSERT, str1)
        res2.insert(INSERT, str2)

    def showStrFormatRes(self, inputText=None, callBack=None, result=None, radio=None, index=None):
        text = inputText.get(1.0, END)
        if radio is True:
            if index.get() == 3:
                res = callBack(text.strip(), index.get())  # 回调函数
            else:
                res = callBack(text.strip().splitlines(), index.get())  # 回调函数
        else:
            res = callBack(text.strip().splitlines())  # 回调函数

        result.delete(1.0, END)
        # # Add formatted data to Text widget
        result.insert(tk.END, res)

        # Add color tags
        result.tag_config("key", foreground="#cd2828")
        result.tag_config("value", foreground="#1d57d9")

        # Traverse formatted data and add color tags to keys and values
        self.formatJson(res, result, "1.0")

    def reset(self, input1=None, input2=None, result1=None, result2=None, label=None):
        if input1 is not None:
            input1.delete(1.0, END)
        if input2 is not None:
            input2.delete(1.0, END)
        if result1 is not None:
            result1.delete(1.0, END)
        if result2 is not None:
            result2.delete(1.0, END)
        if label is not None:
            label.config(text="")
        self.filePath = None

    def formatJson(self, formatted_data1, text1, idx):
        for match in re.finditer(
                r'("([^"]+)":\s*)(("[^"]*")|([0-9]\d*.\d*|0.\d*[0-9]\d*)|(true)|(false)|(\bnull\b)|({[\s\S]*?})|\[[\s\S]*?]),?',
                formatted_data1):
            full_match = match.group(0)
            key = match.group(2)
            value = match.group(3)
            start = text1.search(full_match, idx, tk.END)
            key_start = f"{start}+{full_match.index(key) - 1}c"
            key_end = f"{key_start}+{len(key) + 2}c"
            text1.tag_add("key", key_start, key_end)
            value_start = f"{key_end}+1c"
            value_end = f"{value_start}+{len(value) + 1}c"

            if value.startswith('{') and value.endswith('}'):
                self.formatJson(value, text1, key_end)
            elif value.startswith('[') and value.endswith(']'):
                self.ListFormat(value, text1)
            else:
                text1.tag_add("value", value_start, value_end)

    def ListFormat(self, formatted_data, text):
        for match in re.finditer(
                r'"([^"]+)"\s*:\s*(("[^"]*")|([0-9]\d*.\d*|0.\d*[0-9]\d*)|(true)|(false)|(\bnull\b)|("\[")|({[\s\S]*?}))(?=,|\n|})',
                formatted_data):
            # full = match.group(0)
            key = match.group(1)
            value = match.group(2)

            self.addTags(key, "key", text)
            self.addTags(value, "value", text)

    @staticmethod
    def addTags(regex, tag, text):
        idx = "1.0"
        while True:
            match_start = text.search(regex, idx, tk.END, regexp=True)
            if not match_start:
                break
            if tag == 'key':
                match_end = f"{match_start}+{len(regex) + 1}c"
            else:
                match_end = f"{match_start}+{len(regex)}c"
            text.tag_add(tag, match_start, match_end)
            idx = match_end
