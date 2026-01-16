import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from app.services.settings_service import SettingsService
from app.services.task_service import TaskService
from app.ui.main_window import MainWindow
from app.ui.styles import APP_STYLESHEET


def _ensure_bundled_task_on_path():
    if not getattr(sys, "frozen", False):
        return
    app_dir = os.path.dirname(sys.executable)
    task_path = os.path.join(app_dir, "task")
    if not os.path.exists(task_path):
        return
    current_path = os.environ.get("PATH", "")
    path_entries = current_path.split(os.pathsep) if current_path else []
    if app_dir not in path_entries:
        os.environ["PATH"] = os.pathsep.join([app_dir] + path_entries)


def main():
    _ensure_bundled_task_on_path()
    app = QApplication(sys.argv)
    icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "icon.png"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    app.setStyleSheet(APP_STYLESHEET)
    window = MainWindow(TaskService(), SettingsService())
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
