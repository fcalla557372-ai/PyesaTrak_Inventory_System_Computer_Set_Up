# AreportsView.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView, QFrame, QComboBox,
                             QDateEdit, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor


class ReportsView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Reports & Analytics")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Header
        title = QLabel("Reports & Analytics")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: black; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Controls Container
        controls_frame = QFrame()
        controls_frame.setStyleSheet("background-color: white; border-radius: 10px;")
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setSpacing(15)

        # Filter Options
        filter_layout = QHBoxLayout()

        input_style = """
            padding: 5px; 
            border: 1px solid #ccc; 
            border-radius: 5px; 
            color: black; 
            background-color: white;
        """

        lbl_type = QLabel("Type:")
        lbl_type.setStyleSheet("color: black; font-weight: bold;")
        filter_layout.addWidget(lbl_type)

        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["Inventory Status", "Stock Movement", "Defects Report", "User Activity"])
        self.report_type_combo.setFixedWidth(160)
        self.report_type_combo.setStyleSheet(input_style)
        filter_layout.addWidget(self.report_type_combo)

        lbl_from = QLabel("From:")
        lbl_from.setStyleSheet("color: black; font-weight: bold;")
        filter_layout.addWidget(lbl_from)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setStyleSheet(input_style)
        filter_layout.addWidget(self.start_date)

        lbl_to = QLabel("To:")
        lbl_to.setStyleSheet("color: black; font-weight: bold;")
        filter_layout.addWidget(lbl_to)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setStyleSheet(input_style)
        filter_layout.addWidget(self.end_date)

        self.generate_btn = QPushButton("Generate Report")
        self.generate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.generate_btn.setStyleSheet("""
            QPushButton { background-color: #0076aa; color: white; font-weight: bold; padding: 8px 15px; border-radius: 5px; }
            QPushButton:hover { background-color: #005580; }
        """)
        filter_layout.addWidget(self.generate_btn)

        filter_layout.addStretch()
        controls_layout.addLayout(filter_layout)

        # Table Area
        self.report_table = QTableWidget()
        self.report_table.setShowGrid(False)
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.report_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.report_table.setStyleSheet("""
            QTableWidget { 
                border: 1px solid #eee; 
                background-color: white; 
                color: black; 
                gridline-color: #eee;
            }
            QTableWidget::item {
                padding: 5px;
                color: black;
            }
            QHeaderView::section { 
                background-color: #000; 
                color: white; 
                padding: 8px; 
                font-weight: bold; 
                border: none;
            }
        """)

        controls_layout.addWidget(self.report_table)

        # Bottom Buttons
        actions_layout = QHBoxLayout()
        self.export_btn = QPushButton("Export to PDF")
        self.export_btn.setEnabled(False)
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_btn.setStyleSheet("""
            QPushButton { background-color: #ccc; padding: 8px; border-radius: 5px; color: white; font-weight: bold; }
        """)

        actions_layout.addStretch()
        actions_layout.addWidget(self.export_btn)

        controls_layout.addLayout(actions_layout)
        main_layout.addWidget(controls_frame)

    def load_reports(self, data):
        self.report_table.clear()
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels(["ID", "Report Name", "Type", "Created By", "Date"])
        self.report_table.setRowCount(len(data))
        for r, row in enumerate(data):
            self.report_table.setItem(r, 0, QTableWidgetItem(str(row['report_id'])))
            self.report_table.setItem(r, 1, QTableWidgetItem(str(row['report_name'])))
            self.report_table.setItem(r, 2, QTableWidgetItem(str(row['report_type'])))
            self.report_table.setItem(r, 3, QTableWidgetItem(str(row['created_by'])))
            self.report_table.setItem(r, 4, QTableWidgetItem(str(row['created_at'])))

    def display_generated_data(self, data):
        if not data:
            self.report_table.setRowCount(0)
            return

        self.export_btn.setEnabled(True)
        self.export_btn.setStyleSheet("""
            QPushButton { background-color: #D32F2F; padding: 8px 20px; border-radius: 5px; color: white; font-weight: bold; }
            QPushButton:hover { background-color: #B71C1C; }
        """)

        columns = list(data[0].keys())
        self.report_table.clear()
        self.report_table.setColumnCount(len(columns))
        headers = [c.replace('_', ' ').title() for c in columns]
        self.report_table.setHorizontalHeaderLabels(headers)

        self.report_table.setRowCount(len(data))
        for r, row in enumerate(data):
            for c, key in enumerate(columns):
                val = row[key]

                # --- FIX: Handle Missing Status Data ---
                if key == 'status' and not val:
                    # Infer status from quantity if status is missing in DB
                    qty = row.get('stock_quantity')
                    if qty is not None:
                        val = "Available" if int(qty) > 0 else "Out of Stock"
                    else:
                        val = "-"  # Fallback if no quantity found

                item = QTableWidgetItem(str(val))
                item.setForeground(QColor("black"))
                self.report_table.setItem(r, c, item)

    def set_actions_enabled(self, enabled):
        pass