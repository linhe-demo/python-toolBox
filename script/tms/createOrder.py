import json

from data.tmsOrderParam import TmsOrderParam
from pkg.tms import Tms
from tools.file import File

if __name__ == "__main__":
    config = File(path="\config\config.json").read_json_config()
    param = TmsOrderParam(index="outbound").getParam()
    res = Tms(url1=config["tmsUrl"]["createOutboundTms"], url2=config["tmsUrl"]["createOutboundWms"],
              param=param).createOutboundOrder()  # 向proxy 发起创建出库单
    print(json.loads(res))
