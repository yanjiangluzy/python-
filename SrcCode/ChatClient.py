import queue
import socket
import sys
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import time
from common import *
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, \
    QMessageBox, QLabel, QMainWindow, QPlainTextEdit, QMenu, QAction
from PyQt5.QtGui import QTextCharFormat, QFont, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, \
    QMenu, QAction

IP = '127.0.0.1'
PORT = '8888'
user_name = ''
listbox1 = ''  # 用于显示在线用户的列表框
ii = 0  # 用于判断是开还是关闭列表框
users = []  # 在线用户列表
pattern = '[当前是群聊模式，你的信息将会发送给所有人]'  # 聊天对象, 默认为群聊
recvBuffer = []  # 存放由服务端发送过来的消息, 形式如： {"user_name": ["list"], "message": res} 如果user_name是列表类型，代表发送的是列表
sendBuffer = []  # 存放要发送给服务端的信息， 形式如: {user_name:xx, target:xx, message:xx} target是group代表群发，姓名直接发，做一次特殊处理
login_success = False


class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        global user_name
        self.setWindowTitle(user_name)
        self.setGeometry(200, 200, 800, 600)

        # 创建主窗口部件，并设置为菜单栏、工具栏、状态栏
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout()
        widget.setLayout(layout)
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_status_bar()

        # 创建聊天记录文本框
        self.text_edit = QPlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet('background-color: #F1F1F1; border-radius: 10px; padding: 10px;')
        layout.addWidget(self.text_edit, 1)  # 设置 stretch 参数为 1，使其尽可能地占用空间

        # 创建输入框和发送按钮
        bottom_layout = QHBoxLayout()
        layout.addLayout(bottom_layout)
        self.input_edit = QPlainTextEdit()
        self.input_edit.setMaximumHeight(40)  # 设置输入框最大高度为 40 像素
        self.input_edit.setStyleSheet('background-color: white; border-radius: 20px; padding: 10px;')
        send_button = QPushButton('Send')
        send_button.setStyleSheet(
            'QPushButton { background-color: #4CAF50; color: white; border-radius: 20px; padding: 10px; }'
            'QPushButton:hover { background-color: #3E8E41; }')
        send_button.clicked.connect(self.on_send_clicked)
        bottom_layout.addWidget(self.input_edit)
        bottom_layout.addWidget(send_button)

        # 设置窗口背景颜色
        self.setStyleSheet("background-color: #f5f5f7;")

        # 设置聊天记录文本框字体样式和大小
        self.text_edit.setStyleSheet("font-family: Arial; font-size: 14px;")

        # 设置输入框字体样式和大小
        self.input_edit.setStyleSheet("font-family: Arial; font-size: 14px;")

    def create_menu_bar(self):
        pass

    def create_tool_bar(self):
        # 创建工具栏
        tool_bar = self.addToolBar('Tools')

        # 创建加粗按钮
        bold_button = QAction('Bold', self)
        bold_button.setCheckable(True)
        bold_button.setIcon(QIcon('bold.png'))
        bold_button.triggered.connect(self.on_bold_clicked)

        # 将加粗按钮添加到工具栏中
        tool_bar.addAction(bold_button)

    def on_bold_clicked(self, checked):
        # 在输入框中添加或删除加粗格式
        cursor = self.input_edit.textCursor()
        if checked:
            font = cursor.charFormat().font()
            font.setBold(True)
            cursor.mergeCharFormat(QTextCharFormat())
        else:
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Normal)
            cursor.mergeCharFormat(fmt)

    def create_status_bar(self):
        pass

    def on_send_clicked(self):
        # 发送信息到服务器, 显示到屏幕
        text = self.input_edit.toPlainText()
        global user_name, sendBuffer
        dic = {'user_name': user_name, 'target': 'group', 'message': text}
        sendBuffer.append(dic)
        self.input_edit.clear()


# 实现登录界面
class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Login'
        self.left = 400
        self.top = 200
        self.width = 350
        self.height = 200
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # 设置背景颜色和样式表
        self.setStyleSheet("background-color: #b3d9ff")
        self.label1 = QLabel('Username: ', self)
        self.label1.move(50, 20)
        self.label1.setFont(QFont('Arial', 12))

        # 输入框1
        self.textbox1 = QLineEdit(self)
        self.textbox1.move(150, 20)
        self.textbox1.resize(150, 25)

        # 标签2
        self.label2 = QLabel('Password: ', self)
        self.label2.move(50, 70)
        self.label2.setFont(QFont('Arial', 12))

        # 输入框2
        self.textbox2 = QLineEdit(self)
        self.textbox2.setEchoMode(QLineEdit.Password)
        self.textbox2.move(150, 70)
        self.textbox2.resize(150, 25)

        # 创建一个按钮
        self.button = QPushButton('Login', self)
        self.button.move(130, 120)
        self.button.resize(80, 30)

        # 设置按钮颜色和样式表
        self.button.setStyleSheet("background-color: #3366ff; color: white; font-weight:bold;")

        # 链接按钮到槽函数
        self.button.clicked.connect(self.on_click)

        self.show()

    def on_click(self):
        if self.textbox1.text() == '':
            QMessageBox.information(self, "提示", "用户名输入为空", QMessageBox.Yes)
        else:
            # 将用户名发送给服务器
            global login_success, user_name
            user_name = self.textbox1.text()
            login_success = True
            sendBuffer.append(user_name)
            self.close()


class ChatClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # 链接上服务器
        self.window = None
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
    def surveillanceRecvBuffer(self):
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
                    self.window.text_edit.appendPlainText(send_message)

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

    # 线程执行该函数创建登录窗口
    def login(self):
        app = QApplication(sys.argv)
        ex = Login()
        sys.exit(app.exec_())

    # 线程执行该函数创建聊天窗口
    def chat(self):
        app = QApplication(sys.argv)
        window = ChatWindow()
        self.window = window
        window.show()
        sys.exit(app.exec_())

    def run(self):
        # 启动线程开启recv服务
        recv_t = threading.Thread(target=self.Recv)
        recv_t.start()
        # 启动监视send_buffer线程
        surveillance_send_buffer = threading.Thread(target=self.surveillanceSendBuffer)
        surveillance_send_buffer.start()
        # 构建登录界面
        login_t = threading.Thread(target=self.login)
        login_t.start()
        # 构建聊天界面
        global login_success
        while not login_success:
            time.sleep(1)
        chat_t = threading.Thread(target=self.chat)
        chat_t.start()
        # 启动监视recvBuffer线程
        surveillance_recv_buffer = threading.Thread(target=self.surveillanceRecvBuffer)
        surveillance_recv_buffer.start()


if __name__ == "__main__":
    chatClient = ChatClient()
    chatClient.start()
    while True:
        if not chatClient.is_alive():
            sys.exit(3)
