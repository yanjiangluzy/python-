import json

sep = ":;"


# e.g: 5:;hello
def Encode(string):
    string = str(len(string)) + sep + string
    return string


# 定义缓冲区基类
class Buffer:
    def __init__(self):
        self.message = ""
        self.user_name = ""
