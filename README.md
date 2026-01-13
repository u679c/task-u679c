# Taskwarrior GUI Client

这是一个基于 Python 和 Qt 的 Taskwarrior 可视化客户端，支持任务管理、状态跟踪和优先级设置等功能。

## 环境要求

- Python 3.8+
- Docker
- Taskwarrior (在 Docker 容器中运行)

## Windows 环境配置步骤

### 1. 安装依赖

确保你的系统已安装以下软件：

- Python 3.8 或更高版本
- Docker Desktop for Windows

### 2. 准案 Docker 容器

首先，你需要创建并运行一个包含 Taskwarrior 的 Docker 容器：

```bash
# 拉取 Ubuntu 镜像
docker pull ubuntu:22.04

# 运行容器，挂载数据卷用于存储任务数据
docker run -dit --name task -v task-data:/root/.task ubuntu:22.04

# 进入容器并安装 Taskwarrior
docker exec -it task bash
apt-get update
apt-get install -y taskwarrior
exit
```

### 3. 安装 Python 依赖

这里包不多 自行下载就好啦

```bash
pip install pyqt6 pyqt6-tools qtawesome
```

### 4. 运行应用程序

直接运行主程序：

```bash
python -m app.main
```

## 项目结构

```
├── app/
│   ├── services/          # 服务层
│   │   └── task_service.py # 任务服务（已修改以支持 Docker）
│   ├── ui/               # 用户界面
│   │   ├── main_window.py # 主窗口
│   │   └── styles.py     # 样式定义
│   ├── models.py         # 数据模型
│   └── main.py           # 程序入口
└── README.md             # 本说明文件
```

## 重要修改说明

在 Windows 环境下运行此项目时，[app/services/task_service.py](file://e:\task-u679c-main\app\services\task_service.py) 文件已被修改以支持通过 Docker 容器执行 Taskwarrior 命令：

- `_run_task` 方法使用 `docker exec -i task task` 命令代替直接调用本地的 `task` 命令
- 处理了 Windows 环境下的编码问题，防止 `UnicodeDecodeError` 错误

## 功能特性

- 任务列表显示和过滤
- 任务状态管理（待办/已完成）
- 优先级设置（高/中/低）
- 截止日期管理
- 任务描述和备注
- 链接关联
- 自定义扩展字段支持

## 注意事项

1. 确保 Docker 服务正在运行
2. 确保名为 `task` 的容器已正确创建并安装了 Taskwarrior
3. 如果需要，可以修改 [task_service.py](file://e:\task-u679c-main\app\services\task_service.py) 中的 Docker 容器名称
4. Windows 环境下可能会有字符编码问题，当前版本已对此进行了处理

## 故障排除

### Docker 相关问题

如果遇到 Docker 连接问题，请确保：

- Docker Desktop 已启动
- 当前用户有权限执行 Docker 命令
- 容器名称与代码中指定的一致

### 编码问题

如果仍然遇到编码错误，请检查 Docker 容器中的 Taskwarrior 输出是否包含特殊字符。
