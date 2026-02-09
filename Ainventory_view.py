# Ainventory_view.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView, QFrame, QDialog,
                             QFormLayout, QSpinBox, QLineEdit, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor


class ToggleTableWidget(QTableWidget):
    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid():
            item = self.item(index.row(), 0)
            if item and item.isSelected():
                self.clearSelection()
                self.setCurrentItem(None)
                return
        super().mousePressEvent(event)


class ProductDetailsView(QWidget):
    add_product_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PyesaTrak - Admin Inventory")
        self.setStyleSheet("background-color: transparent;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Background
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
        lbl = QLabel("Inventory Management (Admin)")
        lbl.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        lbl.setStyleSheet("color: black; border: none;")
        card_layout.addWidget(lbl)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("[+] NEW PRODUCT")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setMinimumWidth(160)
        self.btn_add.setStyleSheet("""
            QPushButton { background-color: #008B8B; color: white; font-weight: bold; border-radius: 8px; padding: 10px; font-family: Arial; } 
            QPushButton:hover { background-color: #006666; }
        """)
        self.btn_add.clicked.connect(self.add_product_clicked.emit)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addStretch()
        card_layout.addLayout(btn_layout)

        # Table
        self.product_table = ToggleTableWidget()
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.product_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.product_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.product_table.setShowGrid(False)
        self.product_table.setFrameShape(QFrame.Shape.NoFrame)
        self.product_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.product_table.setStyleSheet("""
            QTableWidget { background-color: transparent; border: none; color: black; font-family: Arial; font-size: 13px; outline: 0; }
            QHeaderView::section { background-color: #000000; color: white; padding: 12px; font-weight: bold; border: none; font-family: Arial; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #F0F0F0; outline: none; border: none; }
            QTableWidget::item:selected { background-color: #B3D9FF; color: black; border: none; outline: none; }
            QTableWidget::item:focus { border: none; outline: none; }
        """)

        # Connect Double Click to Expand Column
        self.product_table.cellDoubleClicked.connect(self.handle_cell_double_click)

        card_layout.addWidget(self.product_table)
        bg_layout.addWidget(card)
        main_layout.addWidget(bg)

    def handle_cell_double_click(self, row, column):
        self.product_table.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)

    def load_products(self, products):
        """Loads standard inventory view (6 columns)"""
        self.product_table.setColumnCount(6)
        self.product_table.setHorizontalHeaderLabels(
            ["Product ID", "Product Name", "Brand", "Model", "Stock", "Status"])
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.product_table.setRowCount(len(products))
        for row, p in enumerate(products):
            self._fill_common_rows(row, p)
            # Status
            status = p['status']
            status_item = self.make_item(status, True)
            if status == 'Available':
                status_item.setForeground(QColor("#2E7D32"))
            elif status == 'Low Stock':
                status_item.setForeground(QColor("#FF9800"))
            elif status == 'Out of Stock':
                status_item.setForeground(QColor("#D32F2F"))
            self.product_table.setItem(row, 5, status_item)

    def load_defective_table(self, products):
        """Loads defective items view with REASON column (7 columns)"""
        self.product_table.setColumnCount(7)
        self.product_table.setHorizontalHeaderLabels(
            ["Product ID", "Product Name", "Brand", "Model", "Stock", "Status", "Defect Reason"])
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Give reason column more space
        self.product_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        self.product_table.setRowCount(len(products))
        for row, p in enumerate(products):
            self._fill_common_rows(row, p)

            # Status (Force Red for Defective View)
            status_item = self.make_item(p['status'], True)
            self.product_table.setItem(row, 5, status_item)

            # Defect Reason
            reason_item = self.make_item(p.get('defect_reason', 'N/A'))
            reason_item.setForeground(QColor("#D32F2F"))  # Red text for reason
            self.product_table.setItem(row, 6, reason_item)

    def _fill_common_rows(self, row, p):
        """Helper to fill first 5 columns"""
        self.product_table.setItem(row, 0, self.make_item(str(p['product_id']), True))
        self.product_table.setItem(row, 1, self.make_item(p['product_name']))
        self.product_table.setItem(row, 2, self.make_item(p.get('brand', '')))
        self.product_table.setItem(row, 3, self.make_item(p.get('model', '')))
        stock_item = self.make_item(str(p['stock_quantity']), True)
        if int(p['stock_quantity']) <= 10:
            stock_item.setForeground(QColor("#D32F2F"))
            stock_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.product_table.setItem(row, 4, stock_item)

    def make_item(self, text, center=False):
        item = QTableWidgetItem(text)
        if center: item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item


# --- ADMIN DIALOG ONLY ---
class BaseTransactionDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 480)
        self.setStyleSheet("""
            QDialog { background-color: white; }
            QLabel { color: black; font-weight: bold; margin-bottom: 2px; }
            QLabel#Header { color: #0076aa; font-size: 20px; margin-bottom: 15px; }
            QLineEdit, QSpinBox, QComboBox { border: 1px solid #ccc; border-radius: 8px; padding: 8px; color: black; background-color: white; }
            QPushButton { border-radius: 8px; padding: 8px 20px; font-weight: bold; }
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 30, 40, 30)
        self.layout.setSpacing(10)
        self.title_lbl = QLabel(title)
        self.title_lbl.setObjectName("Header")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_lbl)

    def add_centered_field(self, label_text, widget):
        lbl = QLabel(label_text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(lbl)
        self.layout.addWidget(widget)
        self.layout.addSpacing(10)

    def add_buttons(self, color):
        self.layout.addStretch()
        h = QHBoxLayout()
        h.setSpacing(15)
        cancel = QPushButton("Cancel")
        cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel.setStyleSheet("background-color: #777; color: white;")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Confirm")
        save.setCursor(Qt.CursorShape.PointingHandCursor)
        save.setStyleSheet(f"background-color: {color}; color: white;")
        save.clicked.connect(self.accept)
        h.addWidget(cancel)
        h.addWidget(save)
        self.layout.addLayout(h)


class AddProductDialog(BaseTransactionDialog):
    def __init__(self, parent=None):
        super().__init__("Add New Product", parent)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter product name")
        self.name_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_centered_field("Product Name", self.name_edit)
        self.brand_edit = QLineEdit()
        self.brand_edit.setPlaceholderText("Enter brand")
        self.brand_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_centered_field("Brand", self.brand_edit)
        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("Enter model")
        self.model_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_centered_field("Model", self.model_edit)
        self.stock_spin = QSpinBox()
        self.stock_spin.setRange(0, 10000)
        self.stock_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stock_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.add_centered_field("Initial Stock Quantity", self.stock_spin)
        self.add_buttons("#008B8B")

    def get_data(self):
        qty = self.stock_spin.value()
        status = "Available" if qty > 0 else "Out of Stock"
        return {
            'product_name': self.name_edit.text(),
            'brand': self.brand_edit.text(),
            'model': self.model_edit.text(),
            'stock_quantity': qty,
            'status': status,
            'description': ""
        }