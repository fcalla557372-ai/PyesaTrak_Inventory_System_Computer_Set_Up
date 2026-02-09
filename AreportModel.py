# AreportModel.py
import mysql.connector
from mysql.connector import Error


class ReportsModel:
    def __init__(self):
        self.db_config = {
            'host': '127.0.0.1',
            'database': 'pyesatrak',
            'user': 'root',
            'password': ''
        }

    def connect(self):
        try:
            return mysql.connector.connect(**self.db_config)
        except Error as e:
            print(f"Error connecting to DB: {e}")
            return None

    def get_all_saved_reports(self):
        """Fetch report history including transaction reference if available"""
        conn = self.connect()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            # Fetch generic reports first
            query = """
                SELECT * FROM saved_reports 
                ORDER BY created_at DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching saved reports: {e}")
            return []
        finally:
            if conn: conn.close()

    def save_report_entry(self, rtype, start, end, user, transaction_id=None):
        """
        Log generation in history with optional reference to a specific stock transaction.
        :param transaction_id: (Optional) ID from stock_transactions table
        """
        conn = self.connect()
        if not conn: return False
        try:
            cursor = conn.cursor()
            report_name = f"{rtype} ({start} to {end})"

            # [UPDATED] Insert includes transaction_id reference
            # If transaction_id is passed as None, MySQL stores it as NULL (which is correct)
            query = """
                INSERT INTO saved_reports 
                (report_name, report_type, start_date, end_date, created_by, transaction_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (report_name, rtype, start, end, user, transaction_id))
            conn.commit()
            return True
        except Error as e:
            print(f"Error saving report log: {e}")
            return False
        finally:
            if conn: conn.close()

    def get_stock_movement(self, start, end):
        conn = self.connect()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT t.transaction_date, t.transaction_type, i.product_name, 
                       t.quantity, t.remarks, u.username
                FROM stock_transactions t
                JOIN inventory i ON t.product_id = i.product_id
                JOIN users u ON t.performed_by = u.user_id
                WHERE t.transaction_date BETWEEN %s AND %s
                ORDER BY t.transaction_date DESC
            """
            cursor.execute(query, (f"{start} 00:00:00", f"{end} 23:59:59"))
            return cursor.fetchall()
        finally:
            if conn: conn.close()

    def get_inventory_status(self):
        conn = self.connect()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT product_id, product_name, brand, model, stock_quantity, status 
                FROM inventory ORDER BY product_id ASC
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            if conn: conn.close()

    def get_defective_report(self, start, end):
        conn = self.connect()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT t.transaction_date, i.product_name, i.brand, 
                       t.quantity as defective_qty, t.remarks, u.username
                FROM stock_transactions t
                JOIN inventory i ON t.product_id = i.product_id
                JOIN users u ON t.performed_by = u.user_id
                WHERE t.transaction_type = 'DEFECT' 
                AND t.transaction_date BETWEEN %s AND %s
                ORDER BY t.transaction_date DESC
            """
            cursor.execute(query, (f"{start} 00:00:00", f"{end} 23:59:59"))
            return cursor.fetchall()
        finally:
            if conn: conn.close()

    def get_user_activity(self, start, end):
        """Fetches login history from user_logins table"""
        conn = self.connect()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT l.login_id, u.username, l.login_time 
                FROM user_logins l
                JOIN users u ON l.user_id = u.user_id
                WHERE l.login_time BETWEEN %s AND %s
                ORDER BY l.login_time DESC
            """
            cursor.execute(query, (f"{start} 00:00:00", f"{end} 23:59:59"))
            return cursor.fetchall()
        finally:
            if conn: conn.close()