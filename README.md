# Taskwarrior GUI Client

这是一个基于 Python 和 Qt 的 Taskwarrior 可视化客户端，支持任务管理、状态跟踪和优先级设置等功能。

## 为什么需要 Docker 配置

Taskwarrior 是一款功能强大的命令行任务管理工具，但它本身不支持 Windows 环境。因此，我们通过 Docker 容器来运行 Taskwarrior，从而实现了在 Windows 系统上的跨平台兼容。

在非 Windows 系统（Linux/macOS）上，通常可以直接安装和使用 Taskwarrior。但在 Windows 上，最简单的解决方案是通过 Docker 容器运行 Linux 版本的 Taskwarrior。

## 环境要求

- Python 3.8+
- Docker (仅 Windows 需要)
- Taskwarrior (直接安装或通过 Docker 容器)

## 在 macOS 上运行

在 macOS 系统上，你可以选择以下两种方式之一来运行此应用程序：

### 方式一：直接安装 Taskwarrior (推荐)

1. 使用 Homebrew 安装 Taskwarrior：
   ```bash
   brew install task
   ```

2. 安装 Python 依赖：
   ```bash
   pip install pyqt6 pyqt6-tools qtawesome
   ```

3. 直接运行主程序：
   ```bash
   python -m app.main
   ```

   > 注意：如果直接安装 Taskwarrior，你需要使用原始的 [task_service.py](file://e:\task-u679c-main\app\services\task_service.py) 文件（直接调用 `task` 命令而不是通过 Docker）。

### 方式二：使用 Docker (兼容性方式)

如果你希望使用与 Windows 相同的配置，也可以在 macOS 上使用 Docker：

1. 安装 Docker Desktop for Mac

2. 配置 Docker 容器：
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

3. 安装 Python 依赖：
   ```bash
   pip install pyqt6 pyqt6-tools qtawesome
   ```

4. 运行应用程序（使用修改过的 [task_service.py](file://e:\task-u679c-main\app\services\task_service.py)，通过 Docker 执行命令）：
   ```bash
   python -m app.main
   ```

## Windows 环境配置步骤

### 1. 安装依赖

确保你的系统已安装以下软件：

- Python 3.8 或更高版本
- Docker Desktop for Windows

### 2. 配置 Docker 容器

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

```bash
pip install -r requirements.txt
```

如果没有 requirements.txt 文件，请安装以下依赖：

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

1. 确保 Docker 服务正在运行（如果使用 Docker 方式）
2. 确保名为 `task` 的容器已正确创建并安装了 Taskwarrior（如果使用 Docker 方式）
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
