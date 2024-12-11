from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .main_window import MainWindow
from models.user import User
import os

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        # 获取项目根目录路径
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('SZTU洗衣机管理系统')
        self.setFixedSize(1024, 768)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(0, 60, 0, 60)  # 调整上下边距
        
        # Logo
        logo_path = os.path.join(self.root_dir, 'desktop', 'resources', 'images', 'logo.png')
        logo = QPixmap(logo_path)
        logo_label = QLabel()
        logo_label.setPixmap(logo)
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)
        
        # 标题
        title_label = QLabel("欢迎使用SZTU洗衣机管理系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; margin: 20px 0;")
        main_layout.addWidget(title_label)
        
        # 输入框容器
        inputs_container = QWidget()
        inputs_layout = QVBoxLayout()
        inputs_layout.setSpacing(15)
        inputs_layout.setContentsMargins(0, 0, 0, 0)
        
        # 账号输入框
        account_layout = QHBoxLayout()
        account_layout.setContentsMargins(0, 0, 0, 0)
        account_label = QLabel("账号：")
        account_label.setFixedWidth(50)  # 固定标签宽度使两个输入框对齐
        self.account_input = QLineEdit()
        self.account_input.setFixedWidth(400)
        self.account_input.setPlaceholderText("请输入账号")
        account_layout.addStretch()
        account_layout.addWidget(account_label)
        account_layout.addWidget(self.account_input)
        account_layout.addStretch()
        inputs_layout.addLayout(account_layout)
        
        # 密码输入框
        password_layout = QHBoxLayout()
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_label = QLabel("密码：")
        password_label.setFixedWidth(50)  # 固定标签宽度使两个输入框对齐
        self.password_input = QLineEdit()
        self.password_input.setFixedWidth(400)
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addStretch()
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        password_layout.addStretch()
        inputs_layout.addLayout(password_layout)
        
        inputs_container.setLayout(inputs_layout)
        main_layout.addWidget(inputs_container)
        
        # 登录按钮容器
        btn_container = QWidget()
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        # 登录按钮
        self.login_btn = QPushButton("登录")
        self.login_btn.setFixedWidth(400)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.login)
        btn_layout.addStretch()
        btn_layout.addWidget(self.login_btn)
        btn_layout.addStretch()
        
        btn_container.setLayout(btn_layout)
        main_layout.addWidget(btn_container)
        
        # 添加提示信息
        hint_label = QLabel("提示：可使用测试账号 admin/admin123")
        hint_label.setStyleSheet("color: #7f8c8d; font-size: 24px;")
        hint_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(hint_label)
        
        self.setLayout(main_layout)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #dcdde1;
                border-radius: 5px;
                font-size: 24px;
            }
            QLineEdit:focus {
                border: 2px solid #74b9ff;
            }
            QPushButton {
                padding: 12px;
                background-color: #0984e3;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: #74b9ff;
            }
            QLabel {
                color: #2d3436;
                font-size: 24px;
            }
        """)
        
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