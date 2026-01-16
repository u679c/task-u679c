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
    QVBoxLayout,
    QWidget,
)

from app.services.settings_service import SettingsService


class SettingsWindow(QMainWindow):
    types_updated = pyqtSignal(list)

    def __init__(self, service: SettingsService):
        super().__init__()
        self.service = service
        self.setWindowTitle("设置")
        self.resize(420, 360)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("设置")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)

        section_title = QLabel("任务类型")
        section_title.setStyleSheet("font-size: 14px; font-weight: 600;")
        layout.addWidget(section_title)

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
        self.close_button = QPushButton("关闭")
        self.save_button.clicked.connect(self.save_types)
        self.close_button.clicked.connect(self.close)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.close_button)
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
