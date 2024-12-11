from queue import Queue
from enum import Enum
from datetime import datetime
import random

class MachineState(Enum):
    AVAILABLE = 1
    OCCUPIED = 2
    REPORTED = 3
    BROKEN = 4

class Machine:
    def __init__(self, machine_id, room_id):
        self.machine_id = machine_id
        self.room_id = room_id
        self.state = MachineState.AVAILABLE
        self.time = 0
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
                self.state = MachineState.AVAILABLE
        
        if self.wait_time > 0:
            self.wait_time -= 1
            if self.wait_time == 0:
                if not self.wait_queue.empty():
                    user = self.wait_queue.get()
                    if hasattr(user, 'reserved_machine') and user.reserved_machine == self:
                        user.cancel_reserve()