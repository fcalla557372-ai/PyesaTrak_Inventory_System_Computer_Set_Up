# ManageUsersView.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView, QFrame, QComboBox,
                             QLineEdit, QDialog, QFormLayout, QDialogButtonBox,
                             QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor


class ManageUsersView(QWidget):
    # Signals
    add_user_clicked = pyqtSignal()
    edit_user_clicked = pyqtSignal(int)
    delete_user_clicked = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Manage Users")
        self.setStyleSheet("background-color: transparent;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Background Container
        bg = QFrame()
        bg.setStyleSheet("background-color: #E8E8E8; border-radius: 15px;")
        bg_layout = QVBoxLayout(bg)
        bg_layout.setContentsMargins(50, 50, 50, 50)

        # White Card
        card = QFrame()
        card.setStyleSheet("background-color: #FFFFFF; border-radius: 15px;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(20)

        # Header
        header = QLabel("Manage Users")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: black; border: none;")
        card_layout.addWidget(header)

        # Controls
        controls_layout = QHBoxLayout()

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setFixedWidth(200)
        self.search_input.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 5px; color: black;")
        controls_layout.addWidget(QLabel("Search:"))
        controls_layout.addWidget(self.search_input)

        # Filters
        self.role_combo = QComboBox()
        self.role_combo.addItems(["All", "Admin", "Staff"])
        self.role_combo.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 5px; color: black;")

        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Active", "Inactive"])
        self.status_combo.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 5px; color: black;")

        controls_layout.addWidget(QLabel("Role:"))
        controls_layout.addWidget(self.role_combo)
        controls_layout.addWidget(QLabel("Status:"))
        controls_layout.addWidget(self.status_combo)
        controls_layout.addStretch()

        # Add Button
        self.btn_add = QPushButton("+ Add New User")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(
            "background-color: #00bfff; color: white; font-weight: bold; padding: 8px 15px; border-radius: 5px;")
        self.btn_add.clicked.connect(self.add_user_clicked.emit)
        controls_layout.addWidget(self.btn_add)

        card_layout.addLayout(controls_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Username", "Role", "Status", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.setFrameShape(QFrame.Shape.NoFrame)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.table.setStyleSheet("""
            QTableWidget { border: none; background-color: white; color: black; font-size: 13px; }
            QHeaderView::section { background-color: #000; color: white; padding: 10px; font-weight: bold; border: none; }
            QTableWidget::item { padding: 5px; border-bottom: 1px solid #f0f0f0; }
        """)

        card_layout.addWidget(self.table)
        bg_layout.addWidget(card)
        main_layout.addWidget(bg)

    def load_data(self, users):
        """Refreshes the table with user list"""
        self.table.setRowCount(0)  # Clear existing rows

        for row_idx, user in enumerate(users):
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 50)

            # 0: ID
            self.table.setItem(row_idx, 0, self.make_item(str(user['user_id']), True))

            # 1: Name (Using userFname / userLname)
            full_name = f"{user.get('userFname', '')} {user.get('userLname', '')}"
            self.table.setItem(row_idx, 1, self.make_item(full_name))

            # 2: Username
            self.table.setItem(row_idx, 2, self.make_item(user['username']))

            # 3: Role
            self.table.setItem(row_idx, 3, self.make_item(user['role'], True))

            # 4: Status
            status_item = self.make_item(user['status'], True)
            if user['status'] == 'Active':
                status_item.setForeground(QColor("green"))
            else:
                status_item.setForeground(QColor("red"))
            self.table.setItem(row_idx, 4, status_item)

            # 5: Actions
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(5)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_edit = QPushButton("Edit")
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.setFixedSize(60, 30)
            btn_edit.setStyleSheet("background-color: #00bfff; color: white; border-radius: 4px; font-weight: bold;")
            btn_edit.clicked.connect(lambda checked, u=user['user_id']: self.edit_user_clicked.emit(u))

            btn_delete = QPushButton("Delete")
            btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_delete.setFixedSize(60, 30)
            btn_delete.setStyleSheet("background-color: #D32F2F; color: white; border-radius: 4px; font-weight: bold;")
            btn_delete.clicked.connect(lambda checked, u=user['user_id']: self.delete_user_clicked.emit(u))

            layout.addWidget(btn_edit)
            layout.addWidget(btn_delete)
            self.table.setCellWidget(row_idx, 5, container)

    def make_item(self, text, center=False):
        item = QTableWidgetItem(str(text))
        item.setForeground(QColor("black"))
        if center: item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item


# --- DIALOG FOR ADD/EDIT USER ---
class UserFormDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.setWindowTitle("User Details")
        self.setFixedSize(400, 500)

        self.setStyleSheet("""
            QDialog { background-color: white; }
            QLabel { font-weight: bold; color: black; font-size: 12px; }
            QLineEdit, QComboBox { 
                padding: 8px; 
                border: 1px solid #ccc; 
                border-radius: 5px; 
                color: black; 
                background-color: white;
            }
        """)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        header = QLabel("Add User" if not user_data else "Edit User")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #0076aa; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        self.fname_edit = QLineEdit()
        form_layout.addRow("First Name:", self.fname_edit)

        self.lname_edit = QLineEdit()
        form_layout.addRow("Last Name:", self.lname_edit)

        self.user_edit = QLineEdit()
        form_layout.addRow("Username:", self.user_edit)

        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_edit.setPlaceholderText("Leave blank to keep current" if user_data else "")
        form_layout.addRow("Password:", self.pass_edit)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["Staff", "Admin"])
        form_layout.addRow("Role:", self.role_combo)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive"])
        form_layout.addRow("Status:", self.status_combo)

        layout.addLayout(form_layout)
        layout.addStretch()

        # Pre-fill data if editing (Using userFname schema)
        if user_data:
            self.fname_edit.setText(user_data.get('userFname', ''))
            self.lname_edit.setText(user_data.get('userLname', ''))
            self.user_edit.setText(user_data.get('username', ''))
            self.role_combo.setCurrentText(user_data.get('role', 'Staff'))
            self.status_combo.setCurrentText(user_data.get('status', 'Active'))

        # Buttons
        btns = QHBoxLayout()
        save_btn = QPushButton("Save User")
        save_btn.setFixedHeight(40)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("background-color: #0076aa; color: white; border-radius: 5px; font-weight: bold;")
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("background-color: gray; color: white; border-radius: 5px; font-weight: bold;")
        cancel_btn.clicked.connect(self.reject)

        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        layout.addLayout(btns)

    def get_data(self):
        # Mapping inputs to your database schema
        return {
            'userFname': self.fname_edit.text(),
            'userLname': self.lname_edit.text(),
            'username': self.user_edit.text(),
            'password': self.pass_edit.text(),
            'role': self.role_combo.currentText(),
            'status': self.status_combo.currentText()
        }