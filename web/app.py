from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import random
from threading import Thread
import time as time_module
import logging
import sys
from functools import wraps

# 配置日志输出到控制台
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///laundry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 测试账号
TEST_ACCOUNTS = {
    "admin": "admin123",
    "test": "test123",
    "user": "user123"
}

# 数据模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, nullable=False)
    state = db.Column(db.Integer, default=0)  # 0:可用 1:占用 2:举报 3:故障
    report_type = db.Column(db.Integer, default=0)  # 1:违规使用 2:设备故障
    time = db.Column(db.Integer, default=0)   # 使用时的倒计时
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reservations = db.Column(db.Text, default='')  # 存储预约用户ID列表
    reservation_time = db.Column(db.Integer, default=0)  # 预约时间戳

    def to_dict(self):
        # 解析预约列表
        reservation_list = []
        if self.reservations:
            try:
                reservation_list = [int(uid) for uid in self.reservations.split(',') if uid]
            except:
                self.reservations = ''  # 如果解析失败，重置预约列表
                
        return {
            'id': self.id,
            'room_id': self.room_id,
            'state': self.state,
            'report_type': self.report_type,
            'time': self.time,
            'user_id': self.user_id,
            'reservation_count': len(reservation_list),
            'is_reserved_by_current_user': current_user.id in reservation_list if current_user.is_authenticated else False
        }

# 全局变量用于控制更新线程
update_thread_running = True

def update_machines():
    """后台更新洗衣机状态的函数"""
    print("后台更新线程启动")
    while update_thread_running:
        try:
            with app.app_context():
                current_time = int(time_module.time())
                machines = Machine.query.all()
                updated = False
                
                for machine in machines:
                    # 更新使用中的机器
                    if machine.state == 1 and machine.time > 0:
                        machine.time -= 1
                        updated = True
                        print(f"Machine {machine.id}: {machine.time}s remaining")
                        
                        if machine.time == 0:
                            machine.state = 0
                            machine.user_id = None
                            print(f"Machine {machine.id} finished")
                    
                    # 检查预约是否过期（30秒）
                    if machine.reservation_time and (current_time - machine.reservation_time) > 30:
                        machine.reservations = ''
                        machine.reservation_time = 0
                        updated = True
                        print(f"Machine {machine.id} reservations expired")
                
                if updated:
                    db.session.commit()
                    print("数据库已更新")
                
        except Exception as e:
            print(f"更新线程错误: {e}")
            db.session.rollback()
        
        time_module.sleep(1)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 检查测试账号
        if username in TEST_ACCOUNTS and password == TEST_ACCOUNTS[username]:
            user = User.query.filter_by(username=username).first()
            if not user:
                # 如果是第一次登录，创建用户
                user = User(username=username, password=password)
                db.session.add(user)
                db.session.commit()
            login_user(user)
            return redirect(url_for('dashboard'))
            
        flash('用户名或密码错误')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/rooms')
@login_required
def get_rooms():
    machines = Machine.query.all()
    rooms = {}
    for machine in machines:
        if machine.room_id not in rooms:
            rooms[machine.room_id] = []
        rooms[machine.room_id].append(machine.to_dict())
    return jsonify(rooms)

@app.route('/api/machine/<int:machine_id>/start', methods=['POST'])
@login_required
def start_machine(machine_id):
    machine = Machine.query.get_or_404(machine_id)
    if machine.state == 3:  # 只有故障机器不能使用
        return jsonify({
            'success': False,
            'message': '故障机器不能使用'
        })
    
    machine.state = 1
    machine.time = 120  # 2分钟测试时间
    machine.user_id = current_user.id
    # 清空预约信息
    machine.reservations = ''
    machine.reservation_time = 0
    db.session.commit()
    logger.info(f"Machine {machine_id} started with {machine.time}s")
    
    return jsonify({
        'success': True,
        'message': '启动成功'
    })

@app.route('/api/machine/<int:machine_id>/report', methods=['POST'])
@login_required
def report_machine(machine_id):
    machine = Machine.query.get_or_404(machine_id)
    report_type = request.json.get('type', 1)  # 默认为违规使用
    
    if machine.state in [2, 3]:
        return jsonify({
            'success': False,
            'message': '该洗衣机已被举报或故障'
        })
    
    machine.state = 3 if report_type == 2 else 2  # 如果是设备故障，直接设为故障状态
    machine.report_type = report_type
    db.session.commit()
    logger.info(f"Machine {machine_id} reported as type {report_type}")
    
    return jsonify({
        'success': True,
        'message': '举报成功'
    })

@app.route('/api/machine/<int:machine_id>/reserve', methods=['POST'])
@login_required
def reserve_machine(machine_id):
    # 首先检查用户是否已经预约了其他机器
    all_machines = Machine.query.all()
    for machine in all_machines:
        if machine.reservations:
            reservation_list = []
            try:
                reservation_list = [int(uid) for uid in machine.reservations.split(',') if uid]
                if current_user.id in reservation_list:
                    return jsonify({
                        'success': False,
                        'message': '您已经预约了其他洗衣机，每人同时只能预约一台机器'
                    })
            except ValueError:
                machine.reservations = ''  # 如果解析失败，重置预约列表
                db.session.commit()
    
    machine = Machine.query.get_or_404(machine_id)
    
    if machine.state in [2, 3]:  # 举报或故障机器不能预约
        return jsonify({
            'success': False,
            'message': '该机器不能预约'
        })
    
    # 解析当前预约列表
    reservation_list = []
    if machine.reservations:
        try:
            reservation_list = [int(uid) for uid in machine.reservations.split(',') if uid]
        except ValueError:
            machine.reservations = ''
            reservation_list = []
    
    if current_user.id in reservation_list:
        return jsonify({
            'success': False,
            'message': '您已经预约过这台机器'
        })
    
    reservation_list.append(current_user.id)
    machine.reservations = ','.join(str(uid) for uid in reservation_list)
    machine.reservation_time = int(time_module.time())
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '预约成功'
    })

@app.route('/api/machine/<int:machine_id>/cancel_reserve', methods=['POST'])
@login_required
def cancel_reserve_machine(machine_id):
    machine = Machine.query.get_or_404(machine_id)
    
    reservation_list = []
    if machine.reservations:
        try:
            reservation_list = [int(uid) for uid in machine.reservations.split(',') if uid]
        except:
            machine.reservations = ''
    
    if current_user.id in reservation_list:
        reservation_list.remove(current_user.id)
        machine.reservations = ','.join(str(uid) for uid in reservation_list)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '取消预约成功'
        })
    
    return jsonify({
        'success': False,
        'message': '您没有预约这台机器'
    })

@app.route('/api/machine/<int:machine_id>/reset', methods=['POST'])
@login_required
def reset_machine(machine_id):
    machine = Machine.query.get_or_404(machine_id)
    machine.state = 0
    machine.time = 0
    machine.user_id = None
    machine.reservations = ''
    machine.reservation_time = 0
    machine.report_type = 0
    db.session.commit()
    logger.info(f"Machine {machine_id} reset to available")
    
    return jsonify({
        'success': True,
        'message': '状态已重置'
    })

if __name__ == '__main__':
    with app.app_context():
        # 删除现有的数据库
        db.drop_all()
        # 创建新的数据库表
        db.create_all()
        logger.info("数据库已重新创建")
        
        # 创建测试用户
        for username, password in TEST_ACCOUNTS.items():
            if not User.query.filter_by(username=username).first():
                test_user = User(username=username, password=password)
                db.session.add(test_user)
                db.session.commit()
                logger.info(f"创建了测试用户: {username}")
        
        # 初始化洗衣机数据
        if Machine.query.count() == 0:
            for room_id in range(3):  # 3个洗衣房
                for _ in range(8):    # 每个洗衣房8台机器
                    state = random.choice([0, 0, 0, 1, 2, 3])  # 大多数机器可用
                    time = 120 if state == 1 else 0  # 如果是使用中状态，设置2分钟倒计时
                    machine = Machine(
                        room_id=room_id,
                        state=state,
                        time=time,
                        user_id=1 if state == 1 else None,  # 如果是使用中状态，设置用户ID
                        reservations='',  # 初始化空预约列表
                        reservation_time=0,
                        report_type=0  # 初始化举报类型
                    )
                    db.session.add(machine)
            db.session.commit()
            logger.info("初始化完成，使用中的洗衣机：")
            for machine in Machine.query.filter_by(state=1).all():
                logger.info(f"Machine {machine.id}: {machine.time}s remaining")
    
    # 启动后台更新线程
    update_thread = Thread(target=update_machines)
    update_thread.daemon = True
    update_thread.start()
    logger.info("后台更新线程已启动")
    
    try:
        # 启动Flask应用
        app.run(host='127.0.0.1', port=5000, debug=False)
    except KeyboardInterrupt:
        print("程序正在关闭...")
        update_thread_running = False
    except Exception as e:
        print(f"程序错误: {e}")
        update_thread_running = False