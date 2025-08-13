# 常用库
# 学习os、sys和json模块

import os
import sys
import json

# os模块
print("当前工作目录:", os.getcwd())

# sys模块
print("Python版本:", sys.version)

# json模块
data = {"name": "Alice", "age": 25}
json_str = json.dumps(data)
print("JSON字符串:", json_str)

# 解析JSON
parsed_data = json.loads(json_str)
print("解析后的数据:", parsed_data)