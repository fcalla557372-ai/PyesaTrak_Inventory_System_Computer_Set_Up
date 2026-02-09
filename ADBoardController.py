# Filename: ADBoardController.py
from ADBModel import DashboardModel
from ManageUsersModel import ManageUsersModel
from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt

from ManageUsersController import ManageUsersController
from Ainventory_Cont import ProductDetailsController
from AreportController import ReportsController
from AreportsView import ReportsView


# --- Custom Frameless Dialog (Matches Staff/Target Design) ---
class CustomMessageBox(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(350, 160)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header (Teal)
        self.header = QFrame()
        self.header.setStyleSheet("""
            QFrame {
                background-color: #0076aa;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        self.header.setFixedHeight(40)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(15, 0, 10, 0)

        title = QLabel("Sign Out")
        title.setStyleSheet("color: white; font-weight: bold; font-family: Arial; font-size: 14px; border: none;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                color: white;
                background: transparent;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { color: #ffcccc; }
        """)
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)

        layout.addWidget(self.header)

        # Body (White)
        self.body = QFrame()
        self.body.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        body_layout = QVBoxLayout(self.body)
        body_layout.setContentsMargins(20, 20, 20, 20)

        msg = QLabel("Are you sure you want to sign out?")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setStyleSheet("color: black; font-family: Arial; font-size: 13px; border: none;")
        body_layout.addWidget(msg)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        btn_style = """
            QPushButton { 
                background-color: #0076aa; 
                color: white; 
                border-radius: 5px; 
                padding: 6px 0; 
                font-weight: bold; 
                font-family: Arial;
                min-width: 90px;
                border: none;
            }
            QPushButton:hover { background-color: #005f8a; }
        """

        btn_yes = QPushButton("Yes")
        btn_yes.setStyleSheet(btn_style)
        btn_yes.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_yes.clicked.connect(self.accept)

        btn_no = QPushButton("No")
        btn_no.setStyleSheet(btn_style)
        btn_no.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_no.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_yes)
        btn_layout.addWidget(btn_no)
        btn_layout.addStretch()

        body_layout.addLayout(btn_layout)
        layout.addWidget(self.body)


class DashboardController:
    def __init__(self, user_data=None):
        from ADBoardView import DashboardView

        self.model = DashboardModel()
        self.view = DashboardView()
        self.user_data = user_data

        self.users_controller = None
        self.product_controller = None
        self.reports_controller = None

        self.view.dashboard_clicked.connect(self.handle_dashboard)
        self.view.manage_users_clicked.connect(self.handle_manage_users)
        self.view.product_stock_clicked.connect(self.handle_product_stock)
        self.view.reports_clicked.connect(self.handle_reports)

        self.view.sign_out_clicked.connect(self.handle_sign_out)
        self.view.refresh_analytics_clicked.connect(self.refresh_dashboard)

        # Removed total products click connection
        self.view.kpi_low_stock_clicked.connect(self.filter_low_stock_view)
        self.view.kpi_out_of_stock_clicked.connect(self.filter_out_of_stock_view)
        self.view.kpi_defective_clicked.connect(self.filter_defective_view)

        self.view.activity_double_clicked.connect(self.show_activity_details)

        self.refresh_dashboard()

    def refresh_dashboard(self):
        print("Refreshing Dashboard Data...")
        data = {
            'total_products': self.model.get_total_products(),
            'low_stock_count': self.model.get_low_stock_items_count(),
            'out_of_stock_count': self.model.get_out_of_stock_count(),
            'defective_count': self.model.get_defective_count(),
            'stock_flow': self.model.get_stock_flow_summary(),
            'recent_activities': self.model.get_recent_inventory_activities(10)
        }
        self.view.update_analytics(data)
        self.recent_activities_data = data['recent_activities']

    def handle_dashboard(self):
        self.view.show_dashboard_page()
        self.refresh_dashboard()

    def handle_manage_users(self):
        if not self.users_controller:
            self.users_controller = ManageUsersController(self.user_data)
            self.view.stacked_widget.removeWidget(self.view.stacked_widget.widget(1))
            self.view.stacked_widget.insertWidget(1, self.users_controller.view)
        self.view.show_manage_users_page()
        self.users_controller.refresh_data()

    def _ensure_product_controller(self):
        if not self.product_controller:
            self.product_controller = ProductDetailsController(self.user_data)
            self.view.stacked_widget.removeWidget(self.view.stacked_widget.widget(2))
            self.view.stacked_widget.insertWidget(2, self.product_controller.view)

    def handle_product_stock(self):
        self._ensure_product_controller()
        self.view.show_product_page()
        self.product_controller.load_all_products()

    def filter_total_products_view(self):
        # This method is effectively essentially same as handle_product_stock
        self._ensure_product_controller()
        self.view.show_product_page()
        self.product_controller.load_all_products()

    def filter_low_stock_view(self):
        self._ensure_product_controller()
        self.view.show_product_page()
        self.product_controller.load_low_stock()

    def filter_out_of_stock_view(self):
        self._ensure_product_controller()
        self.view.show_product_page()
        self.product_controller.load_out_of_stock()

    def filter_defective_view(self):
        self._ensure_product_controller()
        self.view.show_product_page()
        self.product_controller.load_defective()

    def handle_reports(self):
        if not self.reports_controller:
            report_view = ReportsView()
            self.reports_controller = ReportsController(self.user_data)
            self.reports_controller.set_view(report_view)
            self.view.stacked_widget.removeWidget(self.view.stacked_widget.widget(3))
            self.view.stacked_widget.insertWidget(3, report_view)
        self.view.show_reports_page()

    def show_activity_details(self, row_index):
        if row_index < 0 or row_index >= len(self.recent_activities_data):
            return
        activity = self.recent_activities_data[row_index]
        details = (
            f"Transaction Date: {activity.get('formatted_date')}\n"
            f"Type: {activity.get('transaction_type')}\n"
            f"Product: {activity.get('product_name')}\n"
            f"Performed By: {activity.get('performed_by')}\n"
        )
        msg = QMessageBox(self.view)
        msg.setWindowTitle("Activity Details")
        msg.setText(details)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("background-color: white; color: black;")
        msg.exec()

    def handle_sign_out(self):
        msg = CustomMessageBox(self.view)
        if msg.exec():
            try:
                # 1. Open Login Window FIRST
                from login_controller import LoginController
                from login_view import LoginView
                from login_model import LoginModel

                self.lc = LoginController(LoginView(), LoginModel())
                self.lc.show()

                # 2. THEN Close Dashboard
                self.view.close()
            except Exception as e:
                print(f"Error returning to login: {e}")

    def show(self):
        self.view.show()