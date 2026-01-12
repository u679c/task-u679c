# Taskwarrior 可视化待办 (PyQt6)

一个本地的 Taskwarrior UI，界面参考 Microsoft To Do，支持优先级与自定义字段 `xstatus`（显示为“状态”）和 `link`。

## 运行环境

- Python 3.10+
- 已安装 Taskwarrior
- PyQt6（`pip install PyQt6`）

## 运行

```bash
python task_manager.py
```

也可以直接运行模块入口：

```bash
python -m app.main
```

## 自定义字段说明

本应用使用 Taskwarrior 的 UDA 字段 `xstatus` 和 `link`。应用在每次调用时都会带上 UDA 定义，因此无需修改 `.taskrc`。
如果你希望永久写入配置，可将以下内容加入 `~/.taskrc`：

```
uda.xstatus.type=string
uda.xstatus.label=状态
uda.link.type=string
uda.link.label=链接
```
