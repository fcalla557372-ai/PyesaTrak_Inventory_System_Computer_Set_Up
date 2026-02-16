# Ainventory_model.py
import mysql.connector
from mysql.connector import Error


class ProductDetailsModel:
    def __init__(self):
        self.connection = None

    def connect_to_database(self):
        try:
            self.connection = mysql.connector.connect(
                host='127.0.0.1',
                database='pyesatrak',
                user='root',
                password=''
            )
            if self.connection.is_connected():
                return True, "Connected"
        except Error as e:
            return False, str(e)
        return False, "Failed"

    def get_all_products(self):
        """Fetch all products (Default view)"""
        # Equivalent to filtering where 1=1 (always true)
        return self.get_products_by_filter("1=1")

    def get_products_by_filter(self, where_clause):
        """
        Fetch products based on a custom SQL WHERE clause.
        Used for KPI filtering (Low Stock, Out of Stock, etc.)
        """
        self.connect_to_database()
        try:
            cursor = self.connection.cursor(dictionary=True)
            # Fetch products matching the filter
            query = f"SELECT product_id, product_name, brand, model, stock_quantity, status FROM inventory WHERE {where_clause} ORDER BY product_id ASC"
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching filtered products: {e}")
            return []
        finally:
            if self.connection and self.connection.is_connected():
                self.connection.close()

    # --- NEW METHOD FOR DEFECTIVE KPI ---
    def get_defective_products_with_reason(self):
        """
        Fetches products that have been reported as defective,
        joining with the transaction log to get the specific REASON (remarks).
        """
        self.connect_to_database()
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
            if self.connection and self.connection.is_connected():
                self.connection.close()

    def add_new_product(self, data):
        self.connect_to_database()
        try:
            cursor = self.connection.cursor()
            qty = int(data['stock_quantity'])

            # Determine status
            status = data.get('status')
            if not status:
                if qty == 0:
                    status = 'Out of Stock'
                elif qty <= 10:
                    status = 'Low Stock'
                else:
                    status = 'Available'

            # 1. Insert product into inventory
            query = """
                INSERT INTO inventory (product_name, brand, model, description, stock_quantity, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            cursor.execute(query, (
                data['product_name'],
                data['brand'],
                data['model'],
                data['description'],
                qty,
                status
            ))

            # Get the newly created product_id
            product_id = cursor.lastrowid

            # 2. Create initial stock transaction if quantity > 0
            if qty > 0:
                user_id = data.get('user_id', 1)  # Get user_id from data, default to 1 if not provided
                transaction_query = """
                    INSERT INTO stock_transactions 
                    (product_id, transaction_type, quantity, remarks, performed_by, transaction_date)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """
                cursor.execute(transaction_query, (
                    product_id,
                    'IN',
                    qty,
                    f'Initial stock - Product added',
                    user_id
                ))

                # 3. Log activity
                activity_query = """
                    INSERT INTO activity_log (user_id, activity_description, activity_time)
                    VALUES (%s, %s, NOW())
                """
                cursor.execute(activity_query, (
                    user_id,
                    f"Added product '{data['product_name']}' with initial stock: {qty}"
                ))

            self.connection.commit()
            return True
        except Error as err:
            print(f"Error adding product: {err}")
            if self.connection:
                self.connection.rollback()
            return False
        finally:
            if self.connection and self.connection.is_connected():
                self.connection.close()

    def update_stock(self, product_id, quantity_change, transaction_type, remarks, user_id):
        self.connect_to_database()
        try:
            cursor = self.connection.cursor()
            self.connection.start_transaction()

            # 0. Get product name for activity log
            cursor.execute("SELECT product_name FROM inventory WHERE product_id = %s", (product_id,))
            result = cursor.fetchone()
            product_name = result[0] if result else f"Product #{product_id}"

            # 1. Update Inventory Table
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

            # 2. Log Transaction
            log_query = """
                INSERT INTO stock_transactions 
                (product_id, transaction_type, quantity, remarks, performed_by, transaction_date)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(log_query, (product_id, transaction_type, abs(quantity_change), remarks, user_id))

            # 3. Log Activity
            activity_desc = ""
            if transaction_type == 'IN':
                activity_desc = f"Stock IN: {abs(quantity_change)} units of '{product_name}'"
            elif transaction_type == 'OUT':
                activity_desc = f"Stock OUT: {abs(quantity_change)} units of '{product_name}'"
            elif transaction_type == 'DEFECT':
                activity_desc = f"Reported DEFECT: {abs(quantity_change)} units of '{product_name}'"

            if activity_desc:
                activity_query = """
                    INSERT INTO activity_log (user_id, activity_description, activity_time)
                    VALUES (%s, %s, NOW())
                """
                cursor.execute(activity_query, (user_id, activity_desc))

            self.connection.commit()
            return True
        except Error as err:
            print(f"Error updating stock: {err}")
            self.connection.rollback()
            return False
        finally:
            if self.connection and self.connection.is_connected():
                self.connection.close()