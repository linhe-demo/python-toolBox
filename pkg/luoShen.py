import calendar
import datetime
import json
import math
import time

from common.warehouseEnum import WarehouseEnum
from model.erp import ErpDatatable
from model.panGu import PanGuTable
from model.website import websiteTable
from pkg.db import Db
from pkg.highcharts import Highcharts
from tools import curl
from tools.array import Array
from tools.curl import Curl
from tools.file import File
from tools.log import Log
from tools.threadingTool import MyThreading


class LuoShen:
    def __init__(self, filePath=None, warehouse=None, orderSn=None, date=None, param=None):
        self.param = param
        self.filePath = filePath
        self.orderSn = orderSn
        self.warehouse = warehouse
        self.type = WarehouseEnum
        self.date = date
        self.res = {}
        self.excelData = []
        self.skuData = {}
        self.noSaleList = {}


    def getCategoryAttr(self):

        excelList = data = File(path=self.filePath).read_excl()

        for i in excelList:
            catId = i.get("品类ID")

        # sql = websiteTable(index="getCategoryAttribute").getSql()
        # data = Db(sql=sql, param="','".join(self.param), db="websitePron").getAll()
        #
        # newList = Array(target=data, step=100).ArrayChunk()
        #
        # MyThreading(num=20, data=newList, func=self.getFixPlusImgData).semaphoreJob()
        #
        # print(self.resData)
