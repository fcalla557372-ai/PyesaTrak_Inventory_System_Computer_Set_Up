# ADBModel.py
import mysql.connector
from mysql.connector import Error

class DashboardModel:
    """Model for handling dashboard data - Inventory focused"""

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
        except Error:
            return None

    def get_total_products(self):
        conn = self.connect()
        if not conn: return 0
        try:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM inventory")
            return c.fetchone()[0]
        finally:
            conn.close()

    def get_low_stock_items_count(self):
        conn = self.connect()
        if not conn: return 0
        try:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM inventory WHERE stock_quantity <= 10 AND stock_quantity > 0")
            return c.fetchone()[0]
        finally:
            conn.close()

    def get_out_of_stock_count(self):
        conn = self.connect()
        if not conn: return 0
        try:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM inventory WHERE stock_quantity = 0")
            return c.fetchone()[0]
        finally:
            conn.close()

    # --- UPDATED: Fixes the "0 Defective" issue ---
    def get_defective_count(self):
        """
        Count items marked as Defective based on TRANSACTION HISTORY.
        Now consistent with Staff Dashboard logic.
        """
        conn = self.connect()
        if not conn: return 0
        try:
            c = conn.cursor()
            # Sum the quantity of all defect transactions
            c.execute("SELECT COALESCE(SUM(quantity), 0) FROM stock_transactions WHERE transaction_type = 'DEFECT'")
            return int(c.fetchone()[0])
        finally:
            conn.close()

    def get_stock_flow_summary(self):
        """Get total In vs Out quantities for TODAY"""
        conn = self.connect()
        if not conn: return {'in': 0, 'out': 0}
        try:
            c = conn.cursor(dictionary=True)
            # Updated to match Staff Dashboard's "Today" filter for consistency
            query = """
                SELECT 
                    SUM(CASE WHEN transaction_type = 'IN' THEN quantity ELSE 0 END) as stock_in,
                    SUM(CASE WHEN transaction_type = 'OUT' THEN quantity ELSE 0 END) as stock_out
                FROM stock_transactions 
                WHERE DATE(transaction_date) = CURDATE()
            """
            c.execute(query)
            res = c.fetchone()
            if res:
                return {'in': float(res['stock_in'] or 0), 'out': float(res['stock_out'] or 0)}
            return {'in': 0, 'out': 0}
        finally:
            conn.close()

    def get_recent_inventory_activities(self, limit=10):
        conn = self.connect()
        if not conn: return []
        try:
            c = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    t.transaction_date, 
                    DATE_FORMAT(t.transaction_date, '%Y-%m-%d %H:%i') as formatted_date,
                    t.transaction_type, 
                    i.product_name, 
                    u.username as performed_by
                FROM stock_transactions t
                JOIN inventory i ON t.product_id = i.product_id
                LEFT JOIN users u ON t.performed_by = u.user_id
                ORDER BY t.transaction_date DESC LIMIT %s
            """
            c.execute(query, (limit,))
            return c.fetchall()
        finally:
            conn.close()