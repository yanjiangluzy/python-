import json
import socket
import sys
sep = ":;"
# {user_name:xx, pattern:xx, message:xx}
# test_dict = {'user_name': "ly", 'pattern': "group", 'message': "你好"}
#
# # 把字典转成json字符串
# json_text = json.dumps(test_dict)
# length = str(len(json_text))
# json_text = length + ":;" + json_text
# print(length)
# print(json_text)
# json_text = json_text.encode('utf-8')
# print(json_text)
# print(json_text.decode())
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 8888))
sock.send("cx".encode('utf-8'))
while True:
    buffer = ''
    while True:
        data = sock.recv(1024).decode('utf-8')
        if len(data) == 0:
            print("对端关闭")
            sys.exit(1)
        buffer = buffer + data
        while True:
            pos = buffer.find(sep)
            if pos == -1:
                break
            length = int(buffer[:pos])
            print(f"length: {length}")
            if length > len(buffer):
                # 说明没有截取完整，那么就返回去继续接收
                break
            string = buffer[pos + 2:pos + 2 + length]
            buffer = buffer[pos + 2 + length:len(buffer)]  # 从buffer中删除已经提取的部分
            message = json.loads(string)
            print(f"message: {message}")
            continue

