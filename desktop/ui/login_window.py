from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .main_window import MainWindow
from models.user import User

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('登录')
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        # 账号输入
        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("账号")
        layout.addWidget(self.account_input)
        
        # 密码输入
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        # 登录按钮
        self.login_btn = QPushButton("登录")
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)
        
        self.setLayout(layout)
        
    def login(self):
        account = self.account_input.text()
        password = self.password_input.text()
        
        # 测试账号
        test_accounts = {
            "admin": "admin123",
            "test": "test123",
            "user": "user123"
        }
        
        if account in test_accounts and password == test_accounts[account]:
            user = User(account, password, True)
            self.open_main_window(user)
        else:
            QMessageBox.warning(self, "错误", "账号或密码错误！\n可用的测试账号：\nadmin/admin123\ntest/test123\nuser/user123")
            
    def open_main_window(self, user):
        self.main_window = MainWindow(user)
        self.main_window.show()
        self.close()