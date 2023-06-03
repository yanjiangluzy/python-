import errno
import queue
import socket
import sys
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import time
from common import *
from llinkDB import *
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, \
    QMessageBox, QLabel, QMainWindow, QPlainTextEdit, QMenu, QAction, QStatusBar, QDialog, QComboBox, QInputDialog
from PyQt5.QtGui import QTextCharFormat, QFont, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, \
    QMenu, QAction

IP = '127.0.0.1'
PORT = '8888'
user_name = ''
recvBuffer = []  # 存放由服务端发送过来的消息, 形式如： {"user_name": ["list"], "message": res} 如果user_name是列表类型，代表发送的是列表
sendBuffer = []  # 存放要发送给服务端的信息， 形式如: {user_name:xx, target:xx, message:xx} target是group代表群发，姓名直接发，做一次特殊处理
login_success = False
online_users = []  # 在线用户列表
all_users = []  # 当前已经注册了的用户名列表
register = "注册"
login = "登录"  # 两个发送信息的前缀，方便服务器进行区分
target = []  # 要发送信息的目标用户，默认为空，代表群发


class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.status_bar = None
        self.child_chat_window = None
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

        tool_bar = self.addToolBar('Tools')

        # 创建选择目标用户的按钮
        select_user_button = QPushButton('选择目标用户')
        select_user_button.clicked.connect(self.on_select_user_clicked)
        tool_bar.addWidget(select_user_button)

        # 用户Action列表
        self.user_actions = []

    def on_select_user_clicked(self):
        # 创建QMenu和Action
        menu = QMenu(self)
        for user in online_users:
            action = QAction(user, self, checkable=True)
            menu.addAction(action)
            self.user_actions.append(action)

        # 弹出QMenu
        pos = self.sender().mapToGlobal(self.sender().rect().bottomLeft())
        selected = menu.exec_(pos)

        # 获取所有已选中用户
        selected_users = [action.text() for action in self.user_actions if action.isChecked()]

        # 更新发送消息的目标用户列表
        global target
        target = selected_users

        # 在状态栏中显示已选中的目标用户
        info = "当前已选中的目标用户：" + ', '.join(target)
        self.create_status_bar(info)

    def create_menu_bar(self):
        pass

    def create_tool_bar(self):
        # 创建工具栏
        tool_bar = self.addToolBar('Tools')

    def create_status_bar(self, info):
        if self.status_bar is not None:
            self.status_bar.deleteLater()
        self.status_bar = QStatusBar()
        self.status_bar.showMessage(info)
        self.setStatusBar(self.status_bar)

    def on_send_clicked(self):
        # 发送信息到服务器, 显示到屏幕
        text = self.input_edit.toPlainText()
        global user_name, sendBuffer, target
        print(f"发送前: {target}")
        dic = {'user_name': user_name, 'target': target, 'message': text}
        sendBuffer.append(dic)
        self.input_edit.clear()
        # 清空target
        target = []
        info = "群聊模式"
        self.create_status_bar(info)


class Register(QDialog):
    def __init__(self):
        super().__init__()
        self.title = '注册界面'
        self.left = 400
        self.top = 200
        self.width = 350
        self.height = 250
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # 设置背景颜色和样式表
        self.setStyleSheet("background-color: #b3d9ff")

        # Username label and textbox
        self.label1 = QLabel('用户名: ', self)
        self.label1.move(50, 20)
        self.label1.setFont(QFont('Arial', 12))
        self.textbox1 = QLineEdit(self)
        self.textbox1.move(150, 20)
        self.textbox1.resize(150, 25)

        # Password label and textbox
        self.label2 = QLabel('密码: ', self)
        self.label2.move(50, 70)
        self.label2.setFont(QFont('Arial', 12))
        self.textbox2 = QLineEdit(self)
        self.textbox2.setEchoMode(QLineEdit.Password)
        self.textbox2.move(150, 70)
        self.textbox2.resize(150, 25)

        # Confirm Password label and textbox
        self.label3 = QLabel('确认密码: ', self)
        self.label3.move(10, 120)
        self.label3.setFont(QFont('Arial', 12))
        self.textbox3 = QLineEdit(self)
        self.textbox3.setEchoMode(QLineEdit.Password)
        self.textbox3.move(150, 120)
        self.textbox3.resize(150, 25)

        # Register button
        self.button_register = QPushButton('注册', self)
        self.button_register.move(130, 180)
        self.button_register.resize(80, 30)
        self.button_register.setStyleSheet("background-color: #3366ff; color: white; font-weight:bold;")
        self.button_register.clicked.connect(self.on_register_click)

    def on_register_click(self):
        if self.textbox1.text() == '' or self.textbox2.text() == '' or self.textbox3.text() == '':
            QMessageBox.information(self, "提示", "请填写完整的注册信息！", QMessageBox.Yes)
        elif self.textbox2.text() != self.textbox3.text():
            QMessageBox.warning(self, "提示", "两次输入的密码不一致，请重新输入！", QMessageBox.Yes)
            self.textbox2.setText("")
            self.textbox3.setText("")
        else:
            # 处理注册逻辑
            username = self.textbox1.text()
            password = self.textbox2.text()
            global sendBuffer, register, online_users
            is_exist = False
            # 检查用户名是否已经存在
            for user in online_users:
                if username == user:
                    is_exist = True
                    break
            if is_exist:
                QMessageBox.warning(self, "提示", "用户名已经存在，请重新选择一个名字", QMessageBox.Yes)
                self.textbox2.setText("")
                self.textbox3.setText("")
                return
            # 将新用户添加到数据库中
            AddToDB(username, password)
            global all_users
            all_users.append((username, password))
            QMessageBox.warning(self, "提示", "注册成功", QMessageBox.Yes)
            self.close()


class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.title = '登陆界面'
        self.left = 400
        self.top = 200
        self.width = 350
        self.height = 250  # increased height to accommodate the registration button
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # 设置背景颜色和样式表
        self.setStyleSheet("background-color: #b3d9ff")

        # Username label and textbox
        self.label1 = QLabel('用户名: ', self)
        self.label1.move(50, 20)
        self.label1.setFont(QFont('Arial', 12))
        self.textbox1 = QLineEdit(self)
        self.textbox1.move(150, 20)
        self.textbox1.resize(150, 25)

        # Password label and textbox
        self.label2 = QLabel('密码: ', self)
        self.label2.move(50, 70)
        self.label2.setFont(QFont('Arial', 12))
        self.textbox2 = QLineEdit(self)
        self.textbox2.setEchoMode(QLineEdit.Password)
        self.textbox2.move(150, 70)
        self.textbox2.resize(150, 25)

        # Login button
        self.button_login = QPushButton('登录', self)
        self.button_login.move(70, 120)
        self.button_login.resize(80, 30)
        self.button_login.setStyleSheet("background-color: #3366ff; color: white; font-weight:bold;")
        self.button_login.clicked.connect(self.on_login_click)

        # Registration button
        self.button_register = QPushButton('注册', self)
        self.button_register.move(190, 120)
        self.button_register.resize(80, 30)
        self.button_register.setStyleSheet("background-color: #3366ff; color: white; font-weight:bold;")
        self.button_register.clicked.connect(self.on_register_click)

        self.show()

    def on_login_click(self):
        if self.textbox1.text() == '' or self.textbox2.text() == '':
            QMessageBox.information(self, "提示", "用户名或密码输入为空", QMessageBox.Yes)
        else:
            # 将用户名发送给服务器
            global login_success, user_name, login, all_users
            user_name = self.textbox1.text()
            password = self.textbox2.text()
            login_user = (user_name, password)
            is_exist = False
            for user in all_users:
                if login_user == user:
                    is_exist = True
                    break
            if is_exist:
                send_data = login + sep + user_name + sep + password
                sendBuffer.append(send_data)
                global login_success
                login_success = True
                self.close()
            else:
                QMessageBox.information(self, "提示", "该用户不存在，请先注册", QMessageBox.Yes)

    def on_register_click(self):
        # Open registration window
        register_window = Register()
        register_window.exec_()


class ChatClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # 链接上服务器
        self.window = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
        self.sock.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 60 * 1000, 30 * 1000))
        self.sock.connect((IP, int(PORT)))
        # 获取当前用户的ip和 port
        self.addr = self.sock.getsockname()
        # 加载当前已注册的所有用户信息
        global all_users
        all_users = GetAllUsersFromDB()
        print(f"all_users: {all_users}")

    # 监视sendBuffer
    def surveillanceSendBuffer(self):
        global sendBuffer
        while True:
            for data in sendBuffer:
                # 1. 发送的是用户名+密码
                if isinstance(data, str):
                    print(f"获取用户名和密码，准备发送 [{__file__}:{sys._getframe().f_lineno}]")
                    sendBuffer.remove(data)
                    self.sock.send(data.encode())
                # 2. 发送的是信息
                else:
                    print(f"获取用户发送的信息，准备发送 [{__file__}:{sys._getframe().f_lineno}]")
                    sendBuffer.remove(data)
                    data = json.dumps(data)
                    data = Encode(data).encode('utf-8')
                    self.sock.send(data)

    # 监视recv_buffer
    def surveillanceRecvBuffer(self):
        global recvBuffer, online_users
        while True:
            for data in recvBuffer:
                recvBuffer.remove(data)
                if data['type'] == "online_users":
                    # 是用户列表, 更新一下在线用户列表
                    global online_users
                    online_users = data["message"]
                else:
                    # 将消息和用户名回显到屏幕上
                    # 构建消息
                    send_message = data["user_name"] + ":" + data["message"]  # 发送该条消息的用户名
                    self.window.text_edit.appendPlainText(send_message)

    # 仅仅负责保证收到一次完整信息，放入recvBuffer中
    def Recv(self):
        # 接收来自服务端的消息
        buffer = ""
        while True:
            data = self.sock.recv(1024).decode('utf-8')
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
                # print(f"length: {length}")
                if length > len(buffer):
                    # 说明没有截取完整，那么就返回去继续接收
                    break
                string = buffer[pos + 2:pos + 2 + length]
                buffer = buffer[pos + 2 + length:len(buffer)]  # 从buffer中删除已经提取的部分
                message = json.loads(string)
                recvBuffer.append(message)
                print(f"收到的消息： {message}")

    # 线程执行该函数创建登录窗口
    def login(self):
        app = QApplication(sys.argv)
        ex = Login()
        sys.exit(app.exec_())

    # 线程执行该函数创建聊天窗口
    def chat(self):
        app = QApplication(sys.argv)
        self.window = ChatWindow()
        self.window.show()
        self.window.create_status_bar("当前是群聊模式, 点击在线用户列表选择用户可以进行私聊")
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
            print(errno)
            sys.exit(3)
