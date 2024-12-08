from .machine import Machine, MachineState

class LaundryRoom:
    def __init__(self, room_id, machine_count):
        self.room_id = room_id
        self.machines = [Machine() for _ in range(machine_count)]
    
    def get_available_machines(self):
        return [i for i, m in enumerate(self.machines) 
                if m.state == MachineState.AVAILABLE]