# ManageUsersController.py - FULLY FUNCTIONAL
from ManageUsersModel import ManageUsersModel
from ManageUsersView import ManageUsersView, UserFormDialog
from PyQt6.QtWidgets import QMessageBox


class ManageUsersController:
    def __init__(self, user_data=None):
        self.model = ManageUsersModel()
        self.view = ManageUsersView()
        self.user_data = user_data

        # Filter Connections
        self.view.search_input.textChanged.connect(self.refresh_data)
        self.view.role_combo.currentTextChanged.connect(self.refresh_data)
        self.view.status_combo.currentTextChanged.connect(self.refresh_data)

        # Action Buttons
        self.view.add_user_clicked.connect(self.handle_add_user)
        self.view.delete_user_clicked.connect(self.handle_delete_user)
        self.view.edit_user_clicked.connect(self.handle_edit_user)

    def refresh_data(self):
        search = self.view.search_input.text()
        role = self.view.role_combo.currentText()
        status = self.view.status_combo.currentText()

        # Clean up combo box text "All Roles" -> "All"
        if "All" in role: role = "All"
        if "All" in status: status = "All"

        users = self.model.get_users(role, status, search)
        self.view.load_data(users)

    def handle_add_user(self):
        dialog = UserFormDialog(self.view)
        if dialog.exec():
            data = dialog.get_data()
            if not data['username'] or not data['password']:
                QMessageBox.warning(self.view, "Error", "Username and Password are required!")
                return

            if self.model.add_user(data):
                QMessageBox.information(self.view, "Success", "User added successfully!")
                self.refresh_data()
            else:
                QMessageBox.critical(self.view, "Error", "Failed to add user. Username might be taken.")

    def handle_edit_user(self, uid):
        user = self.model.get_user_by_id(uid)
        if not user:
            QMessageBox.warning(self.view, "Error", "User not found.")
            return

        dialog = UserFormDialog(self.view, user)
        if dialog.exec():
            data = dialog.get_data()
            # If password is empty, remove it from update data
            if not data['password']:
                del data['password']

            if self.model.update_user(uid, data):
                QMessageBox.information(self.view, "Success", "User updated successfully!")
                self.refresh_data()
            else:
                QMessageBox.critical(self.view, "Error", "Failed to update user.")

    def handle_delete_user(self, uid):
        # Prevent deleting self
        if self.user_data and uid == self.user_data['user_id']:
            QMessageBox.warning(self.view, "Error", "You cannot delete your own account!")
            return

        reply = QMessageBox.question(self.view, "Confirm Delete",
                                     "Are you sure you want to delete this user?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if self.model.delete_user(uid):
                QMessageBox.information(self.view, "Success", "User deleted.")
                self.refresh_data()
            else:
                QMessageBox.critical(self.view, "Error", "Failed to delete user.")