import json
import os
import sys

if __name__ == "__main__":
    # 引入自定义包路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    from pkg.tms import Tms
    from tools.file import File
    from tools.show import Show
    from data.tmsOrderParam import TmsOrderParam

    inbound = False  # 是否开启创建入库单
    outbound = True  # 是否开启创建出库单

    outboundList = []  # 已创建出库号列表
    inboundList = []  # 已创建入库单号列表

    config = File(path="\config\config.json").read_json_config()

    res = ""

    if inbound is True:
        res = Tms(url1=config["tmsUrl"]["createInboundTms"], url2=config["tmsUrl"]["createInboundWms"],
                  param=TmsOrderParam(index="inbound").getParam(),
                  dataList=inboundList, orderType="inbound").createOrder()  # 向proxy 发起创建人库单
        Show(text="创建入库单：", style="red").print()

    if outbound is True:
        res = Tms(url1=config["tmsUrl"]["createOutboundTms"], url2=config["tmsUrl"]["createOutboundWms"],
                  param=TmsOrderParam(index="outbound").getParam(),
                  dataList=outboundList, orderType="outbound").createOrder()  # 向proxy 发起创建出库单
        Show(text="创建出库单：", style="cyan").print()

    Show(text=json.loads(res), style="blue").print()
