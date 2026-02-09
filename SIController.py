# SIController.py
from SIModel import InventoryModel
from SIView import InventoryView, StockInDialog, StockOutDialog, DefectDialog
from PyQt6.QtWidgets import QMessageBox


class InventoryController:
    """Controller for Staff Inventory Operations"""

    def __init__(self, model, view, user_data=None):
        self.model = model
        self.view = view
        self.user_data = user_data

        # Connect Staff Signals
        self.view.stock_in_clicked.connect(lambda: self.handle_transaction('IN'))
        self.view.stock_out_clicked.connect(lambda: self.handle_transaction('OUT'))
        self.view.defect_clicked.connect(lambda: self.handle_transaction('DEFECT'))

        # Initial Load
        self.load_all_products()

    def load_all_products(self):
        products = self.model.get_all_products()
        self.view.load_table(products)

    # [NEW] Filter Methods for Dashboard KPIs
    def load_low_stock(self):
        products = self.model.get_products_by_filter("stock_quantity <= 10 AND stock_quantity > 0")
        self.view.load_table(products)

    def load_out_of_stock(self):
        products = self.model.get_products_by_filter("stock_quantity = 0")
        self.view.load_table(products)

    def load_defective(self):
        # [UPDATED] Use specific method to get reasons and load specific table view
        products = self.model.get_defective_products_with_reason()
        self.view.load_defective_table(products)

    def handle_transaction(self, trans_type):
        all_products = self.model.get_all_products()
        if not all_products:
            QMessageBox.warning(self.view, "Inventory Empty", "No products available.")
            return

        user_id = self.user_data['user_id'] if self.user_data else 1

        dialog = None
        success_msg = ""

        if trans_type == 'IN':
            dialog = StockInDialog(all_products, self.view)
            success_msg = "Stock added successfully."
        elif trans_type == 'OUT':
            dialog = StockOutDialog(all_products, self.view)
            success_msg = "Stock removed successfully."
        elif trans_type == 'DEFECT':
            dialog = DefectDialog(all_products, self.view)
            success_msg = "Defect reported successfully."

        if dialog and dialog.exec():
            if trans_type == 'IN':
                pid, qty, rem = dialog.get_data()
                success = self.model.update_stock(pid, qty, trans_type, rem, user_id)
            elif trans_type == 'OUT':
                pid, qty, rem = dialog.get_data()
                success = self.model.update_stock(pid, -qty, trans_type, rem, user_id)
            else:  # DEFECT
                pid, qty, rem = dialog.get_data()
                success = self.model.update_stock(pid, -qty, trans_type, rem, user_id)

            if success:
                QMessageBox.information(self.view, "Success", success_msg)
                self.load_all_products()
            else:
                QMessageBox.critical(self.view, "Error", "Transaction failed.")

    def show(self):
        self.view.show()