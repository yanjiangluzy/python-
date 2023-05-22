import socket
import threading
import time
import sys
import json

PORT = 8888  # 定义服务器端口
lock = threading.Lock()  # 定义锁
users = []  # 定义在线用户列表, 每一个用户用元组的形式存放对应信息
messages = []  # 定义一个用来存放一条条信息的列表, 形式如: [conn, user_name, addr]


class ChatServer(threading.Thread):
    global PORT, lock, users

    def __init__(self, port=PORT):
        threading.Thread.__init__(self)
        self.addr = ("", port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 使用tcp协议通信

    def Control(self, conn, addr):
        # user列表中需要存储对应的套接字，以及ip地址，用户名等信息
        # 建立链接后，客户端会发送一次自己的用户名信息
        user = conn.recv(1024)
        user = user.decode()
        # 根据ip地址找对应的用户，而不是用户名
        self.AddUser(conn, addr, user)
        print(f"添加来自: {addr}的用户: {user}成功！！！")
        # 做好上述准备工作后，该线程就可以死循环式的开始等待信息的到来
        # noinspection PyBroadException
        try:
            while True:
                data = conn.recv(1024)
                data = data.decode()
                # 将接收的信息放到信息队列中
                self.PutToMessageQueue(conn, data, addr, True)
        except Exception as e:
            print(f"user{user}, ip: {addr[0]}, port: {addr[2]}断开链接")
            self.DelUser(conn, addr)

    def GetOnlineUsers(self):
        res = []
        for user in users:
            res.append(user[1])
        print(f"当前在线的用户列表: {res}")
        return res

    def AddUser(self, conn, addr, user_name):
        users.append((conn, user_name, addr))
        # 添加完用户后, 更新一下在线用户的信息
        online_users = self.GetOnlineUsers()
        self.PutToMessageQueue(conn, online_users, addr, True)

    def DelUser(self, conn, addr):
        for i in range(len(users)):
            if users[i][0] == conn:
                print(f"删除了用户{users[i][1]}, ip: {str(users[i][2][0])}, port: {users[i][2][1]}")
                users.pop(i)
                # 获取当前在线用户列表
                online_users = self.GetOnlineUsers()
                self.PutToMessageQueue(conn, online_users, addr, False)

    def PutToMessageQueue(self, conn, data, addr, isStr):
        # 将已经准备好的信息添加到消息队列中
        lock.acquire()
        if isStr:
            # 是用户发送的消息 [user, data]
            # 找到是哪一个user发送的
            user_name = ""
            for user in users:
                if user[2] == addr:
                    user_name = user[1]
                    break
            messages.append((conn, user_name, data))
        else:
            messages.append((conn, data))
        # 是更新的列表
        lock.release()

    def Send(self):
        for message in messages:
            if len(message) == 3:
                data = str(message[0]) + ": " + str(message[1])
                message[0].send(data.encode())
            else:
                data = json.dumps(message[1])
                for user in users:
                message[0].send(data.encode())

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
