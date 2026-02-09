# SIView.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame, QDialog, QComboBox,
                             QSpinBox, QLineEdit, QTextEdit)
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


class InventoryView(QWidget):
    stock_in_clicked = pyqtSignal()
    stock_out_clicked = pyqtSignal()
    defect_clicked = pyqtSignal()

    def __init__(self, color_scheme=None):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PyesaTrak - Staff Inventory")
        self.setStyleSheet("background-color: transparent;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        bg = QFrame()
        bg.setStyleSheet("background-color: #E8E8E8; border-radius: 15px;")
        bg_layout = QVBoxLayout(bg)
        bg_layout.setContentsMargins(50, 50, 50, 50)

        card = QFrame()
        card.setStyleSheet("background-color: #FFFFFF; border-radius: 15px;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(20)

        lbl = QLabel("Product Details")
        lbl.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        lbl.setStyleSheet("color: black; border: none;")
        card_layout.addWidget(lbl)

        btn_layout = QHBoxLayout()
        self.btn_in = QPushButton("[+] STOCK IN")
        self.btn_out = QPushButton("[-] STOCK OUT")
        self.btn_def = QPushButton("[!] REPORT DEFECT")

        base_style = "QPushButton { color: white; font-weight: bold; border-radius: 8px; padding: 10px; font-family: Arial; }"
        self.btn_in.setStyleSheet(
            base_style + "QPushButton { background-color: #2E7D32; } QPushButton:hover { background-color: #1B5E20; }")
        self.btn_out.setStyleSheet(
            base_style + "QPushButton { background-color: #0076aa; } QPushButton:hover { background-color: #005580; }")
        self.btn_def.setStyleSheet(
            base_style + "QPushButton { background-color: #D32F2F; } QPushButton:hover { background-color: #A52020; }")

        for btn in [self.btn_in, self.btn_out, self.btn_def]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumWidth(140)
            btn_layout.addWidget(btn)

        btn_layout.addStretch()
        card_layout.addLayout(btn_layout)

        self.btn_in.clicked.connect(self.stock_in_clicked.emit)
        self.btn_out.clicked.connect(self.stock_out_clicked.emit)
        self.btn_def.clicked.connect(self.defect_clicked.emit)

        self.product_table = ToggleTableWidget()
        self.product_table.setColumnCount(6)
        self.product_table.setHorizontalHeaderLabels(
            ["Product ID", "Product Name", "Brand", "Model", "Stock", "Status"])
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.product_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.product_table.setShowGrid(False)
        self.product_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.product_table.cellDoubleClicked.connect(self.handle_cell_double_click)

        self.product_table.setStyleSheet("""
            QTableWidget { background-color: transparent; border: none; color: black; font-family: Arial; font-size: 13px; outline: 0; }
            QHeaderView::section { background-color: #000000; color: white; padding: 12px; font-weight: bold; border: none; font-family: Arial; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #F0F0F0; outline: none; border: none; }
            QTableWidget::item:selected { background-color: #B3D9FF; color: black; border: none; outline: none; }
            QTableWidget::item:focus { border: none; outline: none; }
        """)

        card_layout.addWidget(self.product_table)
        bg_layout.addWidget(card)
        main_layout.addWidget(bg)

    def handle_cell_double_click(self, row, column):
        self.product_table.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)

    def load_table(self, products):
        self.product_table.setColumnCount(6)
        self.product_table.setHorizontalHeaderLabels(
            ["Product ID", "Product Name", "Brand", "Model", "Stock", "Status"])
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.product_table.setRowCount(len(products))
        for row, p in enumerate(products):
            self._fill_common_rows(row, p)
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
        self.product_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        self.product_table.setRowCount(len(products))
        for row, p in enumerate(products):
            self._fill_common_rows(row, p)
            status_item = self.make_item(p['status'], True)
            self.product_table.setItem(row, 5, status_item)

            reason_item = self.make_item(p.get('defect_reason', 'N/A'))
            reason_item.setForeground(QColor("#D32F2F"))
            self.product_table.setItem(row, 6, reason_item)

    def _fill_common_rows(self, row, p):
        self.product_table.setItem(row, 0, self.make_item(str(p['product_id']), True))
        self.product_table.setItem(row, 1, self.make_item(p['product_name']))
        self.product_table.setItem(row, 2, self.make_item(p.get('brand', '')))
        self.product_table.setItem(row, 3, self.make_item(p.get('model', '')))
        stock_qty = int(p['stock_quantity'])
        stock_item = self.make_item(str(stock_qty), True)
        if stock_qty <= 10:
            stock_item.setForeground(QColor("#D32F2F"))
            stock_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.product_table.setItem(row, 4, stock_item)

    def make_item(self, text, center=False):
        item = QTableWidgetItem(text)
        if center: item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def get_selected_product(self):
        r = self.product_table.currentRow()
        if r >= 0:
            return {
                'product_id': int(self.product_table.item(r, 0).text()),
                'product_name': self.product_table.item(r, 1).text(),
                'brand': self.product_table.item(r, 2).text(),
                'model': self.product_table.item(r, 3).text(),
                'stock_quantity': int(self.product_table.item(r, 4).text())
            }
        return None


# --- MISSING DIALOG CLASSES ADDED BELOW ---

class BaseTransactionDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QDialog { background-color: white; }
            QLabel { color: black; font-weight: bold; margin-bottom: 2px; }
            QLabel#Header { color: #0076aa; font-size: 20px; margin-bottom: 15px; }
            QLineEdit, QSpinBox, QTextEdit, QComboBox { 
                border: 1px solid #ccc; border-radius: 8px; padding: 8px; color: black; background-color: white;
            }
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


class StockInDialog(BaseTransactionDialog):
    def __init__(self, product_list, parent=None):
        super().__init__("Stock In", parent)
        self.selected_product_id = None
        self.product_combo = QComboBox()
        self.product_combo.setEditable(True)
        for p in product_list:
            display = f"{p['product_name']} ({p.get('brand', '')})"
            self.product_combo.addItem(display, userData=p)
        self.product_combo.currentIndexChanged.connect(self.update_stock_info)
        self.add_centered_field("Select Product", self.product_combo)

        self.stock_info_lbl = QLabel("Current Stock: -")
        self.stock_info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stock_info_lbl.setStyleSheet("color: #555; font-weight: normal;")
        self.layout.addWidget(self.stock_info_lbl)
        self.layout.addSpacing(10)

        self.qty = QSpinBox()
        self.qty.setRange(1, 10000)
        self.qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qty.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.add_centered_field("Add Quantity", self.qty)

        self.rem = QLineEdit()
        self.rem.setPlaceholderText("Remarks...")
        self.rem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_centered_field("Remarks", self.rem)
        self.add_buttons("#2E7D32")
        self.update_stock_info()

    def update_stock_info(self):
        index = self.product_combo.currentIndex()
        if index >= 0:
            data = self.product_combo.itemData(index)
            self.stock_info_lbl.setText(f"Current Stock: {data['stock_quantity']}")
            self.selected_product_id = data['product_id']

    def get_data(self):
        return self.selected_product_id, self.qty.value(), self.rem.text()


class StockOutDialog(BaseTransactionDialog):
    def __init__(self, product_list, parent=None):
        super().__init__("Stock Out", parent)
        self.selected_product_id = None
        self.product_combo = QComboBox()
        self.product_combo.setEditable(True)
        for p in product_list:
            display = f"{p['product_name']} ({p.get('brand', '')})"
            self.product_combo.addItem(display, userData=p)
        self.product_combo.currentIndexChanged.connect(self.update_stock_info)
        self.add_centered_field("Select Product", self.product_combo)

        self.stock_info_lbl = QLabel("Current Stock: -")
        self.stock_info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stock_info_lbl.setStyleSheet("color: #555; font-weight: normal;")
        self.layout.addWidget(self.stock_info_lbl)
        self.layout.addSpacing(10)

        self.qty = QSpinBox()
        self.qty.setRange(1, 1)
        self.qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qty.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.add_centered_field("Remove Quantity", self.qty)

        self.reason = QLineEdit()
        self.reason.setPlaceholderText("Reason...")
        self.reason.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_centered_field("Reason", self.reason)
        self.add_buttons("#0076aa")
        self.update_stock_info()

    def update_stock_info(self):
        index = self.product_combo.currentIndex()
        if index >= 0:
            data = self.product_combo.itemData(index)
            stock = data['stock_quantity']
            self.stock_info_lbl.setText(f"Current Stock: {stock}")
            self.selected_product_id = data['product_id']
            if stock > 0:
                self.qty.setRange(1, stock)
                self.qty.setEnabled(True)
            else:
                self.qty.setRange(0, 0)
                self.qty.setEnabled(False)

    def get_data(self):
        return self.selected_product_id, self.qty.value(), self.reason.text()


class DefectDialog(BaseTransactionDialog):
    def __init__(self, product_list, parent=None):
        super().__init__("Report Defect", parent)
        self.selected_product_id = None
        self.product_combo = QComboBox()
        self.product_combo.setEditable(True)
        for p in product_list:
            display = f"{p['product_name']} ({p.get('brand', '')})"
            self.product_combo.addItem(display, userData=p)
        self.product_combo.currentIndexChanged.connect(self.update_stock_info)
        self.add_centered_field("Select Product", self.product_combo)

        self.stock_info_lbl = QLabel("Current Stock: -")
        self.stock_info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stock_info_lbl.setStyleSheet("color: #555; font-weight: normal;")
        self.layout.addWidget(self.stock_info_lbl)
        self.layout.addSpacing(10)

        self.qty = QSpinBox()
        self.qty.setRange(1, 1)
        self.qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qty.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.add_centered_field("Defective Qty", self.qty)

        self.type = QComboBox()
        self.type.addItems(["Damaged", "Expired", "Missing Parts", "Other"])
        self.add_centered_field("Defect Type", self.type)

        self.desc = QTextEdit()
        self.desc.setFixedHeight(60)
        self.add_centered_field("Description", self.desc)
        self.add_buttons("#D32F2F")
        self.update_stock_info()

    def update_stock_info(self):
        index = self.product_combo.currentIndex()
        if index >= 0:
            data = self.product_combo.itemData(index)
            stock = data['stock_quantity']
            self.stock_info_lbl.setText(f"Current Stock: {stock}")
            self.selected_product_id = data['product_id']
            if stock > 0:
                self.qty.setRange(1, stock)
                self.qty.setEnabled(True)
            else:
                self.qty.setRange(0, 0)
                self.qty.setEnabled(False)

    def get_data(self):
        return self.selected_product_id, self.qty.value(), f"{self.type.currentText()} - {self.desc.toPlainText()}"