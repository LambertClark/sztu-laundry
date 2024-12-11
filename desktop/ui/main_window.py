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
        self.setFixedSize(1024, 768)  # 改为固定大小，与登录窗口一致
        
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
        
        # 更新所有洗衣房的所有洗衣机的时间
        for room in self.rooms:
            for machine in room.machines:
                machine.update_timer()  # 使用 Machine 类的 update_timer 方法
        
        # 只更新当前显示的洗衣房的界面
        current_room_id = self.room_combo.currentIndex()
        for i in range(self.machine_grid.count()):
            widget = self.machine_grid.itemAt(i).widget()
            if widget:
                machine = self.rooms[current_room_id].machines[i]
                # 只有非故障状态的机器才更新时间显示
                if machine.state != MachineState.BROKEN and hasattr(widget, 'time_label'):
                    widget.time_label.setText(self.format_time(machine.time))
                # 更新状态指示器
                status_indicator = widget.findChild(QLabel, "status_indicator")
                if status_indicator:
                    status_indicator.setStyleSheet(self.get_machine_style(machine.state))
    
    def create_machine_button(self, machine):
        # 创建一个容器widget来包含状态指示器和倒计时标签
        container = QWidget()
        container.setFixedSize(200, 240)
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建状态指示器
        status_indicator = QLabel()
        status_indicator.setObjectName("status_indicator")
        status_indicator.setFixedSize(60, 60)
        status_indicator.setStyleSheet(self.get_machine_style(machine.state))
        layout.addWidget(status_indicator, alignment=Qt.AlignCenter)
        
        # 根据状态添加不同的行为和显示
        if machine.state == MachineState.BROKEN:
            # 故障状态 - 不添加点击事件
            container.setCursor(Qt.ForbiddenCursor)
            container.setStyleSheet("""
                QWidget {
                    background-color: #f5f5f5;
                    border: 1px solid #cccccc;
                    border-radius: 15px;
                    opacity: 0.7;
                }
            """)
            
            # 只显示故障提示标签
            status_text = QLabel("故障维修中")
            status_text.setAlignment(Qt.AlignCenter)
            status_text.setStyleSheet("""
                QLabel {
                    color: #666666;
                    font-size: 18px;
                }
            """)
            layout.addWidget(status_text)
        else:
            # 其他状态显示倒计时
            time_label = QLabel(self.format_time(machine.time))
            time_label.setAlignment(Qt.AlignCenter)
            time_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    color: #333333;
                }
            """)
            layout.addWidget(time_label)
            
            # 存储对label的引用，以便更新
            container.time_label = time_label
            
            # 添加点击事件
            container.setCursor(Qt.PointingHandCursor)
            container.mousePressEvent = lambda event: self.open_machine_window(machine)
            container.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border: 1px solid #cccccc;
                    border-radius: 15px;
                }
                QWidget:hover {
                    border: 2px solid #74b9ff;
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
                border-radius: 30px;  /* 圆角设为宽度的一半 */
                border: 2px solid #cccccc;
                min-width: 60px;
                min-height: 60px;
                max-width: 60px;
                max-height: 60px;
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
        # 对话框关闭后刷新显示
        self.update_machine_grid(self.room_combo.currentIndex())
        
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
    
    def start_using_machine(self, machine):
        # 开始使用洗衣机
        machine.time = 120
        machine.state = MachineState.OCCUPIED
        # 刷新显示
        self.update_machine_grid(self.room_combo.currentIndex())