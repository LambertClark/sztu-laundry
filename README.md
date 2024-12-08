# 洗衣机管理系统

一个集中管理洗衣机的系统，包含桌面客户端（PyQt5）和 Web 端（Flask + Tailwind CSS）两个版本。支持实时监控、预约管理、故障报告等功能。

## 功能特点

### 核心功能
- 多洗衣房管理
- 实时状态监控
- 预约系统
- 故障报告
- 计时功能
- 等待队列管理

### 用户功能
- 账号管理
- 实时预约
- 故障举报
- 使用计时
- 状态查看

## 技术栈

### 桌面客户端
- Python 3.x
- PyQt5
- SQLite

### Web端
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Tailwind CSS
- SQLite

## 安装说明

### 环境要求
- Python 3.8+
- pip 包管理器

### 桌面客户端

1. 安装依赖：
```bash
pip install PyQt5
```

2. 运行程序：
```bash
cd desktop
python main.py
```

### Web端

1. 安装依赖：
```bash
pip install flask flask-login flask-sqlalchemy
```

2. 运行服务器：
```bash
cd web
python app.py
```

3. 访问系统：
   - 打开浏览器访问 `http://localhost:5000`

## 使用说明

### 测试账号
```
admin / admin123
test / test123
user / user123
```

## 状态说明

洗衣机状态分为四种：
- 可用（绿色）
- 使用中（红色）
- 已举报（黄色）
- 故障（灰色）

## 系统限制

1. 预约系统
   - 最多支持5人等待
   - 预约有效期为30秒
   - 超时自动取消
   - 每人同时只能预约一台机器

2. 使用限制
   - 故障机器不可使用
   - 使用中机器不可重复预约
   - 举报后自动清空等待队列

## 开发说明

### 桌面客户端
- 使用 PyQt5 开发
- MVC 架构设计
- 实时更新机制
- 模块化界面设计

### Web端
- Flask 后端框架
- Tailwind CSS 前端样式
- 响应式设计
- 实时状态更新

## 许可证

MIT License