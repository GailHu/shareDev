# -*- coding: utf-8 -*-

import time


# 输出格式化时间Python3
# 格式："%Y%m%d%H%M%S"     20210922104556
# 格式：%Y-%m-%d %H:%M:%S  2021-09-22 10:45:56
def ymd_str(format_str: str = "%Y-%m-%d"):
    # 格式: 2021-09-22
    return time.strftime(format_str, time.localtime())


# 程序入口
if __name__ == '__main__':
    data = ymd_str()
    print(data)
