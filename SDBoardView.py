# SDBoardView.py - FINAL CLEAN VERSION (No Borders)
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QStackedWidget, QFrame, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView,
                             QSizePolicy, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QColor

import matplotlib

matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from SIView import InventoryView


class FlowChart(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#FFFFFF')
        super().__init__(self.fig)
        self.axes = self.fig.add_subplot(111)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.update_chart(0, 0)

    def update_chart(self, stock_in, stock_out):
        self.axes.clear()
        categories = ['Stock In', 'Stock Out']
        values = [stock_in, stock_out]
        colors = ['#0076aa', '#D32F2F']
        bars = self.axes.bar(categories, values, color=colors, width=0.5)

        self.axes.set_facecolor('#FFFFFF')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['left'].set_visible(False)
        self.axes.spines['bottom'].set_color('#E0E0E0')
        self.axes.spines['bottom'].set_linewidth(1)

        self.axes.tick_params(axis='x', colors='#666666', labelsize=11)
        self.axes.tick_params(axis='y', length=0)
        self.axes.set_yticks([])

        for bar in bars:
            height = bar.get_height()
            self.axes.text(
                bar.get_x() + bar.get_width() / 2.,
                height + max(values) * 0.02 if max(values) > 0 else 1,
                f'{int(height)}',
                ha='center', va='bottom',
                fontsize=14, fontweight='bold',
                color='#333333'
            )
        self.draw()


class StaffDashboardView(QWidget):
    dashboard_clicked = pyqtSignal()
    product_stock_clicked = pyqtSignal()
    sign_out_clicked = pyqtSignal()
    refresh_analytics_clicked = pyqtSignal()

    kpi_low_stock_clicked = pyqtSignal()
    kpi_out_of_stock_clicked = pyqtSignal()
    kpi_defective_clicked = pyqtSignal()

    activity_double_clicked = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.COLORS = {
            'primary': '#0076aa',
            'secondary': '#4FC3F7',
            'black': '#1A1A1A',
            'bg_gray': '#F5F5F5',
            'white': '#FFFFFF',
            'danger': '#D32F2F',
            'warning': '#F57C00',
            'success': '#388E3C',
            'purple': '#7B1FA2',
            'text_primary': '#212121',
            'text_secondary': '#757575',
            'border': '#E0E0E0'
        }

        self.header_font = QFont("Segoe UI", 26, QFont.Weight.Normal)
        self.sub_header_font = QFont("Segoe UI", 14, QFont.Weight.DemiBold)
        self.kpi_value_font = QFont("Segoe UI", 36, QFont.Weight.Bold)
        self.kpi_label_font = QFont("Segoe UI", 11, QFont.Weight.Normal)
        self.btn_font = QFont("Segoe UI", 11, QFont.Weight.DemiBold)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PyesaTrak - Staff Dashboard")
        self.setFixedSize(1280, 760)
        self.setStyleSheet(f"background-color: {self.COLORS['bg_gray']}; font-family: 'Segoe UI', Arial;")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # SIDEBAR
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"background-color: {self.COLORS['black']}; border: none;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 40, 20, 40)
        sidebar_layout.setSpacing(8)

        app_title = QLabel("PyesaTrak")
        app_title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        app_title.setStyleSheet(f"color: {self.COLORS['white']}; margin-bottom: 30px; border: none;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(app_title)

        self.dashboard_btn = self.create_nav_btn("Dashboard")
        self.product_stock_btn = self.create_nav_btn("Inventory")

        self.dashboard_btn.clicked.connect(self.dashboard_clicked.emit)
        self.product_stock_btn.clicked.connect(self.product_stock_clicked.emit)

        sidebar_layout.addWidget(self.dashboard_btn)
        sidebar_layout.addWidget(self.product_stock_btn)
        sidebar_layout.addStretch()

        self.sign_out_btn = QPushButton("Sign Out")
        self.sign_out_btn.setFixedHeight(44)
        self.sign_out_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sign_out_btn.setFont(self.btn_font)
        self.sign_out_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #2A2A2A; 
                color: {self.COLORS['white']}; 
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{ 
                background-color: {self.COLORS['danger']}; 
            }}
        """)
        self.sign_out_btn.clicked.connect(self.sign_out_clicked.emit)
        sidebar_layout.addWidget(self.sign_out_btn)

        main_layout.addWidget(sidebar)

        # CONTENT
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(30, 30, 30, 30)

        self.stacked_widget = QStackedWidget()
        self.dashboard_page = self.create_dashboard_page()
        self.products_page = InventoryView(self.COLORS)

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.products_page)

        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(content_area)

        self.update_button_styles(self.dashboard_btn)

    def create_nav_btn(self, text):
        btn = QPushButton(text)
        btn.setFixedHeight(44)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFont(self.btn_font)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: #9E9E9E;
                text-align: left;
                padding-left: 16px;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{ 
                background-color: #2A2A2A;
                color: {self.COLORS['white']}; 
            }}
        """)
        return btn

    def update_button_styles(self, active_btn):
        buttons = [self.dashboard_btn, self.product_stock_btn]
        for btn in buttons:
            if btn == active_btn:
                btn.setStyleSheet(f"""
                    background-color: {self.COLORS['primary']};
                    color: {self.COLORS['white']};
                    text-align: left;
                    padding-left: 16px;
                    border: none;
                    border-radius: 6px;
                """)
            else:
                btn.setStyleSheet(f"""
                    background-color: transparent;
                    color: #9E9E9E;
                    text-align: left;
                    padding-left: 16px;
                    border: none;
                    border-radius: 6px;
                """)

    def show_dashboard_page(self):
        self.stacked_widget.setCurrentIndex(0)
        self.update_button_styles(self.dashboard_btn)

    def show_product_page(self):
        self.stacked_widget.setCurrentIndex(1)
        self.update_button_styles(self.product_stock_btn)

    def create_dashboard_page(self):
        """Dashboard with borderless design"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        # Header
        header_row = QHBoxLayout()
        title = QLabel("Dashboard Overview")
        title.setFont(self.header_font)
        title.setStyleSheet(f"color: {self.COLORS['text_primary']}; border: none;")

        ref_btn = QPushButton("↻ Refresh")
        ref_btn.setFixedSize(110, 38)
        ref_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ref_btn.setFont(self.btn_font)
        ref_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COLORS['white']}; 
                color: {self.COLORS['text_primary']}; 
                border: 1px solid {self.COLORS['border']};
                border-radius: 6px;
            }}
            QPushButton:hover {{ 
                background-color: {self.COLORS['primary']};
                color: {self.COLORS['white']};
                border: 1px solid {self.COLORS['primary']};
            }}
        """)
        ref_btn.clicked.connect(self.refresh_analytics_clicked.emit)

        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(ref_btn)
        layout.addLayout(header_row)

        # KPI Cards - BORDERLESS
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(20)

        self.card_prod, self.lbl_prod = self.create_borderless_kpi(
            "Total Products", "0", "All items in inventory",
            self.COLORS['text_secondary'], clickable=False
        )
        kpi_grid.addWidget(self.card_prod, 0, 0)

        self.card_low, self.lbl_low = self.create_borderless_kpi(
            "Low Stock", "0", "Items below threshold",
            self.COLORS['warning'], clickable=True,
            on_click=lambda: self.kpi_low_stock_clicked.emit()
        )
        kpi_grid.addWidget(self.card_low, 0, 1)

        self.card_out, self.lbl_out = self.create_borderless_kpi(
            "Out of Stock", "0", "Items depleted",
            self.COLORS['danger'], clickable=True,
            on_click=lambda: self.kpi_out_of_stock_clicked.emit()
        )
        kpi_grid.addWidget(self.card_out, 0, 2)

        self.card_def, self.lbl_def = self.create_borderless_kpi(
            "Defective Items", "0", "Reported defects",
            self.COLORS['purple'], clickable=True,
            on_click=lambda: self.kpi_defective_clicked.emit()
        )
        kpi_grid.addWidget(self.card_def, 0, 3)

        layout.addLayout(kpi_grid)

        # Bottom Section
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)

        # Stock Flow
        flow_frame = QFrame()
        flow_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.COLORS['white']}; 
                border: 1px solid {self.COLORS['border']};
                border-radius: 8px;
            }}
        """)
        flow_layout = QVBoxLayout(flow_frame)
        flow_layout.setContentsMargins(24, 24, 24, 24)

        flow_title = QLabel("Today's Stock Flow")
        flow_title.setFont(self.sub_header_font)
        flow_title.setStyleSheet(f"color: {self.COLORS['text_primary']}; border: none;")
        flow_layout.addWidget(flow_title)

        self.flow_chart = FlowChart(width=4, height=3)
        flow_layout.addWidget(self.flow_chart)
        bottom_row.addWidget(flow_frame, 1)

        # Activity
        act_container = QFrame()
        act_container.setStyleSheet(f"""
            QFrame {{
                background-color: {self.COLORS['white']}; 
                border: 1px solid {self.COLORS['border']};
                border-radius: 8px;
            }}
        """)
        act_layout = QVBoxLayout(act_container)
        act_layout.setContentsMargins(24, 24, 24, 24)

        act_title = QLabel("Recent Activity")
        act_title.setFont(self.sub_header_font)
        act_title.setStyleSheet(f"color: {self.COLORS['text_primary']}; border: none;")
        act_layout.addWidget(act_title)

        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["Date", "Type", "Product", "User"])
        self.activity_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.activity_table.verticalHeader().setVisible(False)
        self.activity_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.activity_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.activity_table.setStyleSheet(f"""
            QTableWidget {{ 
                border: none; 
                background-color: {self.COLORS['white']}; 
                color: {self.COLORS['text_primary']}; 
                font-family: 'Segoe UI';
                font-size: 11px;
            }}
            QHeaderView::section {{ 
                background-color: {self.COLORS['bg_gray']}; 
                color: {self.COLORS['text_secondary']}; 
                font-weight: 600; 
                border: none;
                padding: 8px;
                text-transform: uppercase;
                font-size: 10px;
                letter-spacing: 0.5px;
            }}
            QTableWidget::item {{ 
                padding: 10px 8px;
                border-bottom: 1px solid {self.COLORS['border']};
                border-left: none;
                border-right: none;
                border-top: none;
            }}
            QTableWidget::item:selected {{
                background-color: {self.COLORS['bg_gray']};
            }}
        """)
        self.activity_table.cellDoubleClicked.connect(lambda r, c: self.activity_double_clicked.emit(r))
        act_layout.addWidget(self.activity_table)

        bottom_row.addWidget(act_container, 2)
        layout.addLayout(bottom_row)
        layout.addStretch()

        return page

    def create_borderless_kpi(self, title, value, subtitle, status_color, clickable=False, on_click=None):
        """Completely borderless KPI card"""
        card = QFrame()
        card.setFixedHeight(140)

        base_style = f"""
            QFrame {{
                background-color: {self.COLORS['white']}; 
                border: none;
                border-radius: 8px;
            }}
        """

        if clickable:
            base_style = f"""
                QFrame {{
                    background-color: {self.COLORS['white']}; 
                    border: none;
                    border-radius: 8px;
                }}
                QFrame:hover {{
                    background-color: #FAFAFA;
                }}
            """
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            if on_click:
                card.mousePressEvent = lambda e: on_click()

        card.setStyleSheet(base_style)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(4)

        title_label = QLabel(title.upper())
        title_label.setFont(self.kpi_label_font)
        title_label.setStyleSheet(f"""
            color: {self.COLORS['text_secondary']}; 
            background-color: transparent;
            border: none;
            letter-spacing: 0.5px;
        """)
        card_layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setFont(self.kpi_value_font)
        value_label.setStyleSheet(f"""
            color: {status_color}; 
            background-color: transparent;
            border: none;
            font-weight: 700;
        """)
        card_layout.addWidget(value_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Normal))
        subtitle_label.setStyleSheet(f"""
            color: {self.COLORS['text_secondary']}; 
            background-color: transparent;
            border: none;
        """)
        card_layout.addWidget(subtitle_label)

        card_layout.addStretch()

        return card, value_label

    def update_analytics(self, data):
        self.lbl_prod.setText(str(data.get('total_products', 0)))
        self.lbl_low.setText(str(data.get('low_stock_count', 0)))
        self.lbl_out.setText(str(data.get('out_of_stock_count', 0)))
        self.lbl_def.setText(str(data.get('defective_count', 0)))

        flow = data.get('stock_flow', {})
        self.flow_chart.update_chart(flow.get('in', 0), flow.get('out', 0))

        acts = data.get('recent_activities', [])
        self.activity_table.setRowCount(len(acts))
        for r, a in enumerate(acts):
            self.activity_table.setItem(r, 0, QTableWidgetItem(str(a.get('formatted_date', ''))))

            type_item = QTableWidgetItem(str(a.get('transaction_type', '')))
            if a.get('transaction_type') == 'IN':
                type_item.setForeground(QColor(self.COLORS['success']))
            elif a.get('transaction_type') == 'OUT':
                type_item.setForeground(QColor(self.COLORS['danger']))
            elif a.get('transaction_type') == 'DEFECT':
                type_item.setForeground(QColor(self.COLORS['warning']))
            self.activity_table.setItem(r, 1, type_item)

            self.activity_table.setItem(r, 2, QTableWidgetItem(str(a.get('product_name', ''))))
            self.activity_table.setItem(r, 3, QTableWidgetItem(str(a.get('performed_by', ''))))