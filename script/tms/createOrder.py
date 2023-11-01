import json

from data.tmsOrderParam import TmsOrderParam
from pkg.tms import Tms
from tools.file import File
from tools.show import Show

if __name__ == "__main__":

    outboundList = []
    config = File(path="\config\config.json").read_json_config()
    param = TmsOrderParam(index="outbound").getParam()
    res = Tms(url1=config["tmsUrl"]["createOutboundTms"], url2=config["tmsUrl"]["createOutboundWms"],
              param=param, dataList=outboundList).createOutboundOrder()  # 向proxy 发起创建出库单

    Show(text=json.loads(res), style="blue").print()
