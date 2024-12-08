from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .machine_window import MachineWindow

class RoomWindow(QDialog):
    def __init__(self, room, user):
        super().__init__()
        self.room = room
        self.user = user
        self.init_ui()
        # 创建定时器以更新显示
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)
        
    def init_ui(self):
        self.setWindowTitle(f'洗衣房 {self.room.room_id}')
        self.setMinimumSize(1000, 800)
        
        layout = QVBoxLayout()
        
        # 创建网格布局来显示洗衣机
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)  # 设置网格间距
        
        # 创建洗衣机按钮网格
        self.machine_buttons = []
        self.update_machine_grid()
        
        # 将网格布局添加到主布局中
        layout.addLayout(self.grid_layout)
        self.setLayout(layout)
        
    def update_machine_grid(self):
        # 清除现有按钮
        for btn in self.machine_buttons:
            btn.deleteLater()
        self.machine_buttons.clear()
        
        # 重新创建洗衣机按钮
        for i, machine in enumerate(self.room.machines):
            btn = self.create_machine_button(machine, i)
            row = i // 4  # 每行4个洗衣机
            col = i % 4
            self.grid_layout.addWidget(btn, row, col)
            self.machine_buttons.append(btn)
            
    def create_machine_button(self, machine, index):
        btn = QPushButton()
        btn.setFixedSize(200, 200)  # 设置按钮大小
        
        # 创建垂直布局来包含状态图标和文本
        layout = QVBoxLayout(btn)
        
        # 添加洗衣机编号
        number_label = QLabel(f"#{index + 1}")
        number_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(number_label)
        
        # 添加状态指示圆点
        status_indicator = QLabel()
        status_indicator.setFixedSize(100, 100)
        status_indicator.setStyleSheet(self.get_status_style(machine.state))
        status_indicator.setAlignment(Qt.AlignCenter)
        layout.addWidget(status_indicator)
        
        # 添加时间显示
        self.time_label = QLabel(self.get_time_text(machine))
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)
        
        # 添加等待人数显示
        wait_label = QLabel(f"等待: {machine.wait_queue.qsize()}人")
        wait_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(wait_label)
        
        # 设置按钮点击事件
        btn.clicked.connect(lambda: self.open_machine_detail(machine))
        
        return btn
        
    def get_status_style(self, state):
        colors = {
            MachineState.AVAILABLE: "#4CAF50",  # 绿色
            MachineState.OCCUPIED: "#F44336",   # 红色
            MachineState.REPORTED: "#FFC107",   # 黄色
            MachineState.BROKEN: "#9E9E9E"      # 灰色
        }
        return f"""
            QLabel {{
                background-color: {colors[state]};
                border-radius: 50px;
                margin: 10px;
            }}
        """
        
    def get_time_text(self, machine):
        if machine.time > 0:
            minutes = machine.time // 60
            seconds = machine.time % 60
            return f"{minutes:02d}:{seconds:02d}"
        return "空闲"
        
    def open_machine_detail(self, machine):
        dialog = MachineWindow(machine, self.user)
        dialog.exec_()
        
    def update_display(self):
        """定时更新显示"""
        self.update_machine_grid()