from queue import Queue
from enum import Enum
from datetime import datetime
import random

class MachineState(Enum):
    AVAILABLE = 0
    OCCUPIED = 1
    REPORTED = 2
    BROKEN = 3

class Machine:
    def __init__(self):
        # 随机初始化时间（0-120秒）
        self.time = random.randint(0, 120)
        # 如果初始时间不为0，则设置状态为占用
        self.state = MachineState.OCCUPIED if self.time > 0 else MachineState.AVAILABLE
        self.wait_queue = Queue()
        self.wait_time = 0
        
    def start_washing(self):
        if self.state == MachineState.AVAILABLE:
            self.time = 120
            self.state = MachineState.OCCUPIED
            return True
        return False
    
    def update_timer(self):
        if self.time > 0:
            self.time -= 1
            if self.time == 0:
                if not self.wait_queue.empty():
                    self.wait_queue.get()
                self.state = MachineState.AVAILABLE
        
        if not self.wait_queue.empty():
            if self.wait_time > 0:
                self.wait_time -= 1
            if self.wait_time == 0:
                self.wait_queue.get()