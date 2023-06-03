import sys

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, \
    QMessageBox, QLabel, QMainWindow, QPlainTextEdit, QMenu, QAction, QStatusBar, QDialog
from PyQt5.QtGui import QTextCharFormat, QFont, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, \
    QMenu, QAction


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
            # 在此处将用户名和密码发送给服务器进行注册处理s
            send_data = username + sep + password
            # 等待服务器返回结果
            QMessageBox.information(self, "提示", "注册成功！", QMessageBox.Yes)
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
            global login_success, user_name
            user_name = self.textbox1.text()
            password = self.textbox2.text()
            login_success = True
            send_data = user_name + sep + password
            sendBuffer.append(send_data)
            self.close()

    def on_register_click(self):
        # Open registration window
        register_window = Register()
        register_window.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Login()
    sys.exit(app.exec_())
