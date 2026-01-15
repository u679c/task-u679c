# Taskwarrior GUI Client

基于 Python + PyQt6 的 Taskwarrior 可视化客户端，支持任务管理、状态跟踪、优先级、截止日期与链接等功能。

基于Taskwarrior的任务管理系统

## 运行环境

- Python 3.8+
- Taskwarrior
- Windows 需要 Docker（通过容器运行 Taskwarrior）

## 安装依赖（Windows 与 macOS 通用）

推荐使用虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate  # macOS
# 或者在 Windows:
# .venv\Scripts\activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

如果没有 `requirements.txt`，可手动安装：

```bash
pip install pyqt6 pyqt6-tools qtawesome openpyxl
```

## macOS 使用方式

### 方式一：直接安装 Taskwarrior（推荐）

```bash
brew install task
```

运行应用：

```bash
python -m app.main
```
或者你也可以写一个command脚本运行...
### 方式二：使用 Docker（兼容 Windows 的方式）

```bash
docker pull ubuntu:22.04
docker run -dit --name task -v task-data:/root/.task ubuntu:22.04
docker exec -it task bash
apt-get update
apt-get install -y taskwarrior
exit
```

运行应用：

```bash
python -m app.main
```

## Windows 使用方式（Docker）

1. 安装 Docker Desktop for Windows
2. 创建并配置 Taskwarrior 容器：

```bash
docker pull ubuntu:22.04
docker run -dit --name task -v task-data:/root/.task ubuntu:22.04
docker exec -it task bash
apt-get update
apt-get install -y taskwarrior
exit
```

3. 运行应用：

```bash
python -m app.main
```

## 项目结构

```
├── app/
│   ├── services/          # 服务层
│   │   └── task_service.py # 任务服务
│   ├── ui/               # 用户界面
│   │   ├── main_window.py # 主窗口
│   │   └── styles.py     # 样式定义
│   ├── models.py         # 数据模型
│   └── main.py           # 程序入口
└── README.md
```

## 备注

- Windows 依赖 Docker 容器运行 Taskwarrior。
- 如果你改了容器名称，记得同步修改 `app/services/task_service.py` 中的容器名。
