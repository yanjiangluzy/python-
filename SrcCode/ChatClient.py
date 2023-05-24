import socket
import sys
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import tkinter as tk
import tkinter.messagebox
import ttkbootstrap as ttk
from tkinter.messagebox import *
from tkinter.scrolledtext import ScrolledText  # 导入滚动文本框
from common import *

IP = '127.0.0.1'
PORT = '8888'
user_name = ''
listbox1 = ''  # 用于显示在线用户的列表框
ii = 0  # 用于判断是开还是关闭列表框
users = []  # 在线用户列表
pattern = '[当前是群聊模式，你的信息将会发送给所有人]'  # 聊天对象, 默认为群聊
recvBuffer = []  # 存放由服务端发送过来的消息, 形式如： {"user_name": ["list"], "message": res} 如果user_name是列表类型，代表发送的是列表
sendBuffer = []  # 存放要发送给服务端的信息， 形式如: {user_name:xx, target:xx, message:xx} target是group代表群发，姓名直接发，做一次特殊处理


# 实现登录界面
class Login:
    def __init__(self):
        # 实现登录窗口
        self.login_success = True  # 用来判断是否登录成功
        self.loginWindow = tk.Tk()
        self.loginWindow.title("登录")
        self.loginWindow.geometry("270x110")  # 设置好窗口大小
        self.loginWindow.resizable(False, False)
        self.loginWindow.protocol("WM_DELETE_WINDOW", self.exitLogin)
        self.user = tk.StringVar()  # 用户名文本
        self.user.set("")
        self.entry_user = tk.Entry(self.loginWindow, textvariable=self.user)  # 用户名输入框
        self.label_user = tk.Label(self.loginWindow, text='昵称')
        self.label_user.place(x=30, y=40, width=50, height=20)
        self.entry_user.place(x=90, y=40, width=130, height=20)

    def exitLogin(self):
        self.login_success = False
        print("登录窗口关闭")
        self.loginWindow.destroy()  # 关闭窗口

    # 登录按钮处理函数
    def login(self):
        global IP, PORT, user_name, sendBuffer
        # IP, PORT = entryIP.get().split(':')  # 获取IP和端口号
        PORT = int(PORT)  # 端口号需要为int类型
        user_name = self.entry_user.get()
        if user_name == "":
            tkinter.messagebox.showerror('温馨提示', message='请输入任意的用户名！')
        else:
            # 将建立链接请求发送给服务端，并将用户名发送给服务器
            sendBuffer.append(user_name)  # 输入的用户名直接裸发送就好
            self.loginWindow.destroy()  # 关闭窗口

    def getLoginWindow(self):
        # 设置登录窗口
        # 设置登录按钮
        self.loginWindow.bind("<Return>", self.login)
        my_button = ttk.Button(self.loginWindow, text="登录", command=self.login,
                               bootstyle=("success", "info", "outline"))
        my_button.place(x=100, y=70, width=70, height=30)
        self.loginWindow.mainloop()


# 组件的放置必须按照顺序一个一个创建
class Chat:
    def __init__(self):
        # 创建聊天窗口
        # 消息显示框， 在线用户列表框， 文本输入框， 发送按钮， 显示/隐藏在线用户列表按钮
        self.chatWindow = tk.Tk()
        self.chatWindow.title(user_name)
        self.chatWindow.geometry("670x500")  # 设置宽和高
        # 创建滚动文本框用来展示消息
        self.mention_label = tk.Label(self.chatWindow, width=670, text="欢迎来到聊天室!!!")
        self.message_box = ScrolledText(self.chatWindow, width=570, height=320)  # 将消息展示框设置成为只读
        self.message_box.pack()
        # 设置文本框使用的字体颜色
        self.message_box.tag_config('red', foreground='red')
        self.message_box.tag_config('blue', foreground='blue')
        self.message_box.tag_config('green', foreground='green')
        self.message_box.tag_config('pink', foreground='pink')
        # 添加欢迎语
        self.message_box.insert(tkinter.END, '欢迎加入聊天室 ！\n', 'blue')
        # 文本输入框
        self.input_txt = self.input_txt = tkinter.StringVar()  # 输入的文本
        self.input_txt.set('')
        self.input_box = tkinter.Entry(self.chatWindow, textvariable=self.input_txt)  # 文本输入框
        self.input_box.place(x=5, y=350, width=570, height=40)
        self.input_box.focus()  # 使得焦点一直聚焦在文本输入框，不用按鼠标

    # 点击发送按钮后做的事
    def my_send_group(self):
        # 群发
        global sendBuffer
        if len(users) == 0:
            prompt_box = tkinter.Tk()
            prompt_box.withdraw()
            showinfo('提示', '当前没有其他在线用户可以交流，请再等等吧！')
        else:
            message = self.input_box.get()
            self.input_txt.set("")  # 清空输入框
            # length:;message
            # message: {'user_name':xx, 'target':xx, 'message':xx}
            dic = {'user_name': user_name, 'target': 'group', 'message': message}
            sendBuffer.append(dic)

    # 发送按钮
    def sendButton(self):
        send_button = tkinter.Button(self.chatWindow, text="发送", command=self.my_send_group)
        send_button.place(x=515, y=353, width=60, height=30)
        self.chatWindow.bind('<Return>', self.my_send_group)  # 绑定回车发送信息

    def getChatWindow(self):
        self.sendButton()
        self.chatWindow.mainloop()


class ChatClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # 链接上服务器
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((IP, int(PORT)))
        # 获取当前用户的ip和 port
        addr = self.sock.getsockname()

    # 监视sendBuffer
    def surveillanceSendBuffer(self):
        global sendBuffer
        while True:
            for data in sendBuffer:
                # 1. 发送的是用户名
                if isinstance(data, str):
                    sendBuffer.remove(data)
                    self.sock.send(data.encode())
                # 2. 发送的是信息
                else:
                    sendBuffer.remove(data)
                    data = json.dumps(data)
                    data = Encode(data).encode('utf-8')
                    self.sock.send(data)

    # 监视recv_buffer
    def surveillanceRecvBuffer(self, chat, i):
        global recvBuffer, users
        while True:
            for data in recvBuffer:
                recvBuffer.remove(data)
                if data["user_name"][0] == "list":
                    # 是用户列表
                    users = data["message"]
                else:
                    # 将消息和用户名回显到屏幕上
                    # 构建消息
                    send_message = data["user_name"][0] + ":" + data["message"]  # 发送该条消息的用户名
                    chat.message_box.insert(tkinter.END, send_message + "\n", 'red')

    def Recv(self):
        # 接收来自服务端的消息
        buffer = ""
        while True:
            data = self.sock.recv(1024).decode('utf-8')
            print(f"收到的消息: {data}")
            if len(data) == 0:
                # 客户端关闭
                print("客户端关闭，我也即将关闭链接")
                self.sock.close()
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
                print(f"收到的消息： {message}")
                recvBuffer.append(message)

    def run(self):
        # 启动线程开启recv服务
        recv_t = threading.Thread(target=self.Recv)
        recv_t.start()
        # 启动监视send_buffer线程
        surveillance_send_buffer = threading.Thread(target=self.surveillanceSendBuffer)
        surveillance_send_buffer.start()
        # 构建登录界面
        login = Login()
        login.getLoginWindow()
        # 要检测是否登录成功
        if not login.login_success:
            print("登陆失败")
            sys.exit(3)
        # 构建聊天界面
        chat = Chat()
        # 启动监视recvBuffer线程
        surveillance_recv_buffer = threading.Thread(target=self.surveillanceRecvBuffer, args=(chat, 1))
        surveillance_recv_buffer.start()
        chat.getChatWindow()


if __name__ == "__main__":
    chatClient = ChatClient()
    chatClient.start()
    while True:
        if not chatClient.is_alive():
            sys.exit(3)

# # 其他功能按钮, 开一个列表存储所有表情 -- TODO 重构代码注意点
# b1 = ""
# b2 = ""
# b3 = ""
# b4 = ""
# ee = 0  # 代表表情面板开关与否
#
# # 将图片打开存入变量中
# p1 = tkinter.PhotoImage(file='./emoji/facepalm.png')
# p2 = tkinter.PhotoImage(file='./emoji/smirk.png')
# p3 = tkinter.PhotoImage(file='./emoji/concerned.png')
# p4 = tkinter.PhotoImage(file='./emoji/smart.png')
#
#
# # 通过tkinter.PhotoImage函数添加表情
# # 通过字典设置表情的映射，以便后续操作
# # TODO 重构代码注意点
#
# def mark(exp):  # 参数是发的表情图标记, 发送后将按钮销毁
#     global ee
#     mes = exp + ':;' + user_name + ':;' + chat
#     sock.send(mes.encode())
#     b1.destroy()
#     b2.destroy()
#     b3.destroy()
#     b4.destroy()
#     ee = 0
#
#
# # 四个对应的函数
# def bb1():
#     mark('aa**')
#
#
# def bb2():
#     mark('bb**')
#
#
# def bb3():
#     mark('cc**')
#
#
# def bb4():
#     mark('dd**')
#
#
# def express():
#     global b1, b2, b3, b4, ee
#     if ee == 0:
#         ee = 1
#         b1 = tkinter.Button(chatWindow, command=bb1, image=p1,
#                             relief=tkinter.FLAT, bd=0)
#         b2 = tkinter.Button(chatWindow, command=bb2, image=p2,
#                             relief=tkinter.FLAT, bd=0)
#         b3 = tkinter.Button(chatWindow, command=bb3, image=p3,
#                             relief=tkinter.FLAT, bd=0)
#         b4 = tkinter.Button(chatWindow, command=bb4, image=p4,
#                             relief=tkinter.FLAT, bd=0)
#
#         b1.place(x=5, y=248)
#         b2.place(x=75, y=248)
#         b3.place(x=145, y=248)
#         b4.place(x=215, y=248)
#     else:
#         ee = 0
#         b1.destroy()
#         b2.destroy()
#         b3.destroy()
#         b4.destroy()
#
#
# # 创建表情按钮
# eBut = tkinter.Button(chatWindow, text='表情', command=express)
# eBut.place(x=5, y=320, width=60, height=30)
#
# # 创建多行文本框, 显示在线用户
# onlineUsers = tkinter.Listbox(chatWindow)
# onlineUsers.place(x=445, y=0, width=130, height=320)
#
# li = 0  # 用于判断是开还是关闭列表框
#
#
# def showUsers():
#     global listbox1, ii
#     if ii == 1:
#         listbox1.place(x=445, y=0, width=130, height=320)
#         ii = 0
#     else:
#         listbox1.place_forget()  # 隐藏控件
#         ii = 1


# # 查看在线用户按钮
# button1 = tkinter.Button(chatWindow, text='用户列表', command=showUsers)
# button1.place(x=485, y=320, width=90, height=30)


# def Recv():
#     # 开一个线程用来时刻检测收到的消息，对收到的消息做解码，反序列化后输出到屏幕
#     # 服务器发送的信息，可能是用户列表，也有可能是转发其他用户的信息
#     global recvBuffer, sock
#     buffer = ""
#     while True:
#         data = sock.recv(1024).decode('utf-8')  # 添加到缓冲区中
#         if len(data) == 0:
#             # 客户端关闭
#             print("服务端关闭，我也即将关闭链接")
#             sock.close()
#             sys.exit(2)  # 线程结束生命
#         buffer = buffer + data
#         while True:
#             pos = buffer.find(sep)
#             if pos == -1:
#                 break
#             length = int(buffer[:pos])
#             print(f"length: {length}")
#             if length > len(buffer):
#                 # 说明没有截取完整，那么就返回去继续接收
#                 break
#             string = buffer[pos + 2:pos + 2 + length]
#             buffer = buffer[pos + 2 + length:len(buffer)]  # 从buffer中删除已经提取的部分
#             message = json.loads(string)
#             print(f"message: {message}")
#             recvBuffer.append(message)
#
#
# def parse():
#     # 对recvBuffer中的信息做解析
#     while True:
#
#
