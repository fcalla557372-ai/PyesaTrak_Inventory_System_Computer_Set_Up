# Ainventory_Cont.py
from Ainventory_model import ProductDetailsModel
from Ainventory_view import ProductDetailsView, AddProductDialog
from PyQt6.QtWidgets import QMessageBox


class ProductDetailsController:
    def __init__(self, user_data=None):
        self.model = ProductDetailsModel()
        self.view = ProductDetailsView()
        self.user_data = user_data

        # [NEW] Apply Role Permissions Immediately
        if self.user_data:
            role = self.user_data.get('role', 'Staff')
            # Assuming view has this method if you need to reuse this controller for staff
            if hasattr(self.view, 'apply_role_permissions'):
                self.view.apply_role_permissions(role)

        # Connect View Signals
        self.view.add_product_clicked.connect(self.handle_add_product)
        # Admin doesn't have stock in/out buttons in view, but keeping for compatibility if needed
        if hasattr(self.view, 'stock_in_clicked'):
            self.view.stock_in_clicked.connect(lambda: self.handle_transaction('IN'))
            self.view.stock_out_clicked.connect(lambda: self.handle_transaction('OUT'))
            self.view.defect_clicked.connect(lambda: self.handle_transaction('DEFECT'))

        # Initial Load
        self.load_all_products()

    def load_all_products(self):
        """Load full inventory list (Reset filters)"""
        products = self.model.get_all_products()
        self.view.load_products(products)

    # --- FILTER METHODS (Called by Dashboard) ---
    def load_low_stock(self):
        """Show items with stock <= 10 but > 0"""
        products = self.model.get_products_by_filter("stock_quantity <= 10 AND stock_quantity > 0")
        self.view.load_products(products)

    def load_out_of_stock(self):
        """Show items with 0 stock"""
        products = self.model.get_products_by_filter("stock_quantity = 0")
        self.view.load_products(products)

    def load_defective(self):
        """Show items explicitly marked as Defective WITH REASON"""
        # [NEW] Use specific method to get reasons
        products = self.model.get_defective_products_with_reason()
        # [NEW] Use specific view method to show Reason column
        self.view.load_defective_table(products)

    def handle_add_product(self):
        dialog = AddProductDialog(self.view)
        if dialog.exec():
            data = dialog.get_data()
            if not data['product_name']:
                QMessageBox.warning(self.view, "Missing Information", "Product Name is required.")
                return

            # Add user_id to data for transaction logging
            if self.user_data:
                data['user_id'] = self.user_data.get('user_id', 1)
            else:
                data['user_id'] = 1  # Default to admin if no user data

            if self.model.add_new_product(data):
                QMessageBox.information(self.view, "Success", "Product added successfully.")
                self.load_all_products()
            else:
                QMessageBox.critical(self.view, "Error", "Failed to add product.")

    def handle_transaction(self, trans_type):
        # Admin controller primarily handles View/Add.
        # Transaction logic is typically in Staff controller,
        # but kept here if shared logic is required.
        pass

    def show(self):
        self.view.show()