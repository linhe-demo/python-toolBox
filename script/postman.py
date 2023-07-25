import os
import sys

if __name__ == "__main__":
    # 引入自定义包路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    from pkg.window import Window
    from common.typeEnum import TypeEnum
    from pkg.callBack import CallBack

    Window(title="接口请求工具", label1="请求地址：", label2="请求参数：", btn1="发送", btn2="重置",
           resultName="请求结果：", toolType=TypeEnum.URL_REQUEST.value, callback=CallBack().postman).initWindow()
