from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.services.settings_service import SettingsService


class TaskTypeSettingsWidget(QWidget):
    types_updated = pyqtSignal(list)

    def __init__(self, service: SettingsService):
        super().__init__()
        self.service = service

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        add_row = QHBoxLayout()
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("新增类型")
        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self.add_type)
        add_row.addWidget(self.type_input, stretch=1)
        add_row.addWidget(self.add_button)
        layout.addLayout(add_row)

        self.type_list = QListWidget()
        layout.addWidget(self.type_list, stretch=1)

        remove_row = QHBoxLayout()
        remove_row.addStretch(1)
        self.remove_button = QPushButton("移除选中")
        self.remove_button.clicked.connect(self.remove_selected)
        remove_row.addWidget(self.remove_button)
        layout.addLayout(remove_row)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_types)
        button_row.addWidget(self.save_button)
        layout.addLayout(button_row)

        self.load_types()

    def load_types(self) -> None:
        self.type_list.clear()
        for name in self.service.get_task_types():
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.type_list.addItem(item)

    def add_type(self) -> None:
        name = self.type_input.text().strip()
        if not name:
            return
        if name == "无":
            QMessageBox.information(self, "提示", "“无”为系统内置项，不能作为自定义类型。")
            return
        if self._has_type(name):
            QMessageBox.information(self, "提示", "该类型已存在。")
            return
        item = QListWidgetItem(name)
        item.setData(Qt.ItemDataRole.UserRole, name)
        self.type_list.addItem(item)
        self.type_input.clear()

    def remove_selected(self) -> None:
        row = self.type_list.currentRow()
        if row < 0:
            return
        self.type_list.takeItem(row)

    def save_types(self) -> None:
        types = []
        for index in range(self.type_list.count()):
            item = self.type_list.item(index)
            name = (item.text() or "").strip()
            if name:
                types.append(name)
        saved = self.service.set_task_types(types)
        self.types_updated.emit(saved)
        QMessageBox.information(self, "设置", "已保存。")

    def _has_type(self, name: str) -> bool:
        for index in range(self.type_list.count()):
            if self.type_list.item(index).text() == name:
                return True
        return False


class StatusSettingsWidget(QWidget):
    statuses_updated = pyqtSignal(list)

    def __init__(self, service: SettingsService):
        super().__init__()
        self.service = service

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        add_row = QHBoxLayout()
        self.status_input = QLineEdit()
        self.status_input.setPlaceholderText("新增状态")
        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self.add_status)
        add_row.addWidget(self.status_input, stretch=1)
        add_row.addWidget(self.add_button)
        layout.addLayout(add_row)

        self.status_list = QListWidget()
        layout.addWidget(self.status_list, stretch=1)

        remove_row = QHBoxLayout()
        remove_row.addStretch(1)
        self.remove_button = QPushButton("移除选中")
        self.remove_button.clicked.connect(self.remove_selected)
        remove_row.addWidget(self.remove_button)
        layout.addLayout(remove_row)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_statuses)
        button_row.addWidget(self.save_button)
        layout.addLayout(button_row)

        self.load_statuses()

    def load_statuses(self) -> None:
        self.status_list.clear()
        for name in self.service.get_statuses():
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.status_list.addItem(item)

    def add_status(self) -> None:
        name = self.status_input.text().strip()
        if not name:
            return
        if name == "无状态":
            QMessageBox.information(self, "提示", "“无状态”为系统内置项，不能作为自定义状态。")
            return
        if self._has_status(name):
            QMessageBox.information(self, "提示", "该状态已存在。")
            return
        item = QListWidgetItem(name)
        item.setData(Qt.ItemDataRole.UserRole, name)
        self.status_list.addItem(item)
        self.status_input.clear()

    def remove_selected(self) -> None:
        row = self.status_list.currentRow()
        if row < 0:
            return
        self.status_list.takeItem(row)

    def save_statuses(self) -> None:
        statuses = []
        for index in range(self.status_list.count()):
            item = self.status_list.item(index)
            name = (item.text() or "").strip()
            if name:
                statuses.append(name)
        saved = self.service.set_statuses(statuses)
        self.statuses_updated.emit(saved)
        QMessageBox.information(self, "设置", "已保存。")

    def _has_status(self, name: str) -> bool:
        for index in range(self.status_list.count()):
            if self.status_list.item(index).text() == name:
                return True
        return False


class SettingsWindow(QMainWindow):
    types_updated = pyqtSignal(list)
    statuses_updated = pyqtSignal(list)

    def __init__(self, service: SettingsService):
        super().__init__()
        self.service = service
        self.setObjectName("SettingsWindow")
        self.setWindowTitle("设置")
        self.resize(460, 380)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("设置")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, stretch=1)

        self.type_settings = TaskTypeSettingsWidget(self.service)
        self.type_settings.types_updated.connect(self.types_updated.emit)
        self.tabs.addTab(self.type_settings, "任务类型配置")

        self.status_settings = StatusSettingsWidget(self.service)
        self.status_settings.statuses_updated.connect(self.statuses_updated.emit)
        self.tabs.addTab(self.status_settings, "状态配置")

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.close)
        button_row.addWidget(self.close_button)
        layout.addLayout(button_row)
