from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                            QMessageBox, QWidget)
from PyQt5.QtCore import QTimer, Qt
from models.machine import MachineState
from models.user import User
from queue import Queue

class MachineWindow(QDialog):
    def __init__(self, machine, user):
        super().__init__()
        self.machine = machine
        self.user = user
        self.setWindowTitle('洗衣机详情')
        self.setFixedSize(500, 600)  # 设置固定大小
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)  # 增加边距
        
        # 标题
        title_label = QLabel(f"洗衣房 {self.machine.room_id + 1} - 洗衣机 {self.machine.machine_id + 1}")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2d3436;
                margin-bottom: 20px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 状态显示
        state_text = {
            MachineState.AVAILABLE: "状态：空闲",
            MachineState.OCCUPIED: "状态：使用中",
            MachineState.REPORTED: "状态：违规使用",
            MachineState.BROKEN: "状态：故障"
        }
        state_label = QLabel(state_text[self.machine.state])
        state_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                margin: 10px 0;
                padding: 10px;
                background-color: #f5f6fa;
                border-radius: 10px;
            }
        """)
        state_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(state_label)
        
        # 倒计时显示
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                margin: 10px 0;
                padding: 10px;
                background-color: #f5f6fa;
                border-radius: 10px;
            }
        """)
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)
        
        # 等待人数显示
        wait_count = self.machine.wait_queue.qsize()
        self.wait_label = QLabel(f"当前等待人数：{wait_count}")
        self.wait_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                margin: 10px 0;
                padding: 10px;
                background-color: #f5f6fa;
                border-radius: 10px;
            }
        """)
        self.wait_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.wait_label)
        
        # 现在所有标签都创建好了，可以安全地调用 update_time
        self.update_time()
        
        # 按钮容器
        btn_container = QWidget()
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(20)  # 增加按钮之间的间距
        
        # 按钮的通用样式
        button_style = """
            QPushButton {
                background-color: %s;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                width: 240px;  /* 固定宽度 */
                height: 50px;  /* 固定高度 */
            }
            QPushButton:hover {
                background-color: %s;
            }
        """
        
        # 开始使用按钮 - 只在可用或违规状态时显示
        if self.machine.state in [MachineState.AVAILABLE, MachineState.REPORTED]:
            use_btn = QPushButton("开始使用")
            use_btn.setFixedSize(240, 50)  # 设置固定大小
            use_btn.setStyleSheet(button_style % ('#0984e3', '#74b9ff'))
            use_btn.clicked.connect(self.start_using)
            btn_layout.addWidget(use_btn, 0, Qt.AlignCenter)  # 居中对齐
        
        # 预约按钮 - 在非故障状态时显示
        if self.machine.state != MachineState.BROKEN:
            if self.user.reserved_machine is None or self.user.reserved_machine == self.machine:
                reserve_btn = QPushButton("预约" if self.user.reserved_machine != self.machine else "取消预约")
                reserve_btn.setFixedSize(240, 50)  # 设置固定大小
                reserve_btn.setStyleSheet(button_style % ('#00b894', '#55efc4'))
                reserve_btn.clicked.connect(self.reserve_machine if self.user.reserved_machine != self.machine 
                                         else self.cancel_reserve)
                btn_layout.addWidget(reserve_btn, 0, Qt.AlignCenter)  # 居中对齐
        
        # 举报按钮
        report_btn = QPushButton("举报")
        report_btn.setFixedSize(240, 50)  # 设置固定大小
        report_btn.setStyleSheet(button_style % ('#d63031', '#ff7675'))
        report_btn.clicked.connect(self.open_report_window)
        btn_layout.addWidget(report_btn, 0, Qt.AlignCenter)  # 居中对齐
        
        btn_container.setLayout(btn_layout)
        layout.addWidget(btn_container)
        
        self.setLayout(layout)
        
    def update_time(self):
        minutes = self.machine.time // 60
        seconds = self.machine.time % 60
        self.time_label.setText(f"剩余时间：{minutes:02d}:{seconds:02d}")
        
        # 更新等待人数显示
        wait_count = self.machine.wait_queue.qsize()
        self.wait_label.setText(f"当前等待人数：{wait_count}")
        
    def reserve_machine(self):
        # 检查洗衣机状态
        if self.machine.state == MachineState.BROKEN:
            QMessageBox.warning(self, "预约失败", "该洗衣机当前不可用")
            return
            
        # 检查等待队列
        if self.machine.wait_queue.qsize() >= 5:
            QMessageBox.warning(self, "预约失败", "等待人数已达上限")
            return
            
        # 添加到等待队列
        self.machine.wait_queue.put(self.user)
        self.machine.wait_time = 30  # 设置30秒等待时间
        self.user.reserve_machine(self.machine)  # 记录用户的预约
        
        # 更新显示
        wait_count = self.machine.wait_queue.qsize()
        self.wait_label.setText(f"当前等待人数：{wait_count}")
        
        QMessageBox.information(self, "预约成功", 
            "预约成功！\n请在30秒内到达洗衣机前开始使用，\n否则预约将自动取消。")
            
        # 关闭当前窗口并重新打开，以刷新界面
        self.close()
        dialog = MachineWindow(self.machine, self.user)
        dialog.exec_()
        
    def cancel_reserve(self):
        # 从等待队列中移除
        new_queue = Queue()
        while not self.machine.wait_queue.empty():
            user = self.machine.wait_queue.get()
            if user != self.user:
                new_queue.put(user)
        self.machine.wait_queue = new_queue
        
        # 清除用户的预约记录
        self.user.cancel_reserve()
        self.machine.wait_time = 0
        
        # 更新显示
        wait_count = self.machine.wait_queue.qsize()
        self.wait_label.setText(f"当前等待人数：{wait_count}")
        
        QMessageBox.information(self, "取消成功", "已取消预约")
        self.close()
        
    def open_report_window(self):
        from .report_window import ReportWindow
        dialog = ReportWindow(self.machine)
        dialog.exec_()
        
        # 如果洗衣机状态改变，更新显示
        self.update_time()
        
    def start_using(self):
        self.machine.time = 120
        self.machine.state = MachineState.OCCUPIED
        self.close()  # 关闭详情窗口