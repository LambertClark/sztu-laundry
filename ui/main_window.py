from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from models.machine import MachineState
from models.room import LaundryRoom
from .room_window import RoomWindow


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.rooms = [LaundryRoom(i, 8) for i in range(3)]
        self.elapsed_time = 0  # 添加顺计时计数器
        self.init_ui()
        
        # 添加定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all_machines)
        self.timer.start(1000)  # 每秒更新一次
        
    def init_ui(self):
        self.setWindowTitle('洗衣机管理系统')
        self.setMinimumSize(800, 600)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 顶部布局
        top_layout = QHBoxLayout()
        
        # 用户信息显示
        user_info = QLabel(f"账号: {self.user.account}")
        top_layout.addWidget(user_info)
        
        # 添加顺计时显示
        self.time_counter = QLabel("运行时间: 00:00")
        top_layout.addWidget(self.time_counter)
        
        top_layout.addStretch()
        
        # 洗衣房选择下拉框
        self.room_combo = QComboBox()
        self.room_combo.addItems([f"洗衣房 {i+1}" for i in range(3)])
        self.room_combo.currentIndexChanged.connect(self.on_room_changed)
        top_layout.addWidget(self.room_combo)
        
        layout.addLayout(top_layout)
        
        # 洗衣机状态显示区域
        self.machine_grid = QGridLayout()
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.machine_grid)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # 初始显示第一个洗衣房
        self.update_machine_grid(0)
        
    def update_all_machines(self):
        # 更新顺计时
        self.elapsed_time += 1
        minutes = self.elapsed_time // 60
        seconds = self.elapsed_time % 60
        self.time_counter.setText(f"运行时间: {minutes:02d}:{seconds:02d}")
        
        current_room_id = self.room_combo.currentIndex()
        room = self.rooms[current_room_id]
        
        # 更新所有洗衣机的时间
        for machine in room.machines:
            if machine.time > 0:
                machine.time -= 1
                if machine.time == 0:
                    machine.state = MachineState.AVAILABLE
        
        # 更新显示
        for i in range(self.machine_grid.count()):
            widget = self.machine_grid.itemAt(i).widget()
            if widget:
                machine = room.machines[i]
                widget.time_label.setText(self.format_time(machine.time))
                status_indicator = widget.findChild(QLabel, "status_indicator")
                if status_indicator:
                    status_indicator.setStyleSheet(self.get_machine_style(machine.state))
    
    def create_machine_button(self, machine):
        # 创建一个容器widget来包含状态指示器和倒计时标签
        container = QWidget()
        container.setFixedSize(120, 150)  # 设置固定大小
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建状态指示器
        status_indicator = QLabel()
        status_indicator.setObjectName("status_indicator")  # 设置对象名以便查找
        status_indicator.setFixedSize(40, 40)  # 圆点大小
        status_indicator.setStyleSheet(self.get_machine_style(machine.state))
        layout.addWidget(status_indicator, alignment=Qt.AlignCenter)
        
        # 添加倒计时标签
        time_label = QLabel(self.format_time(machine.time))
        time_label.setAlignment(Qt.AlignCenter)
        time_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333333;
            }
        """)
        layout.addWidget(time_label)
        
        # 存储对label的引用，以便更新
        container.time_label = time_label
        
        # 点击事件
        container.mousePressEvent = lambda event: self.open_machine_window(machine)
        
        # 设置容器的样式
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 10px;
            }
        """)
        
        return container
    
    def get_machine_style(self, state):
        colors = {
            MachineState.AVAILABLE: "#4CAF50",  # 绿色
            MachineState.OCCUPIED: "#F44336",   # 红色
            MachineState.REPORTED: "#FFC107",   # 黄色
            MachineState.BROKEN: "#9E9E9E"      # 灰色
        }
        return f"""
            QLabel {{
                background-color: {colors[state]};
                border-radius: 20px;  /* 圆角设为宽度的一半 */
                border: 2px solid #cccccc;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
            }}
        """
    
    def format_time(self, seconds):
        if seconds == 0:
            return "空闲"
        return f"{seconds//60:02d}:{seconds%60:02d}"
        
    def open_machine_window(self, machine):
        from .machine_window import MachineWindow
        dialog = MachineWindow(machine, self.user)
        dialog.exec_()
        
    def on_room_changed(self, index):
        self.update_machine_grid(index)
        
    def update_machine_grid(self, room_id):
        # 清除现有布局
        while self.machine_grid.count():
            item = self.machine_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # 添加洗衣机按钮
        room = self.rooms[room_id]
        for i, machine in enumerate(room.machines):
            btn = self.create_machine_button(machine)
            self.machine_grid.addWidget(btn, i//4, i%4)