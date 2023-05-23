import socket
import threading
import time
import sys
import json
from common import *

PORT = 8888  # 定义服务器端口
lock = threading.Lock()  # 定义锁
sendBuffer = []  # 发送缓冲区，以字典形式存放要发送给用户的消息，{user_name:xx, pattern:xx, message:xx}


class User:
    def __init__(self, sock, user_name, addr):
        self.sock = sock
        self.user_name = user_name
        self.addr = addr


class Users:
    def __init__(self):
        self.user_group = []  # 存放 User列表

    def PrintOnlineUsers(self):
        print("当前在线用户: ", end=' ')
        for user in self.user_group:
            print(user.user_name, end=' ')
        print()

    def AddUser(self, sock, user_name, addr):
        lock.acquire()
        new_user = User(sock, user_name, addr)
        self.user_group.append(new_user)
        lock.release()
        self.PrintOnlineUsers()

    def DelUser(self, addr):
        lock.acquire()
        for user in self.user_group:
            if user.addr == addr:
                self.user_group.remove(user)
                break
        lock.release()
        self.PrintOnlineUsers()

    def GetOnlineUser(self):
        # 全盘返回，交由send处理
        res = self.user_group
        return res


class ChatServer(threading.Thread):
    global PORT, lock

    def __init__(self, port=PORT):
        threading.Thread.__init__(self)
        self.addr = ("", port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 使用tcp协议通信
        self.users = Users()  # 定义一个用来管理用户的数据结构

    # 主体控制逻辑: 1. 将新用户添加到在线用户列表中 2. 接收来自该用户的消息
    def Control(self, conn, addr):
        # 建立链接后，客户端会发送一次自己的用户名信息
        user_name = conn.recv(1024).decode('utf-8')  # 这里一定收集齐了一次信息吗？
        self.users.AddUser(conn, user_name, addr)
        print(f"添加来自: {addr}的用户: {user_name}成功！！！")
        # 做好上述准备工作后，该线程就可以死循环式的开始等待信息的到来
        # noinspection PyBroadException
        try:
            while True:
                self.Recv(conn)
        except Exception as e:
            print(f"user: {user_name}, ip: {addr[0]}, port: {addr[1]}断开链接")
            self.users.DelUser(addr)
            conn.close()

    # 提取信息
    def Recv(self, sock):
        buffer = ""
        while True:
            data = sock.recv(1024).decode('utf-8')  # 添加到缓冲区中
            print(f"收到的消息: {data}")
            if len(data) == 0:
                # 客户端关闭
                print("客户端关闭，我也即将关闭链接")
                sock.close()
                sys.exit(2)  # 线程结束生命
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
                sendBuffer.append(message)
                continue

    def Send(self):
        while True:
            time.sleep(1)
            for data in sendBuffer:
                # 提取message的各种属性: {user_name:xx, target:xx, message:xx}
                print("检测到存在信息需要转发")
                user_name = data['user_name']
                target = data['target']
                message = data['message']
                if target == "group":  # 如果是群发，那么pattern指定为group
                    # 群发
                    print("开始群发...")
                    user_group = self.users.GetOnlineUser()
                    # 给每一个用户都发送消息，除了自己
                    for user in user_group:
                        if user.user_name != user_name:
                            # 对信息做序列化后编码发送
                            send_data = {"user_name": user_name, "message": message}
                            send_data = json.dumps(send_data)
                            send_data = Encode(send_data)
                            user.sock.send(send_data.encode())
                            sendBuffer.remove(data) # 移除已经发送的数据
                            print("发送完毕")
                # 私聊 -- 根据target找到对应的用户发送
                # TODO

    def run(self):
        # 绑定内核，开始监听
        self.sock.bind(self.addr)
        self.sock.listen(5)
        # 启动一个线程用来监视发送缓冲区，如果发现有可以发送的信息，就立即发送
        send_thread = threading.Thread(target=self.Send)
        send_thread.start()
        while True:
            # 在建立链接时获取到对应用户的信息及新建立好的套接字, 并更新在线用户列表
            conn, addr = self.sock.accept()
            t = threading.Thread(target=self.Control, args=(conn, addr))
            t.start()


if __name__ == "__main__":
    chatServer = ChatServer()
    chatServer.start()
    while True:
        time.sleep(1)
        if not chatServer.is_alive():
            print("服务器挂了")
            sys.exit(1)
