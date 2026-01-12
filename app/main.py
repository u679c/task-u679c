import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from app.services.task_service import TaskService
from app.ui.main_window import MainWindow
from app.ui.styles import APP_STYLESHEET


def main():
    app = QApplication(sys.argv)
    icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "icon.png"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    app.setStyleSheet(APP_STYLESHEET)
    window = MainWindow(TaskService())
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
