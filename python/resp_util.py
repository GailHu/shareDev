# -*- coding: utf-8 -*-

SUCCESS_STATUS = {
    "code": 200,
    "msg": "success",
    "data": {}
}

ERROR_STATUS = {
    "code": 500,
    "msg": "error",
    "data": {}
}

def create_response(status: dict, msg: str = None, data: dict | list = None, code: int = None):
    """
    通用响应生成方法
    :param status: 状态模板，通常是 SUCCESS_STATUS 或 ERROR_STATUS
    :param msg: 自定义消息，可选
    :param data: 自定义数据字段，可选
    :param code: 自定义状态码，可选，默认为模板中的 code
    :return: 格式化的响应字典
    """
    response = status.copy()  # 避免直接修改模板
    if code is not None:
        response["code"] = code
    if msg is not None:
        response["msg"] = msg
    if data is not None:
        response["data"] = data
    return response