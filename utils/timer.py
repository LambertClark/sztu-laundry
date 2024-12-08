class Timer(QObject):
    update_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        
    def update(self):
        # 更新所有洗衣房中的洗衣机时间
        for room in self.get_all_rooms():  # 需要实现获取所有洗衣房的方法
            for machine in room.machines:
                machine.update_timer()
        self.update_signal.emit()