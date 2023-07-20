# 错误类型枚举
from enum import Enum


class ErrorEnum(Enum):
    NOT_EMPTY = {"code": 400, "message": "Format data cannot be empty"}
    PARAM_ERROR = {"code": 500, "message": "Please enter correct json data"}
