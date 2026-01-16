from datetime import datetime, timezone

from PyQt6.QtCore import QDate, Qt
import sys

from PyQt6.QtGui import QAction, QColor, QIcon, QKeySequence, QPalette, QShortcut
from PyQt6.sip import isdeleted
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QDateEdit,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

try:
    import qtawesome as qta
except ImportError:
    qta = None


def _icon(name: str, color: str) -> QIcon:
    if qta is None:
        return QIcon()
    return qta.icon(name, color=color)

from app.models import TaskItem
from app.services.settings_service import SettingsService
from app.services.task_service import TaskService
from app.ui.settings_window import SettingsWindow

PRIORITY_LABELS = {
    "H": "紧急",
    "M": "重要",
    "L": "低优先",
}

DEFAULT_STATUS_LABEL = "待开始"
NONE_TYPE_LABEL = "无"


def normalize_task_type(value: str) -> str:
    if not value:
        return ""
    value = value.strip()
    if value == NONE_TYPE_LABEL:
        return ""
    return value


class TaskListItemWidget(QWidget):
    def __init__(self, task: TaskItem, on_toggle):
        super().__init__()
        self.task = task
        self.on_toggle = on_toggle
        self.is_selected = False
        self.item = None
        self.list_widget = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        self.checkbox = QCheckBox()
        self.checkbox.toggled.connect(self._on_toggled)
        layout.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignVCenter)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        title_text = self._format_title(task)
        self.title_label = QLabel(title_text)
        self.title_label.setTextFormat(Qt.TextFormat.PlainText)
        self.title_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.title_label.setStyleSheet("color: #1a1d24; font-weight: 600;")
        text_layout.addWidget(self.title_label)

        effective_priority = task.priority or "L"
        priority_label = PRIORITY_LABELS.get(effective_priority, effective_priority)
        priority_text = f"【{priority_label}】" if priority_label else ""
        status_text = task.xstatus or (DEFAULT_STATUS_LABEL if task.task_state != "completed" else "已完成")
        link_text = task.link or "无链接"
        completion_text = ""
        if task.task_state == "completed":
            completion_text = self._format_completed(task.end)
        due_text = self._format_due(task.due)
        if task.link:
            meta_html = (
                f"{priority_text}{status_text}{completion_text}{due_text} · "
                f"<a href=\"{task.link}\">{link_text}</a>"
            )
        else:
            meta_html = f"{priority_text}{status_text}{completion_text}{due_text} · {link_text}"
        self.meta_label = QLabel(meta_html)
        self.meta_label.setTextFormat(Qt.TextFormat.RichText)
        self.meta_label.setOpenExternalLinks(True)
        self.meta_label.setStyleSheet("color: #4b5563;")
        text_layout.addWidget(self.meta_label)

        layout.addLayout(text_layout, stretch=1)

        self.apply_completed_style(task.task_state == "completed")
        self._install_click_filters()
        self.setAutoFillBackground(False)

    def bind_item(self, item, list_widget):
        self.item = item
        self.list_widget = list_widget
        self._update_size()

    def set_checked(self, checked: bool):
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(checked)
        self.checkbox.blockSignals(False)

    def apply_completed_style(self, completed: bool):
        for label in (self.title_label, self.meta_label):
            font = label.font()
            font.setStrikeOut(completed)
            label.setFont(font)
        self._apply_text_color()

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self._apply_text_color()

    def _apply_text_color(self):
        if self.is_selected:
            title_color = "#000000"
            meta_color = "#000000"
        elif self.task.task_state == "completed":
            title_color = "#9aa3b2"
            meta_color = "#9aa3b2"
        else:
            title_color = "#1a1d24"
            meta_color = "#4b5563"
        self.title_label.setStyleSheet(f"color: {title_color}; font-weight: 600;")
        self.meta_label.setStyleSheet(f"color: {meta_color};")
        self.setStyleSheet("background: transparent;")

    def _on_toggled(self, checked: bool):
        self.on_toggle(self.task.uuid, checked)

    def _install_click_filters(self):
        self.installEventFilter(self)
        self.title_label.installEventFilter(self)
        self.meta_label.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == event.Type.MouseButtonPress:
            if (
                self.list_widget is not None
                and self.item is not None
                and not isdeleted(self.list_widget)
                and not isdeleted(self.item)
            ):
                self.list_widget.setCurrentItem(self.item)
        return super().eventFilter(obj, event)

    def _update_size(self):
        if self.item is not None:
            self.item.setSizeHint(self.sizeHint())

    @staticmethod
    def _format_title(task: TaskItem) -> str:
        xtype = normalize_task_type(task.xtype)
        if xtype:
            return f"{xtype}·{task.description}"
        return task.description or ""

    @staticmethod
    def _format_due(due_value: str) -> str:
        if not due_value:
            return ""
        parsed = parse_due_date(due_value)
        if not parsed:
            return f" · 截止 {due_value}"
        if TaskListItemWidget._is_same_week(parsed, QDate.currentDate()):
            weekday = TaskListItemWidget._weekday_label(parsed)
            return f" · 截止 {parsed.toString('yyyy-MM-dd')} {weekday}"
        return f" · 截止 {parsed.toString('yyyy-MM-dd')}"

    @staticmethod
    def _format_completed(end_value: str) -> str:
        if not end_value:
            return ""
        parsed = parse_task_datetime(end_value)
        if not parsed:
            return f" · 完成 {end_value}"
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone()
        return f" · 完成 {parsed.strftime('%Y-%m-%d %H:%M')}"

    @staticmethod
    def _is_same_week(date: QDate, today: QDate) -> bool:
        if not date.isValid() or not today.isValid():
            return False
        date_week = date.weekNumber()
        today_week = today.weekNumber()
        return date_week == today_week

    @staticmethod
    def _weekday_label(date: QDate) -> str:
        labels = {
            1: "周一",
            2: "周二",
            3: "周三",
            4: "周四",
            5: "周五",
            6: "周六",
            7: "周日",
        }
        return labels.get(date.dayOfWeek(), "")


class MainWindow(QMainWindow):
    def __init__(self, service: TaskService, settings_service: SettingsService):
        super().__init__()
        self.service = service
        self.settings_service = settings_service
        self.setWindowTitle("Taskwarrior 可视化待办")
        self.resize(1200, 720)

        self.current_filter = "all"
        self.current_type: str | None = None
        self.expanded_filter: str | None = None
        self.type_options: list[str] = []
        self.tasks_by_uuid: dict[str, TaskItem] = {}
        self.item_widgets: dict[str, TaskListItemWidget] = {}
        self.is_populating = False
        self.current_task_uuid: str | None = None
        self.is_loading_details = False
        self.sidebar_sections: dict[str, dict[str, object]] = {}
        self.settings_window: SettingsWindow | None = None

        self.reload_type_options()

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(16, 12, 16, 12)
        root_layout.setSpacing(12)

        header = QLabel("任务清单")
        header.setObjectName("HeaderTitle")
        header.setStyleSheet("font-size: 28px; font-weight: 600;")
        root_layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root_layout.addWidget(splitter, stretch=1)

        splitter.addWidget(self._build_sidebar())
        splitter.addWidget(self._build_list_panel())
        splitter.addWidget(self._build_detail_panel())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 1)

        self._build_menu()
        self._setup_macos_shortcuts()
        self.refresh_tasks()

    def _build_menu(self):
        refresh_action = QAction("刷新", self)
        refresh_action.triggered.connect(self.refresh_tasks)
        self.menuBar().addAction(refresh_action)

    def _setup_macos_shortcuts(self):
        if sys.platform != "darwin":
            return
        minimize_shortcut = QShortcut(QKeySequence("Meta+W"), self)
        minimize_shortcut.activated.connect(self.showMinimized)
        quit_shortcut = QShortcut(QKeySequence("Meta+Q"), self)
        quit_shortcut.activated.connect(self.close)

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(8, 8, 8, 8)
        sidebar.setMinimumWidth(210)

        title = QLabel("清单")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(title)

        sections = [
            ("all", "全部任务"),
            ("pending", "待办"),
            ("completed", "已完成"),
        ]
        for filter_name, label in sections:
            button = QPushButton(label)
            button.setObjectName("SidebarButton")
            button.clicked.connect(lambda checked=False, name=filter_name: self.on_filter_clicked(name))
            layout.addWidget(button)

            type_container = QWidget()
            type_layout = QVBoxLayout(type_container)
            type_layout.setContentsMargins(18, 0, 0, 6)
            type_layout.setSpacing(4)
            type_container.setVisible(False)
            layout.addWidget(type_container)

            self.sidebar_sections[filter_name] = {
                "button": button,
                "container": type_container,
                "layout": type_layout,
            }
        layout.addStretch(1)

        self.settings_button = QPushButton()
        self.settings_button.setObjectName("SettingsButton")
        self.settings_button.setIcon(_icon("fa5s.cog", color="#6b7280"))
        self.settings_button.setToolTip("设置")
        self.settings_button.setFixedSize(32, 32)
        self.settings_button.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_button, alignment=Qt.AlignmentFlag.AlignLeft)

        return sidebar

    def _build_list_panel(self):
        panel = QFrame()
        panel.setObjectName("ListPanel")
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchInput")
        self.search_input.setPlaceholderText("搜索任务...")
        self.search_input.textChanged.connect(self.apply_search_filter)
        layout.addWidget(self.search_input)

        sort_row = QHBoxLayout()
        sort_label = QLabel("排序")
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("默认", "default")
        self.sort_combo.addItem("优先级：高 → 低", "priority")
        self.sort_combo.addItem("截止日期：近 → 远", "due")
        self.sort_combo.currentIndexChanged.connect(self.on_sort_changed)
        sort_row.addWidget(sort_label)
        sort_row.addWidget(self.sort_combo, stretch=1)
        self.export_button = QPushButton("导出")
        self.export_button.setFixedHeight(35)
        self.export_button.setObjectName("ExportButton")
        self.export_button.setIcon(_icon("fa5s.file-export", color="#1f5fd1"))
        self.export_button.clicked.connect(self.export_tasks)
        sort_row.addWidget(self.export_button)
        layout.addLayout(sort_row)

        self.task_list = QListWidget()
        palette = self.task_list.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#DBEAFE"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
        self.task_list.setPalette(palette)
        self.task_list.setSpacing(8)
        self.task_list.itemSelectionChanged.connect(self.on_task_selected)
        layout.addWidget(self.task_list, stretch=1)

        add_row = QHBoxLayout()
        self.new_task_input = QLineEdit()
        self.new_task_input.setPlaceholderText("添加任务")
        self.add_task_button = QPushButton("添加")
        self.add_task_button.clicked.connect(self.add_task)
        add_row.addWidget(self.new_task_input)
        add_row.addWidget(self.add_task_button)
        layout.addLayout(add_row)

        return panel

    def _build_detail_panel(self):
        panel = QFrame()
        panel.setObjectName("DetailPanel")
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)

        header_row = QHBoxLayout()
        title = QLabel("详情")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        header_row.addWidget(title)
        header_row.addStretch(1)
        self.detail_close_button = QPushButton("×")
        self.detail_close_button.setFixedSize(24, 24)
        self.detail_close_button.setObjectName("DetailCloseButton")
        self.detail_close_button.clicked.connect(self.clear_selection)
        header_row.addWidget(self.detail_close_button)
        layout.addLayout(header_row)

        self.detail_desc = QLineEdit()
        self.detail_desc.setPlaceholderText("任务内容")
        self._add_field(layout, "任务内容", "fa5s.align-left", self.detail_desc)

        self.detail_status = QComboBox()
        self.detail_status.addItems(["无状态",  "待开始", "等待评审", "进行中", "已完成"])
        self._add_field(layout, "状态", "fa5s.signal", self.detail_status)

        self.detail_type = QComboBox()
        self._populate_type_combo(self.detail_type)
        self._add_field(layout, "类型", "fa5s.tags", self.detail_type)
        type_index = self.detail_type.findData("")
        if type_index >= 0:
            self.detail_type.setCurrentIndex(type_index)

        self.detail_link = QLineEdit()
        self.detail_link.setPlaceholderText("相关链接")
        self._add_field(layout, "链接", "fa5s.link", self.detail_link)

        self.detail_note = QPlainTextEdit()
        self.detail_note.setPlaceholderText("备注或描述")
        self.detail_note.setMinimumHeight(90)
        self._add_field(layout, "描述", "fa5s.sticky-note", self.detail_note)
        self.detail_note.installEventFilter(self)

        self.detail_priority = QComboBox()
        self.detail_priority.addItem("", "")
        for code in ("H", "M", "L"):
            label = f"{code} · {PRIORITY_LABELS[code]}"
            self.detail_priority.addItem(label, code)
        self._add_field(layout, "优先级", "fa5s.flag", self.detail_priority)

        self.detail_due = QDateEdit()
        self.detail_due.setCalendarPopup(True)
        self.detail_due.setDisplayFormat("yyyy-MM-dd")
        self.detail_due.setDate(QDate.currentDate())
        self._add_field(layout, "截止日期", "fa5s.calendar-alt", self.detail_due)

        layout.addStretch(1)

        button_row = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.complete_button = QPushButton("完成任务")
        self.delete_button = QPushButton("删除")
        self.save_button.setIcon(_icon("fa5s.save", color="#ffffff"))
        self.complete_button.setIcon(_icon("fa5s.check-circle", color="#ffffff"))
        self.delete_button.setIcon(_icon("fa5s.trash", color="#ffffff"))
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.complete_button)
        button_row.addWidget(self.delete_button)
        layout.addLayout(button_row)

        self.save_button.clicked.connect(self.save_task)
        self.complete_button.clicked.connect(self.complete_task)
        self.delete_button.clicked.connect(self.delete_task)

        self.detail_desc.editingFinished.connect(self.auto_save_task)
        self.detail_status.currentIndexChanged.connect(self.auto_save_task)
        self.detail_type.currentIndexChanged.connect(self.auto_save_task)
        self.detail_link.editingFinished.connect(self.auto_save_task)
        self.detail_priority.currentIndexChanged.connect(self.auto_save_task)
        self.detail_due.dateChanged.connect(self.auto_save_task)

        layout.addStretch(1)
        self.detail_panel = panel
        panel.setVisible(False)
        return panel

    def set_filter(self, filter_name):
        self.current_filter = filter_name
        self.refresh_tasks()

    def on_filter_clicked(self, filter_name: str):
        if self.current_filter == filter_name and self.expanded_filter == filter_name:
            self.expanded_filter = None
        else:
            self.expanded_filter = filter_name
        self.current_filter = filter_name
        self.current_type = None
        self.refresh_tasks()

    def on_type_clicked(self, filter_name: str, type_value: str):
        self.current_filter = filter_name
        self.current_type = type_value
        self.expanded_filter = filter_name
        self.refresh_tasks()

    def refresh_tasks(self):
        try:
            tasks = self.service.fetch_tasks(self.current_filter)
            self.update_type_submenus(tasks)
            tasks = self.apply_type_filter(tasks)
            tasks = self.sort_tasks(tasks)
            self.tasks_by_uuid = {task.uuid: task for task in tasks if task.uuid}
            selected_uuid = None
            current_item = self.task_list.currentItem()
            if current_item is not None:
                selected_uuid = current_item.data(Qt.ItemDataRole.UserRole)
            self.populate_task_list(tasks)
            if selected_uuid:
                self._restore_selection(selected_uuid)
            if self.current_task_uuid is not None:
                task = self.tasks_by_uuid.get(self.current_task_uuid)
                if task:
                    self.update_complete_button(task)
            if self.task_list.currentItem() is None:
                self.clear_details()
        except Exception as exc:
            self.show_error(str(exc))

    def populate_task_list(self, tasks):
        self.is_populating = True
        self.task_list.clear()
        self.item_widgets = {}
        for task in tasks:
            if not task.uuid:
                continue
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, task.uuid)
            widget = TaskListItemWidget(task, self.on_item_check_changed)
            widget.set_checked(task.task_state == "completed")
            widget.bind_item(item, self.task_list)
            self.item_widgets[task.uuid] = widget
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, widget)
        self.is_populating = False
        self.update_selection_styles()

    def on_sort_changed(self):
        self.refresh_tasks()

    def sort_tasks(self, tasks):
        if not getattr(self, "sort_combo", None):
            return tasks
        mode = self.sort_combo.currentData()
        if self.current_filter == "all":
            tasks = self._order_by_completion(tasks)
        if mode != "priority":
            if mode != "due":
                return tasks
            indexed = list(enumerate(tasks))
            indexed.sort(key=lambda pair: (self._due_rank(pair[1]), pair[0]))
            return [task for _, task in indexed]
        indexed = list(enumerate(tasks))
        indexed.sort(key=lambda pair: (self._priority_rank(pair[1]), pair[0]))
        return [task for _, task in indexed]

    @staticmethod
    def _order_by_completion(tasks):
        indexed = list(enumerate(tasks))
        indexed.sort(key=lambda pair: (pair[1].task_state == "completed", pair[0]))
        return [task for _, task in indexed]

    @staticmethod
    def _priority_rank(task: TaskItem) -> int:
        priority = (task.priority or "L").upper()
        return {"H": 0, "M": 1, "L": 2}.get(priority, 3)

    @staticmethod
    def _due_rank(task: TaskItem) -> tuple[int, int]:
        parsed = parse_due_date(task.due)
        if not parsed:
            return (1, 0)
        return (0, parsed.toJulianDay())

    def apply_search_filter(self):
        text = self.search_input.text().strip().lower()
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            widget = self.task_list.itemWidget(item)
            if not widget:
                continue
            search_target = f"{widget.title_label.text()} {widget.meta_label.text()}".lower()
            item.setHidden(text not in search_target)

    def on_task_selected(self):
        selected = self.task_list.currentItem()
        if not selected:
            self.clear_details()
            return
        task_uuid = selected.data(Qt.ItemDataRole.UserRole)
        self.current_task_uuid = task_uuid
        task = self.tasks_by_uuid.get(task_uuid)
        if not task:
            self.clear_details()
            return
        self.detail_panel.setVisible(True)
        self.is_loading_details = True
        self.detail_desc.setText(task.description)
        self.detail_status.setCurrentText(task.xstatus)
        type_value = normalize_task_type(task.xtype)
        index = self.detail_type.findData(type_value)
        if index >= 0:
            self.detail_type.setCurrentIndex(index)
        else:
            empty_index = self.detail_type.findData("")
            if empty_index >= 0:
                self.detail_type.setCurrentIndex(empty_index)
        self.detail_link.setText(task.link)
        self.detail_note.setPlainText(task.note)
        if task.priority:
            index = self.detail_priority.findData(task.priority)
            self.detail_priority.setCurrentIndex(index)
        else:
            index = self.detail_priority.findData("L")
            self.detail_priority.setCurrentIndex(index)
        parsed_due = parse_due_date(task.due)
        if parsed_due:
            self.detail_due.setDate(parsed_due)
        else:
            self.detail_due.setDate(QDate.currentDate())
        self.update_complete_button(task)
        self.update_selection_styles()
        self.is_loading_details = False

    def add_task(self):
        description = self.new_task_input.text().strip()
        if not description:
            return
        try:
            self.service.add_task(description, "L")
            self.new_task_input.clear()
            self.refresh_tasks()
        except Exception as exc:
            self.show_error(str(exc))

    def save_task(self):
        selected = self.task_list.currentItem()
        if not selected:
            return
        task_uuid = selected.data(Qt.ItemDataRole.UserRole)
        description = self.detail_desc.text().strip()
        note = self.detail_note.toPlainText().strip()
        xstatus = self.detail_status.currentText().strip()
        xtype = self.detail_type.currentData() or ""
        link = self.detail_link.text().strip()
        priority = self.detail_priority.currentData() or "L"
        due = self.detail_due.date().toString("yyyy-MM-dd")

        try:
            self.service.update_task(task_uuid, description, note, xtype, xstatus, link, priority, due)
            self.refresh_tasks()
        except Exception as exc:
            self.show_error(str(exc))

    def auto_save_task(self):
        if self.is_loading_details:
            return
        if not self.detail_panel.isVisible():
            return
        if self.current_task_uuid is None:
            return
        self.save_task()

    def eventFilter(self, obj, event):
        if obj is self.detail_note and event.type() == event.Type.FocusOut:
            self.auto_save_task()
        return super().eventFilter(obj, event)

    def complete_task(self):
        selected = self.task_list.currentItem()
        if not selected:
            return
        task_uuid = selected.data(Qt.ItemDataRole.UserRole)
        task = self.tasks_by_uuid.get(task_uuid)
        if not task:
            return
        try:
            if task.task_state == "completed":
                self.service.reopen_task(task_uuid)
            else:
                self.service.complete_task(task_uuid)
            self.refresh_tasks()
        except Exception as exc:
            self.show_error(str(exc))

    def delete_task(self):
        selected = self.task_list.currentItem()
        if not selected:
            return
        task_uuid = selected.data(Qt.ItemDataRole.UserRole)
        confirm = QMessageBox.question(
            self,
            "删除任务",
            "确定删除该任务？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            self.service.delete_task(task_uuid)
            self.refresh_tasks()
        except Exception as exc:
            self.show_error(str(exc))

    def clear_details(self):
        self.current_task_uuid = None
        self.detail_desc.clear()
        self.detail_status.setCurrentIndex(0)
        type_index = self.detail_type.findData("")
        if type_index >= 0:
            self.detail_type.setCurrentIndex(type_index)
        self.detail_link.clear()
        self.detail_note.clear()
        self.detail_priority.setCurrentIndex(0)
        self.detail_due.setDate(QDate.currentDate())
        self.complete_button.setText("完成")
        self.update_selection_styles()
        self.detail_panel.setVisible(False)

    def show_error(self, message):
        QMessageBox.critical(self, "错误", message)

    def closeEvent(self, event):
        confirm = QMessageBox.question(
            self,
            "退出应用",
            "确定退出吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def on_item_check_changed(self, task_uuid: str | None, checked: bool):
        if self.is_populating:
            return
        if not task_uuid:
            return
        task = self.tasks_by_uuid.get(task_uuid)
        if not task:
            return
        try:
            if checked and task.task_state != "completed":
                self.service.complete_task(task_uuid)
            elif not checked and task.task_state == "completed":
                self.service.reopen_task(task_uuid)
            else:
                return
            self.refresh_tasks()
        except Exception as exc:
            self.show_error(str(exc))

    def update_complete_button(self, task: TaskItem):
        if task.task_state == "completed":
            self.complete_button.setText("撤销完成")
            self.complete_button.setIcon(_icon("fa5s.undo", color="#ffffff"))
        else:
            self.complete_button.setText("完成")
            self.complete_button.setIcon(_icon("fa5s.check-circle", color="#ffffff"))

    def update_selection_styles(self):
        selected_item = self.task_list.currentItem()
        selected_id = None
        if selected_item is not None:
            selected_id = selected_item.data(Qt.ItemDataRole.UserRole)
        for task_uuid, widget in self.item_widgets.items():
            widget.set_selected(task_uuid == selected_id)

    def clear_selection(self):
        self.task_list.clearSelection()
        self.clear_details()

    def export_tasks(self):
        tasks = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            if item.isHidden():
                continue
            task_uuid = item.data(Qt.ItemDataRole.UserRole)
            task = self.tasks_by_uuid.get(task_uuid)
            if task:
                tasks.append(task)
        if not tasks:
            QMessageBox.information(self, "导出", "当前列表没有可导出的任务。")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出任务",
            "tasks.xlsx",
            "Excel Workbook (*.xlsx)",
        )
        if not file_path:
            return
        if not file_path.lower().endswith(".xlsx"):
            file_path += ".xlsx"
        try:
            from openpyxl import Workbook
        except ImportError:
            self.show_error("缺少 openpyxl 依赖，请先安装：pip install openpyxl")
            return
        try:
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Tasks"
            headers = [
                "任务",
                "类型",
                "状态",
                "自定义状态",
                "优先级",
                "截止日期",
                "完成时间",
                "链接",
                "备注",
                "项目",
                "UUID",
            ]
            sheet.append(headers)
            for task in tasks:
                priority_label = PRIORITY_LABELS.get((task.priority or "").upper(), task.priority or "")
                priority_text = ""
                if task.priority:
                    priority_text = f"{task.priority} · {priority_label}" if priority_label else task.priority
                due_value = ""
                parsed_due = parse_due_date(task.due)
                if parsed_due:
                    due_value = parsed_due.toString("yyyy-MM-dd")
                completed_value = self._format_completed_value(task.end)
                sheet.append(
                    [
                        task.description,
                        normalize_task_type(task.xtype),
                        task.task_state,
                        task.xstatus,
                        priority_text,
                        due_value,
                        completed_value,
                        task.link,
                        task.note,
                        task.project,
                        task.uuid,
                    ]
                )
            workbook.save(file_path)
            QMessageBox.information(self, "导出", "导出成功。")
        except Exception as exc:
            self.show_error(str(exc))

    def _add_field(self, layout, label_text, icon_name, widget):
        header_row = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(_icon(icon_name, color="#AACFFF").pixmap(14, 14))
        header_row.addWidget(icon)
        header_row.addWidget(QLabel(label_text))
        header_row.addStretch(1)
        layout.addLayout(header_row)
        layout.addWidget(widget)

    def _restore_selection(self, task_uuid: str):
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == task_uuid:
                self.task_list.setCurrentItem(item)
                return

    def update_type_submenus(self, tasks):
        for filter_name, section in self.sidebar_sections.items():
            container = section["container"]
            layout = section["layout"]
            if filter_name != self.expanded_filter:
                self._clear_layout(layout)
                container.setVisible(False)
                continue
            available_types = self._available_types(tasks)
            self._clear_layout(layout)
            for label, value in available_types:
                button = QPushButton(label)
                button.setObjectName("SidebarSubButton")
                button.clicked.connect(
                    lambda checked=False, name=filter_name, t=value: self.on_type_clicked(name, t)
                )
                layout.addWidget(button)
            container.setVisible(bool(available_types))

    def apply_type_filter(self, tasks):
        if self.current_type is None:
            return tasks
        return [task for task in tasks if normalize_task_type(task.xtype) == self.current_type]

    def _available_types(self, tasks):
        counts = {value: 0 for _, value in self._type_entries()}
        for task in tasks:
            normalized = normalize_task_type(task.xtype)
            if normalized in counts:
                counts[normalized] += 1
        available = []
        for label, value in self._type_entries():
            if counts.get(value, 0) > 0:
                available.append((label, value))
        return available

    def open_settings(self):
        if self.settings_window is None or isdeleted(self.settings_window):
            self.settings_window = SettingsWindow(self.settings_service)
            self.settings_window.types_updated.connect(self.on_types_updated)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def on_types_updated(self, types: list[str]):
        self.type_options = types
        self._populate_type_combo(self.detail_type)
        if self.current_type not in self._type_values():
            self.current_type = None
        self.refresh_tasks()

    def reload_type_options(self):
        self.type_options = self.settings_service.get_task_types()

    def _populate_type_combo(self, combo: QComboBox):
        current_value = combo.currentData() if combo.count() else ""
        combo.blockSignals(True)
        combo.clear()
        for label, value in self._type_entries():
            combo.addItem(label, value)
        combo.blockSignals(False)
        index = combo.findData(current_value)
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            empty_index = combo.findData("")
            if empty_index >= 0:
                combo.setCurrentIndex(empty_index)

    def _type_entries(self):
        entries = [(NONE_TYPE_LABEL, "")]
        for name in self.type_options:
            cleaned = normalize_task_type(name)
            if not cleaned:
                continue
            if cleaned == NONE_TYPE_LABEL:
                continue
            entries.append((cleaned, cleaned))
        return entries

    def _type_values(self):
        return {value for _, value in self._type_entries()}

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    @staticmethod
    def _format_completed_value(end_value: str) -> str:
        parsed = parse_task_datetime(end_value)
        if not parsed:
            return ""
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone()
        return parsed.strftime("%Y-%m-%d %H:%M")

def parse_due_date(value: str) -> QDate | None:
    if not value:
        return None
    patterns = (
        "%Y%m%dT%H%M%SZ",
        "%Y%m%dT%H%M%S",
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
    )
    for pattern in patterns:
        try:
            parsed = datetime.strptime(value, pattern)
            return QDate(parsed.year, parsed.month, parsed.day)
        except ValueError:
            continue
    if len(value) >= 8 and value[:8].isdigit():
        try:
            parsed = datetime.strptime(value[:8], "%Y%m%d")
            return QDate(parsed.year, parsed.month, parsed.day)
        except ValueError:
            return None
    return None


def parse_task_datetime(value: str) -> datetime | None:
    if not value:
        return None
    patterns = (
        "%Y%m%dT%H%M%SZ",
        "%Y%m%dT%H%M%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
    )
    for pattern in patterns:
        try:
            parsed = datetime.strptime(value, pattern)
            if pattern.endswith("Z"):
                return parsed.replace(tzinfo=timezone.utc)
            return parsed
        except ValueError:
            continue
    if len(value) >= 8 and value[:8].isdigit():
        try:
            return datetime.strptime(value[:8], "%Y%m%d")
        except ValueError:
            return None
    return None
