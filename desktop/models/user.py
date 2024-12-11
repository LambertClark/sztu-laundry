class User:
    def __init__(self, account, password, is_admin=False):
        self.account = account
        self.password = password
        self.is_admin = is_admin
        self.reserved_machine = None  # 记录用户当前预约的洗衣机
        
    def reserve_machine(self, machine):
        self.reserved_machine = machine
        
    def cancel_reserve(self):
        self.reserved_machine = None