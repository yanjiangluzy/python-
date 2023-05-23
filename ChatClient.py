import socket
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import tkinter
import tkinter.messagebox
from tkinter.messagebox import *
from tkinter.scrolledtext import ScrolledText  # 导入滚动文本框

IP = '127.0.0.1'
PORT = '8888'
user_name = ''
listbox1 = ''  # 用于显示在线用户的列表框
ii = 0  # 用于判断是开还是关闭列表框
users = []  # 在线用户列表
chat = '[当前是群聊模式，你的信息将会发送给所有人]'  # 聊天对象, 默认为群聊
SEP = ":;"

# 实现登录窗口
loginWindow = tkinter.Tk()
loginWindow.title("多人在线聊天室")
loginWindow.geometry("270x110")  # 设置好窗口大小

# 设置登录时默认ip和端口, 以及姓名
# default_addr = tkinter.StringVar()
# default_addr.set(":")
user = tkinter.StringVar()
user.set("root")

# 服务器标签 不需要，内部直接使用，不用暴露给用户
# labelIP = tkinter.Label(loginWindow, text='地址:端口')
# labelIP.place(x=20, y=10, width=100, height=20)
#
# entryIP = tkinter.Entry(loginWindow, width=80, textvariable=default_addr)
# entryIP.place(x=120, y=10, width=130, height=20)

# 用户名标签
labelUser = tkinter.Label(loginWindow, text='昵称')
labelUser.place(x=30, y=40, width=80, height=20)

entryUser = tkinter.Entry(loginWindow, width=80, textvariable=user)
entryUser.place(x=120, y=40, width=130, height=20)


# 登录按钮处理函数
def login(*args):
    global IP, PORT, user_name
    # IP, PORT = entryIP.get().split(':')  # 获取IP和端口号
    PORT = int(PORT)  # 端口号需要为int类型
    user_name = entryUser.get()
    if not user:
        tkinter.messagebox.showerror('温馨提示', message='请输入任意的用户名！')
    else:
        loginWindow.destroy()  # 关闭窗口


loginWindow.bind("<Return>", login)
my_button = tkinter.Button(loginWindow, text="登录", command=login)
my_button.place(x=100, y=70, width=70, height=30)

loginWindow.mainloop()

# 链接上服务器
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((IP, PORT))
# 链接上服务器需要发送一次用户名，以便服务器进行管理
sock.send(user_name.encode())
# 获取当前用户的ip和 port
addr = sock.getsockname()

# 创建聊天窗口
chatWindow = tkinter.Tk()
chatWindow.title(user_name)
chatWindow.geometry("400x580")

# 创建滚动文本框用来展示消息
message_box = ScrolledText(chatWindow, width=570, height=320)
message_box.place(x=5, y=0)
# 设置文本框使用的字体颜色
message_box.tag_config('red', foreground='red')
message_box.tag_config('blue', foreground='blue')
message_box.tag_config('green', foreground='green')
message_box.tag_config('pink', foreground='pink')
# 添加欢迎语
message_box.insert(tkinter.END, '欢迎加入聊天室 ！', 'blue')

# 其他功能按钮, 开一个列表存储所有表情 -- TODO 重构代码注意点
b1 = ""
b2 = ""
b3 = ""
b4 = ""
ee = 0  # 代表表情面板开关与否

# 将图片打开存入变量中
p1 = tkinter.PhotoImage(file='./emoji/facepalm.png')
p2 = tkinter.PhotoImage(file='./emoji/smirk.png')
p3 = tkinter.PhotoImage(file='./emoji/concerned.png')
p4 = tkinter.PhotoImage(file='./emoji/smart.png')


# 通过tkinter.PhotoImage函数添加表情
# 通过字典设置表情的映射，以便后续操作
# TODO 重构代码注意点

def mark(exp):  # 参数是发的表情图标记, 发送后将按钮销毁
    global ee
    mes = exp + ':;' + user_name + ':;' + chat
    sock.send(mes.encode())
    b1.destroy()
    b2.destroy()
    b3.destroy()
    b4.destroy()
    ee = 0


# 四个对应的函数
def bb1():
    mark('aa**')


def bb2():
    mark('bb**')


def bb3():
    mark('cc**')


def bb4():
    mark('dd**')


def express():
    global b1, b2, b3, b4, ee
    if ee == 0:
        ee = 1
        b1 = tkinter.Button(chatWindow, command=bb1, image=p1,
                            relief=tkinter.FLAT, bd=0)
        b2 = tkinter.Button(chatWindow, command=bb2, image=p2,
                            relief=tkinter.FLAT, bd=0)
        b3 = tkinter.Button(chatWindow, command=bb3, image=p3,
                            relief=tkinter.FLAT, bd=0)
        b4 = tkinter.Button(chatWindow, command=bb4, image=p4,
                            relief=tkinter.FLAT, bd=0)

        b1.place(x=5, y=248)
        b2.place(x=75, y=248)
        b3.place(x=145, y=248)
        b4.place(x=215, y=248)
    else:
        ee = 0
        b1.destroy()
        b2.destroy()
        b3.destroy()
        b4.destroy()


# 创建表情按钮
eBut = tkinter.Button(chatWindow, text='表情', command=express)
eBut.place(x=5, y=320, width=60, height=30)

# 创建多行文本框, 显示在线用户
onlineUsers = tkinter.Listbox(chatWindow)
onlineUsers.place(x=445, y=0, width=130, height=320)

li = 0  # 用于判断是开还是关闭列表框


def showUsers():
    global listbox1, ii
    if ii == 1:
        listbox1.place(x=445, y=0, width=130, height=320)
        ii = 0
    else:
        listbox1.place_forget()  # 隐藏控件
        ii = 1


# 查看在线用户按钮
button1 = tkinter.Button(chatWindow, text='用户列表', command=showUsers)
button1.place(x=485, y=320, width=90, height=30)

# 创建输入文本框和关联变量
input_txt = tkinter.StringVar()
input_txt.set('')
input_box = tkinter.Entry(chatWindow, width=120, textvariable=input_txt)
input_box.place(x=5, y=350, width=570, height=40)


# 点击发送按钮后做的事
def my_send_group():
    # 群发
    if len(users) == 1:
        prompt_box = tkinter.Tk()
        prompt_box.withdraw()
        showinfo('提示', '当前没有其他在线用户可以交流，请再等等吧！')
    else:
        message = input_box.get()
        input_txt.set("")  # 清空输入框
        for target_user in users:
            if target_user != user_name:
                message = message + SEP + user_name + SEP + "群发"
                sock.send(message.encode())


# 发送按钮
sendButton = tkinter.Button(chatWindow, text="发送", command=my_send_group)
sendButton.place(x=515, y=353, width=60, height=30)
chatWindow.bind('<Return>', my_send_group)  # 绑定回车发送信息



chatWindow.mainloop()



