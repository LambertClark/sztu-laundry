from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QComboBox, QTextEdit, 
                            QPushButton, QMessageBox)
from models.machine import MachineState

class ReportWindow(QDialog):
    def __init__(self, machine):
        super().__init__()
        self.machine = machine
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('举报')
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # 举报类型选择
        self.type_combo = QComboBox()
        self.type_combo.addItems(["违规使用", "设备故障"])
        layout.addWidget(self.type_combo)
        
        # 详细说明文本框
        self.detail_text = QTextEdit()
        self.detail_text.setPlaceholderText("请输入具体情况说明...")
        layout.addWidget(self.detail_text)
        
        # 提交按钮
        submit_btn = QPushButton("提交举报")
        submit_btn.clicked.connect(self.submit_report)
        layout.addWidget(submit_btn)
        
        self.setLayout(layout)
        
    def submit_report(self):
        report_type = self.type_combo.currentText()
        detail = self.detail_text.toPlainText()
        
        if not detail:
            QMessageBox.warning(self, "警告", "请输入具体情况说明")
            return
            
        # 更新洗衣机状态
        if report_type == "违规使用":
            self.machine.state = MachineState.REPORTED
        else:
            self.machine.state = MachineState.BROKEN
            
        # 清空等待队列
        while not self.machine.wait_queue.empty():
            self.machine.wait_queue.get()
            
        QMessageBox.information(self, "成功", 
            f"举报已提交\n类型：{report_type}\n说明：{detail}")
        self.accept()