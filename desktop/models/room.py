from random import randint, choice
from .machine import Machine, MachineState

class LaundryRoom:
    def __init__(self, room_id, machine_count):
        self.room_id = room_id
        self.machines = []
        
        # 创建洗衣机时随机分配状态
        for i in range(machine_count):
            machine = Machine(i, self.room_id)
            # 随机选择一个状态
            machine.state = choice(list(MachineState))
            
            # 如果状态是正在使用，则随机分配一个使用时间（1-120秒）
            if machine.state == MachineState.OCCUPIED:
                machine.time = randint(1, 120)  # 1-120秒
            else:
                machine.time = 0
                
            self.machines.append(machine)
    
    def get_available_machines(self):
        return [i for i, m in enumerate(self.machines) 
                if m.state == MachineState.AVAILABLE]