# 工具类型枚举
from enum import Enum


class TypeEnum(Enum):
    STR_FORMAT = 'python_str_format'
    STR_COMPARE = 'python_str_compare'
    OCR = 'python_ocr'
    URL_REQUEST = 'python_curl'

    OPERATION_LOG = 'operationLog'

    POST = 1
    GET = 2
