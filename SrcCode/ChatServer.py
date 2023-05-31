import concurrent.futures

import select
import socket
import threading
import time
import sys
import json
from common import *
from concurrent.futures import ThreadPoolExecutor

PORT = 8888  # 定义服务器端口
lock = threading.Lock()  # 定义锁
sendBuffer = []  # 发送缓冲区，以字典形式存放要发送给用户的消息，{user_name:xx, target:xx, message:xx}
user_sep = ":"  # 用于分割用户id和用户名的字符


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

    def UpdateOnlineUsersSeq(self):
        # 构建好数据发送
        res = []
        for user in self.user_group:
            res.append(user.user_name)
        dic = {"user_name": ["list"], "message": res}  # 如果user_name是列表类型，代表发送的是列表
        dic = json.dumps(dic)
        dic = Encode(dic).encode('utf-8')
        for user in self.user_group:
            user.sock.send(dic)

    def AddUser(self, sock, user_name, addr):
        lock.acquire()
        # user_id = str(int(time.time()))  # 用时间戳来表示每一个用户
        # user_name = user_id + user_sep + user_name
        new_user = User(sock, user_name, addr)
        self.user_group.append(new_user)
        lock.release()
        print(f"添加来自: {addr}的用户: {user_name} 成功！！！")
        self.PrintOnlineUsers()
        self.UpdateOnlineUsersSeq()
        return user_name

    def DelUser(self, sock):
        lock.acquire()
        for user in self.user_group:
            if user.sock == sock:
                self.user_group.remove(user)
                print(f"删除来自: {user.addr}的用户: {user.user_name} 成功！！！")
                break
        lock.release()
        self.PrintOnlineUsers()
        self.UpdateOnlineUsersSeq()

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
        self.pool = ThreadPoolExecutor(max_workers=10)  # 创建一个线程池
        self.input = []  # 定义select的输入
        self.output = []  # 定义写事件
        self.exception = []  # 定义异常事件列表

    # 处理新来的用户
    def handlerNewUser(self, conn, addr):
        # 1. 接收用户名 2. 添加到user中
        user_name = conn.recv(1024).decode('utf-8')
        if len(user_name) == 0:
            print("用户退出!!")
            conn.close()
        self.users.AddUser(conn, user_name, addr)

    # 接收信息并放入sendBuffer中
    def Recv(self, sock):
        buffer = ""
        try:
            data = sock.recv(1024).decode('utf-8')  # 添加到缓冲区中
        except Exception as e:
            print(f"用户 {sock.getpeername()} 断开连接: {e}")
            self.users.DelUser(sock)
            self.input.remove(sock)
            return
        print(f"收到的消息: {data}")
        if len(data) == 0:
            # 客户端关闭, 需要从user中删除, 同时select中需要删除
            print("客户端关闭，我也即将关闭链接")
            sock.close()
            self.users.DelUser(sock)
            self.input.remove(sock)
            return
        buffer = buffer + data
        while True:
            pos = buffer.find(sep)
            if pos == -1:
                break
            length = int(buffer[:pos])
            if length > len(buffer):
                # 说明没有截取完整，那么就返回去继续接收
                break
            string = buffer[pos + 2:pos + 2 + length]
            buffer = buffer[pos + 2 + length:len(buffer)]  # 从buffer中删除已经提取的部分
            message = json.loads(string)
            try:
                lock.acquire()
                sendBuffer.append(message)
            finally:
                lock.release()
            print(f"message: {message}")
            continue

    def HandlerSendBuffer(self):
        time.sleep(1)
        for data in sendBuffer:
            # 提取message的各种属性: {user_name:xx, target:xx, message:xx}
            print("检测到存在信息需要转发")
            user_name = data['user_name']
            target = data['target']
            message = data['message']
            print(f"当前消息来自: {user_name}")
            try:
                lock.acquire()
                sendBuffer.remove(data)  # 移除已经提取完毕的数据
            finally:
                lock.release()
            if target == "group":  # 如果是群发，那么pattern指定为group
                # 群发
                user_group = self.users.GetOnlineUser()
                # 给每一个用户都发送消息, 包括自己
                for user in user_group:
                    # 对信息做序列化后编码发送 {"user_name": 用户名, "message": 消息内容} : 如果user_name是all，代表发送的是列表
                    send_data = {"user_name": user_name, "message": message, "pattern": "message"}
                    send_data = json.dumps(send_data)
                    send_data = Encode(send_data)
                    user.sock.send(send_data.encode('utf-8'))
                    print("群发完毕")
            # 私聊 -- 根据target找到对应的用户发送
            else:
                user_group = self.users.GetOnlineUser()
                for user in user_group:
                    if target == user.user_name or user_name == user.user_name:
                        # 对信息做序列化后编码发送 {"user_name": 用户名, "message": 消息内容} : 如果user_name是all，代表发送的是列表
                        send_data = {"user_name": user_name, "message": message, "pattern": "message"}
                        send_data = json.dumps(send_data)
                        send_data = Encode(send_data)
                        user.sock.send(send_data.encode('utf-8'))
                        print("私发完毕")

    def consumer(self):
        self.pool.submit(self.HandlerSendBuffer)

    def producer(self, service_sock):
        future = self.pool.submit(self.Recv, service_sock)
        concurrent.futures.wait([future])

    # 1. 创建监听套接字
    # 2. 添加到select中
    def run(self):
        # 绑定内核，开始监听
        self.sock.bind(self.addr)
        self.sock.listen(5)
        # 把监听套接字添加到select中
        self.input.append(self.sock)
        # 开始服务
        while True:
            rlist, wlist, elist = select.select(self.input, self.output, self.exception)  # 阻塞式等待
            for r in rlist:
                if r is self.sock:
                    # 新连接到来, accept返回一个句柄以及元组0，元组中存储 ip和port
                    service_sock, addr = self.sock.accept()
                    # 将新的sock添加到select中
                    self.input.append(service_sock)
                    # 1. 接收一次用户发送过来的用户名信息，将用户添加到 users中进行管理
                    addr = (service_sock, addr)
                    self.pool.submit(self.handlerNewUser, *addr)
                else:
                    # 用户消息到来
                    # 这里必须要等待sendBuffer有数据
                    self.producer(r)
                    self.pool.submit(self.consumer)


if __name__ == "__main__":
    chatServer = ChatServer()
    chatServer.start()
    while True:
        time.sleep(1)
        if not chatServer.is_alive():
            print("服务器挂了")
            chatServer.pool.shutdown()  # 关闭线程池
            sys.exit(1)
