import threading
import json
from common import *


class User:
    def __init__(self, sock, user_name, addr, password):
        self.sock = sock
        self.user_name = user_name
        self.addr = addr
        self.password = password


# 管理在线用户
class OnlineUsers:
    def __init__(self):
        self.online_user_group = []  # 存放 User列表
        self.lock = threading.Lock()

    def PrintOnlineUsers(self):
        print("当前在线用户: ", end=' ')
        for user in self.online_user_group:
            print(user.user_name, end=' ')
        print()

    def UpdateOnlineUsersSeq(self):
        # 构建好数据发送
        res = []
        for user in self.online_user_group:
            res.append(user.user_name)
        dic = {"type": "online_users", "user_name": "none", "message": res}  # 如果user_name是列表类型，代表发送的是列表
        dic = json.dumps(dic)
        dic = Encode(dic).encode('utf-8')
        for user in self.online_user_group:
            user.sock.send(dic)

    def AddUser(self, sock, user_name, addr, password):
        self.lock.acquire()
        # user_id = str(int(time.time()))  # 用时间戳来表示每一个用户
        # user_name = user_id + user_sep + user_name
        new_user = User(sock, user_name, addr, password)
        self.online_user_group.append(new_user)
        self.lock.release()
        print(f"添加来自: {addr}的用户: {user_name} 成功！！！")
        self.PrintOnlineUsers()
        self.UpdateOnlineUsersSeq()
        return user_name

    def DelUser(self, sock):
        self.lock.acquire()
        for user in self.online_user_group:
            if user.sock == sock:
                self.online_user_group.remove(user)
                print(f"删除来自: {user.addr}的用户: {user.user_name} 成功！！！")
                break
        self.lock.release()
        self.PrintOnlineUsers()
        self.UpdateOnlineUsersSeq()

    def GetOnlineUser(self):
        # 返回一个字典
        dic = {}
        for user in self.online_user_group:
            dic[user.user_name] = user.sock
        return dic
