# SIModel.py
import mysql.connector
from mysql.connector import Error

class InventoryModel:
    """Model specifically for Staff operations (No Add Product)"""
    def __init__(self):
        self.connection = None
        self.db_config = {
            'host': '127.0.0.1',
            'database': 'pyesatrak',
            'user': 'root',
            'password': ''
        }

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            return self.connection.is_connected()
        except Error as e:
            print(f"Database Error: {e}")
            return False

    def get_all_products(self):
        return self.get_products_by_filter("1=1")

    def get_products_by_filter(self, where_clause):
        self.connect()
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = f"SELECT product_id, product_name, brand, model, stock_quantity, status FROM inventory WHERE {where_clause} ORDER BY product_id ASC"
            cursor.execute(query)
            return cursor.fetchall()
        except Error:
            return []
        finally:
            if self.connection: self.connection.close()

    # --- NEW METHOD FOR DEFECTIVE KPI ---
    def get_defective_products_with_reason(self):
        """
        Fetches products that have been reported as defective,
        joining with the transaction log to get the specific REASON (remarks).
        """
        self.connect()
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT i.product_id, i.product_name, i.brand, i.model, 
                       i.stock_quantity, i.status, t.remarks as defect_reason
                FROM inventory i
                JOIN stock_transactions t ON i.product_id = t.product_id
                WHERE t.transaction_type = 'DEFECT'
                ORDER BY t.transaction_date DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching defective products: {e}")
            return []
        finally:
            if self.connection: self.connection.close()

    def update_stock(self, product_id, quantity_change, transaction_type, remarks, user_id):
        self.connect()
        try:
            cursor = self.connection.cursor()
            self.connection.start_transaction()

            update_query = """
                UPDATE inventory 
                SET stock_quantity = stock_quantity + %s,
                    status = CASE 
                        WHEN (stock_quantity + %s) <= 0 THEN 'Out of Stock'
                        WHEN (stock_quantity + %s) <= 10 THEN 'Low Stock'
                        ELSE 'Available'
                    END,
                    updated_at = NOW()
                WHERE product_id = %s
            """
            cursor.execute(update_query, (quantity_change, quantity_change, quantity_change, product_id))

            log_query = """
                INSERT INTO stock_transactions 
                (product_id, transaction_type, quantity, remarks, performed_by, transaction_date)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(log_query, (product_id, transaction_type, abs(quantity_change), remarks, user_id))

            self.connection.commit()
            return True
        except Error:
            self.connection.rollback()
            return False
        finally:
            if self.connection: self.connection.close()