# Filename: Main.py
import sys
from PyQt6.QtWidgets import QApplication

# Import classes inside main to avoid circular import issues
# (Make sure these files are in the same folder)
from login_model import LoginModel
from login_view import LoginView
from login_controller import LoginController

def main():
    app = QApplication(sys.argv)

    # 1. Initialize the Model (Data)
    model = LoginModel()

    # 2. Initialize the View (UI Window)
    view = LoginView()

    # 3. Initialize the Controller (Connects Model & View)
    # Note: Your LoginController __init__ requires (view, model) arguments
    controller = LoginController(view, model)

    # 4. Show the Window
    controller.show()

    # 5. Execute the Application Loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()