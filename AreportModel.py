# AreportModel.py - UPDATED with Validation Workflow
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
            conn = mysql.connector.connect(**self.db_config)
            if conn.is_connected():
                return conn
            return None
        except Error as e:
            print(f"Error connecting to DB: {e}")
            return None

    def get_all_saved_reports(self):
        """Fetch report history with proper user tracking"""
        conn = self.connect()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    r.report_id,
                    r.report_name,
                    r.report_type,
                    r.start_date,
                    r.end_date,
                    r.created_at as transaction_date,
                    r.report_status,
                    CONCAT(req.userFname, ' ', req.userLname) as requested_by,
                    CONCAT(proc.userFname, ' ', proc.userLname) as processed_by,
                    CONCAT(val.userFname, ' ', val.userLname) as validated_by,
                    r.validated_at
                FROM saved_reports r
                LEFT JOIN users req ON r.requested_by = req.user_id
                LEFT JOIN users proc ON r.processed_by = proc.user_id
                LEFT JOIN users val ON r.validated_by = val.user_id
                ORDER BY r.created_at DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching saved reports: {e}")
            return []
        finally:
            if conn: conn.close()

    def save_report_entry(self, rtype, start, end, user_data, transaction_id=None):
        """
        Log report generation with proper workflow tracking.

        Args:
            rtype: Report type
            start: Start date
            end: End date
            user_data: Full user dictionary with user_id and name info
            transaction_id: Optional transaction reference
        """
        conn = self.connect()
        if not conn: return False
        try:
            cursor = conn.cursor()
            report_name = f"{rtype} ({start} to {end})"

            # Extract user info
            user_id = user_data.get('user_id') if isinstance(user_data, dict) else None

            # For now, the person generating is both requester and processor
            # Later you can add a separate validation step
            query = """
                INSERT INTO saved_reports 
                (report_name, report_type, start_date, end_date, 
                 requested_by, processed_by, transaction_id, 
                 created_at, report_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), 'Processed')
            """
            cursor.execute(query, (
                report_name,
                rtype,
                start,
                end,
                user_id,  # requested_by
                user_id,  # processed_by
                transaction_id
            ))
            conn.commit()
            return True
        except Error as e:
            print(f"Error saving report log: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if conn: conn.close()

    def validate_report(self, report_id, validator_user_id):
        """
        Mark a report as validated by a supervisor/admin

        Args:
            report_id: ID of the report to validate
            validator_user_id: User ID of the person validating
        """
        conn = self.connect()
        if not conn: return False
        try:
            cursor = conn.cursor()
            query = """
                UPDATE saved_reports 
                SET validated_by = %s,
                    validated_at = NOW(),
                    report_status = 'Validated'
                WHERE report_id = %s
            """
            cursor.execute(query, (validator_user_id, report_id))
            conn.commit()
            return True
        except Error as e:
            print(f"Error validating report: {e}")
            return False
        finally:
            if conn: conn.close()

    # --- SPECIFIC REPORT DATA FETCHERS ---

    def get_stock_movement(self, start, end):
        """Get stock movement transactions with full user names"""
        conn = self.connect()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    DATE_FORMAT(t.transaction_date, '%Y-%m-%d %H:%i') as transaction_date,
                    t.transaction_type, 
                    i.product_name, 
                    i.brand,
                    t.quantity, 
                    t.remarks,
                    CONCAT(u.userFname, ' ', u.userLname) as processed_by
                FROM stock_transactions t
                JOIN inventory i ON t.product_id = i.product_id
                LEFT JOIN users u ON t.performed_by = u.user_id
                WHERE t.transaction_date BETWEEN %s AND %s
                ORDER BY t.transaction_date DESC
            """
            cursor.execute(query, (f"{start} 00:00:00", f"{end} 23:59:59"))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching Stock Movement: {e}")
            return []
        finally:
            if conn: conn.close()

    def get_inventory_status(self):
        """Get current inventory status"""
        conn = self.connect()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    product_id, 
                    product_name, 
                    brand, 
                    model, 
                    stock_quantity, 
                    status,
                    DATE_FORMAT(updated_at, '%Y-%m-%d %H:%i') as last_updated
                FROM inventory 
                ORDER BY product_id ASC
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching Inventory Status: {e}")
            return []
        finally:
            if conn: conn.close()

    def get_defective_report(self, start, end):
        """Get defective items report with full user names"""
        conn = self.connect()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    DATE_FORMAT(t.transaction_date, '%Y-%m-%d %H:%i') as transaction_date,
                    i.product_name, 
                    i.brand, 
                    t.quantity as defective_qty, 
                    t.remarks,
                    CONCAT(u.userFname, ' ', u.userLname) as reported_by
                FROM stock_transactions t
                JOIN inventory i ON t.product_id = i.product_id
                LEFT JOIN users u ON t.performed_by = u.user_id
                WHERE t.transaction_type = 'DEFECT' 
                  AND t.transaction_date BETWEEN %s AND %s
                ORDER BY t.transaction_date DESC
            """
            cursor.execute(query, (f"{start} 00:00:00", f"{end} 23:59:59"))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching Defective Report: {e}")
            return []
        finally:
            if conn: conn.close()

    def get_user_activity(self, start, end):
        """Get user login activity with full names"""
        conn = self.connect()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    l.login_id, 
                    CONCAT(u.userFname, ' ', u.userLname) as user_name,
                    u.role,
                    DATE_FORMAT(l.login_time, '%Y-%m-%d %H:%i') as login_time
                FROM user_logins l
                JOIN users u ON l.user_id = u.user_id
                WHERE l.login_time BETWEEN %s AND %s
                ORDER BY l.login_time DESC
            """
            cursor.execute(query, (f"{start} 00:00:00", f"{end} 23:59:59"))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching User Activity: {e}")
            return []
        finally:
            if conn: conn.close()