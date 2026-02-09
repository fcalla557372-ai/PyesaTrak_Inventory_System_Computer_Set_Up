# Filename: ADBoardView.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QStackedWidget, QFrame, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView,
                             QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QColor

# --- MATPLOTLIB IMPORTS ---
import matplotlib

matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ManageUsersView import ManageUsersView
from Ainventory_view import ProductDetailsView


# --- CUSTOM CHART WIDGET ---
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
        self.axes.spines['bottom'].set_color('#cccccc')
        self.axes.spines['bottom'].set_linewidth(1.5)

        self.axes.tick_params(axis='x', colors='#333333', labelsize=10)
        self.axes.tick_params(axis='y', length=0)
        self.axes.set_yticks([])

        for bar in bars:
            height = bar.get_height()
            self.axes.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                           f'{int(height)}',
                           ha='center', va='bottom', fontsize=12, fontweight='bold', color='#333333')
        self.draw()


class DashboardView(QWidget):
    # Signals
    dashboard_clicked = pyqtSignal()
    manage_users_clicked = pyqtSignal()
    reports_clicked = pyqtSignal()
    product_stock_clicked = pyqtSignal()
    sign_out_clicked = pyqtSignal()
    refresh_analytics_clicked = pyqtSignal()

    # KPI Signals (Total Products removed as it's static)
    kpi_low_stock_clicked = pyqtSignal()
    kpi_out_of_stock_clicked = pyqtSignal()
    kpi_defective_clicked = pyqtSignal()

    # Table Signal
    activity_double_clicked = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.COLORS = {
            'primary': '#0076aa',
            'secondary': '#38b6ff',
            'black': '#000000',
            'bg_gray': '#f2f2f2',
            'white': '#FFFFFF',
            'danger': '#D32F2F',
            'warning': '#FF9800'
        }
        self.header_font = QFont("League Spartan", 24, QFont.Weight.Bold)
        self.sub_header_font = QFont("Poppins", 14, QFont.Weight.Bold)
        self.btn_font = QFont("League Spartan", 11, QFont.Weight.Bold)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PyesaTrak - Admin Dashboard")
        self.setFixedSize(1260, 750)
        self.setStyleSheet(f"background-color: {self.COLORS['bg_gray']}; font-family: 'Poppins', Arial;")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. SIDEBAR
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet(f"background-color: {self.COLORS['black']}; border: none;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(25, 50, 25, 50)
        sidebar_layout.setSpacing(15)

        app_title = QLabel("PyesaTrak")
        app_title.setFont(QFont("League Spartan", 28, QFont.Weight.Bold))
        app_title.setStyleSheet(f"color: {self.COLORS['secondary']}; margin-bottom: 20px;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(app_title)

        self.dashboard_btn = self.create_nav_btn("Dashboard")
        self.manage_users_btn = self.create_nav_btn("Manage Users")
        self.product_stock_btn = self.create_nav_btn("Inventory")
        self.reports_btn = self.create_nav_btn("Reports")

        self.dashboard_btn.clicked.connect(self.dashboard_clicked.emit)
        self.manage_users_btn.clicked.connect(self.manage_users_clicked.emit)
        self.product_stock_btn.clicked.connect(self.product_stock_clicked.emit)
        self.reports_btn.clicked.connect(self.reports_clicked.emit)

        sidebar_layout.addWidget(self.dashboard_btn)
        sidebar_layout.addWidget(self.manage_users_btn)
        sidebar_layout.addWidget(self.product_stock_btn)
        sidebar_layout.addWidget(self.reports_btn)

        sidebar_layout.addStretch()

        self.sign_out_btn = QPushButton("Sign Out")
        self.sign_out_btn.setFixedHeight(50)
        self.sign_out_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sign_out_btn.setFont(self.btn_font)
        self.sign_out_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #333333; 
                color: white; 
                border-radius: 25px; 
            }}
            QPushButton:hover {{ background-color: {self.COLORS['danger']}; color: white; }}
        """)
        self.sign_out_btn.clicked.connect(self.sign_out_clicked.emit)
        sidebar_layout.addWidget(self.sign_out_btn)

        main_layout.addWidget(sidebar)

        # 2. CONTENT AREA
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(40, 40, 40, 40)

        self.stacked_widget = QStackedWidget()
        self.dashboard_page = self.create_dashboard_page()
        self.users_page = ManageUsersView()
        self.products_page = ProductDetailsView()
        self.reports_page = QWidget()

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.users_page)
        self.stacked_widget.addWidget(self.products_page)
        self.stacked_widget.addWidget(self.reports_page)

        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(content_area)

        self.update_button_styles(self.dashboard_btn)

    def create_nav_btn(self, text):
        btn = QPushButton(text)
        btn.setFixedHeight(55)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFont(QFont("League Spartan", 14, QFont.Weight.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: #888888;
                text-align: left;
                padding-left: 20px;
                border: none;
                border-radius: 25px;
            }}
            QPushButton:hover {{ color: {self.COLORS['white']}; }}
        """)
        return btn

    def update_button_styles(self, active_btn):
        buttons = [self.dashboard_btn, self.manage_users_btn, self.product_stock_btn, self.reports_btn]
        for btn in buttons:
            if btn == active_btn:
                btn.setStyleSheet(f"""
                    background-color: {self.COLORS['primary']};
                    color: white;
                    text-align: left;
                    padding-left: 20px;
                    border: none;
                    border-radius: 25px;
                """)
            else:
                btn.setStyleSheet("""
                    background-color: transparent;
                    color: #888888;
                    text-align: left;
                    padding-left: 20px;
                    border: none;
                    border-radius: 25px;
                """)

    def show_dashboard_page(self):
        self.stacked_widget.setCurrentIndex(0)
        self.update_button_styles(self.dashboard_btn)

    def show_manage_users_page(self):
        self.stacked_widget.setCurrentIndex(1)
        self.update_button_styles(self.manage_users_btn)

    def show_product_page(self):
        self.stacked_widget.setCurrentIndex(2)
        self.update_button_styles(self.product_stock_btn)

    def show_reports_page(self):
        self.stacked_widget.setCurrentIndex(3)
        self.update_button_styles(self.reports_btn)

    # --- DASHBOARD PAGE ---
    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(25)

        # Header
        header_row = QHBoxLayout()
        title = QLabel("Overview")
        title.setFont(self.header_font)
        title.setStyleSheet(f"color: {self.COLORS['black']};")

        ref_btn = QPushButton("Refresh Data")
        ref_btn.setFixedSize(140, 45)
        ref_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ref_btn.setFont(self.btn_font)
        ref_btn.setStyleSheet(f"""
            background-color: {self.COLORS['secondary']}; 
            color: black; 
            border-radius: 22px;
        """)
        ref_btn.clicked.connect(self.refresh_analytics_clicked.emit)

        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(ref_btn)
        layout.addLayout(header_row)

        # KPI Cards
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(25)

        # 1. Total Products (NOT CLICKABLE)
        self.card_prod = self.create_clickable_kpi(kpi_row, "TOTAL PRODUCTS", "0", self.COLORS['primary'])
        self.lbl_prod = self.card_prod['label']

        # 2. Low Stock (Clickable)
        self.card_low = self.create_clickable_kpi(kpi_row, "LOW STOCK", "0", self.COLORS['warning'])
        self.card_low['frame'].mousePressEvent = lambda e: self.kpi_low_stock_clicked.emit()
        self.card_low['frame'].setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_low = self.card_low['label']

        # 3. Out of Stock (Clickable)
        self.card_out = self.create_clickable_kpi(kpi_row, "OUT OF STOCK", "0", self.COLORS['danger'])
        self.card_out['frame'].mousePressEvent = lambda e: self.kpi_out_of_stock_clicked.emit()
        self.card_out['frame'].setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_out = self.card_out['label']

        # 4. Defective (Clickable)
        self.card_defect = self.create_clickable_kpi(kpi_row, "DEFECTIVE", "0", "#9C27B0")
        self.card_defect['frame'].mousePressEvent = lambda e: self.kpi_defective_clicked.emit()
        self.card_defect['frame'].setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_defect = self.card_defect['label']

        layout.addLayout(kpi_row)

        # Bottom Row
        bottom_row = QHBoxLayout()

        # Graph
        flow_frame = QFrame()
        flow_frame.setStyleSheet("background-color: white; border-radius: 25px;")
        flow_layout = QVBoxLayout(flow_frame)
        flow_layout.setContentsMargins(20, 20, 20, 20)
        flow_title = QLabel("Today's Flow")
        flow_title.setFont(self.sub_header_font)
        flow_layout.addWidget(flow_title)
        self.flow_chart = FlowChart(width=4, height=3)
        flow_layout.addWidget(self.flow_chart)
        bottom_row.addWidget(flow_frame, 1)

        # Activity Table
        act_container = QFrame()
        act_container.setStyleSheet("background-color: white; border-radius: 25px;")
        act_layout = QVBoxLayout(act_container)
        act_layout.setContentsMargins(25, 25, 25, 25)
        act_title = QLabel("Recent Activity (Double-click details)")
        act_title.setFont(self.sub_header_font)
        act_layout.addWidget(act_title)

        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["Date", "Type", "Item", "User"])
        self.activity_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.activity_table.verticalHeader().setVisible(False)
        self.activity_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.activity_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.activity_table.setStyleSheet(f"""
            QTableWidget {{ border: none; background-color: white; color: black; font-family: 'Poppins'; }}
            QHeaderView::section {{ background-color: white; color: #888; font-weight: bold; border-bottom: 2px solid #eee; }}
            QTableWidget::item {{ padding: 8px; }}
        """)
        # Connect Double Click
        self.activity_table.cellDoubleClicked.connect(lambda r, c: self.activity_double_clicked.emit(r))
        act_layout.addWidget(self.activity_table)

        bottom_row.addWidget(act_container, 2)
        layout.addLayout(bottom_row)
        layout.addStretch()

        return page

    def create_clickable_kpi(self, layout, title, value, color):
        """Creates a KPI card"""
        card = QFrame()
        card.setFixedHeight(130)
        card.setStyleSheet(f"background-color: white; border-radius: 25px; border-left: 8px solid {color};")

        l = QVBoxLayout(card)
        l.setContentsMargins(20, 20, 20, 20)

        t = QLabel(title)
        t.setFont(QFont("League Spartan", 10, QFont.Weight.Bold))
        t.setStyleSheet("color: #888; background-color: transparent;")
        l.addWidget(t)

        v = QLabel(value)
        v.setFont(QFont("League Spartan", 32, QFont.Weight.Bold))
        v.setStyleSheet(f"color: {color}; background-color: transparent;")
        l.addWidget(v)

        layout.addWidget(card)
        return {'frame': card, 'label': v}

    def update_analytics(self, data):
        self.lbl_prod.setText(str(data.get('total_products', 0)))
        self.lbl_low.setText(str(data.get('low_stock_count', 0)))
        self.lbl_out.setText(str(data.get('out_of_stock_count', 0)))
        self.lbl_defect.setText(str(data.get('defective_count', 0)))

        flow = data.get('stock_flow', {})
        self.flow_chart.update_chart(flow.get('in', 0), flow.get('out', 0))

        acts = data.get('recent_activities', [])
        self.activity_table.setRowCount(len(acts))
        for r, a in enumerate(acts):
            self.activity_table.setItem(r, 0, QTableWidgetItem(str(a.get('formatted_date', ''))))
            type_item = QTableWidgetItem(str(a.get('transaction_type', '')))
            if a.get('transaction_type') == 'IN':
                type_item.setForeground(QColor(self.COLORS['primary']))
            elif a.get('transaction_type') == 'OUT':
                type_item.setForeground(QColor(self.COLORS['danger']))
            self.activity_table.setItem(r, 1, type_item)
            self.activity_table.setItem(r, 2, QTableWidgetItem(str(a.get('product_name', ''))))
            self.activity_table.setItem(r, 3, QTableWidgetItem(str(a.get('performed_by', ''))))