import json

sep = ":;"


# e.g: 5:;hello
def Encode(string):
    string = str(len(string)) + sep + string
    return string


def Decode(string):
    # 对接收上来的数据进行解码
    pos = string.find(sep)
    if pos == -1:
        return ""
    # 到这里一定能够提取出长度
    length = int(string[:pos])
    if length > len(string):
        # 说明没有截取完整，那么就返回去继续接收
        return ""
    return string[pos + 2:pos + 2 + length + 1]
