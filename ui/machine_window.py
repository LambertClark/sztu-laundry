from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                            QMessageBox)
from PyQt5.QtCore import QTimer
from models.machine import MachineState

class MachineWindow(QDialog):
    def __init__(self, machine, user):
        super().__init__()
        self.machine = machine
        self.user = user
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 倒计时显示
        self.time_label = QLabel()
        self.update_time()
        layout.addWidget(self.time_label)
        
        # 等待人数显示
        wait_count = self.machine.wait_queue.qsize()
        self.wait_label = QLabel(f"当前等待人数：{wait_count}")
        layout.addWidget(self.wait_label)
        
        # 预约按钮
        reserve_btn = QPushButton("预约")
        reserve_btn.clicked.connect(self.reserve_machine)
        layout.addWidget(reserve_btn)
        
        # 举报按钮
        report_btn = QPushButton("举报")
        report_btn.clicked.connect(self.open_report_window)
        layout.addWidget(report_btn)
        
        self.setLayout(layout)
        
    def update_time(self):
        minutes = self.machine.time // 60
        seconds = self.machine.time % 60
        self.time_label.setText(f"剩余时间：{minutes:02d}:{seconds:02d}")
        
    def reserve_machine(self):
        # 检查洗衣机状态
        if self.machine.state != MachineState.AVAILABLE:
            QMessageBox.warning(self, "预约失败", "该洗衣机当前不可用")
            return
            
        # 检查等待队列
        if self.machine.wait_queue.qsize() >= 5:  # 最多允许5人等待
            QMessageBox.warning(self, "预约失败", "等待人数已达上限")
            return
            
        # 添加到等待队列
        self.machine.wait_queue.put(self.user)
        self.machine.wait_time = 30  # 设置30秒等待时间
        
        # 更新显示
        wait_count = self.machine.wait_queue.qsize()
        self.wait_label.setText(f"当前等待人数：{wait_count}")
        
        QMessageBox.information(self, "预约成功", 
            "预约成功！\n请在30秒内到达洗衣机前开始使用，\n否则预约将自动取消。")
        
    def open_report_window(self):
        from .report_window import ReportWindow
        dialog = ReportWindow(self.machine)
        dialog.exec_()
        
        # 如果洗衣机状态改变，更新显示
        self.update_time()