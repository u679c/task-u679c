APP_STYLESHEET = """
QMainWindow {
    background-color: #eaf2fb;
}
QFrame#Sidebar {
    background: #f5f3f2;
    border: none;
    border-right: 1px solid #e2e2e2;
    border-radius: 0px;
}
QFrame#ListPanel {
    background: #eef6ff;
    border: none;
}
QFrame#DetailPanel {
    background: #f7fbff;
    border: none;
    border-left: 1px solid #dde8f7;
}
QLabel {
    color: #1a1d24;
}
QLabel#HeaderTitle {
    color: #2b5c9f;
}
QLineEdit, QComboBox, QDateEdit {
    background: #ffffff;
    border: 1px solid #d6e2f3;
    border-radius: 10px;
    padding: 7px 10px;
}
QComboBox::drop-down, QDateEdit::drop-down {
    border: none;
    width: 28px;
    background: transparent;
}
QComboBox QAbstractItemView {
    color: #000000;
    selection-color: #6199BA;
    outline: 0;
}

QLineEdit#SearchInput {
    background: #f2f2f2;
}
QPushButton {
    background-color: #3b82f6;
    color: #ffffff;
    border-radius: 10px;
    padding: 7px 12px;
}
QPushButton:hover {
    background-color: #2563eb;
}
QPushButton#SidebarButton {
    background: transparent;
    color: #2a2a2a;
    text-align: left;
    padding: 8px 10px;
    border-radius: 8px;
}
QPushButton#SidebarButton:hover {
    background: #e9e7e6;
}
QPushButton#DetailCloseButton {
    background: transparent;
    border: none;
    color: #6b7280;
    font-size: 16px;
    padding: 0;
}
QPushButton#DetailCloseButton:hover {
    color: #111827;
}
QListWidget {
    background: #ffffff;
    border: 1px solid #dbe6f6;
    border-radius: 12px;
    padding: 6px;
}
QListWidget::item {
    # background: transparent;
    border: 1px solid #edf2fa;
    border-radius: 10px;
    padding: 0px;
    height: 60px;
    margin-bottom: 0px;
}
QListWidget::item:selected {
    background: #DBEAFE;
    border: 1px solid #bfdbfe;
}
QListWidget::item:selected:active {
    background: #DBEAFE;
}
QListWidget::item:selected:!active {
    background: #DBEAFE;
}
QMenuBar {
    background: #eaf2fb;
}
QSplitter::handle {
    background: #dbe6f6;
}
QSplitter::handle:horizontal {
    width: 6px;
}
"""
