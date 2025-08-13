# 读写文件
# 学习如何操作文件

# 写入文件
with open("example.txt", "w") as file:
    file.write("Hello, World!\n")
    file.write("This is a sample file.\n")

# 读取文件
with open("example.txt", "r") as file:
    content = file.read()
    print(content)