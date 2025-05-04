import sys
import bcrypt
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QStackedWidget, QLabel, QHBoxLayout, QCheckBox,
    QMainWindow, QFrame, QSizePolicy, QScrollArea
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="LibraryDb"
    )


class StyledLineEdit(QLineEdit):
    def __init__(self, placeholder):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("padding: 8px; border-radius: 5px; border: 1px solid gray;")
        self.setFont(QFont("Arial", 10))


class SignupPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(12)
        form_container.setMaximumWidth(500)

        self.title = QLabel("Create Account")
        self.title.setFont(QFont("Arial", 16, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(self.title)

        self.username = StyledLineEdit("Username")
        form_layout.addWidget(self.username)

        self.password = StyledLineEdit("Password")
        self.password.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.password)

        self.confirm_password = StyledLineEdit("Confirm Password")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.confirm_password)

        self.show_password = QCheckBox("Show Password")
        self.show_password.stateChanged.connect(self.toggle_password_visibility)
        form_layout.addWidget(self.show_password)

        self.signup_button = QPushButton("Sign Up")
        self.signup_button.clicked.connect(self.signup)
        form_layout.addWidget(self.signup_button)

        self.switch_button = QPushButton("Already have an account? Log in")
        self.switch_button.clicked.connect(self.main_window.show_login)
        form_layout.addWidget(self.switch_button)

        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(form_container)
        h_layout.addStretch(1)

        main_layout.addStretch(1)
        main_layout.addLayout(h_layout)
        main_layout.addStretch(1)

        self.setLayout(main_layout)

    def toggle_password_visibility(self):
        mode = QLineEdit.Normal if self.show_password.isChecked() else QLineEdit.Password
        self.password.setEchoMode(mode)
        self.confirm_password.setEchoMode(mode)

    def signup(self):
        user = self.username.text().strip()
        pwd = self.password.text()
        confirm_pwd = self.confirm_password.text()

        if not user or not pwd or not confirm_pwd:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return
        if pwd != confirm_pwd:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
        if len(pwd) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters.")
            return

        hashed_pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user, hashed_pwd))
            conn.commit()
            QMessageBox.information(self, "Success", "Account created!")
            self.username.clear()
            self.password.clear()
            self.confirm_password.clear()
            self.main_window.show_login()
        except mysql.connector.errors.IntegrityError:
            QMessageBox.warning(self, "Error", "Username already exists.")
        finally:
            cursor.close()
            conn.close()

class LoginPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(12)
        form_container.setMaximumWidth(500)

        self.title = QLabel("Login")
        self.title.setFont(QFont("Arial", 16, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(self.title)

        self.username = StyledLineEdit("Username")
        form_layout.addWidget(self.username)

        self.password = StyledLineEdit("Password")
        self.password.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.password)

        self.show_password = QCheckBox("Show Password")
        self.show_password.stateChanged.connect(self.toggle_password_visibility)
        form_layout.addWidget(self.show_password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        form_layout.addWidget(self.login_button)

        self.switch_button = QPushButton("Don't have an account? Sign up")
        self.switch_button.clicked.connect(self.main_window.show_signup)
        form_layout.addWidget(self.switch_button)

        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(form_container)
        h_layout.addStretch(1)

        main_layout.addStretch(1)
        main_layout.addLayout(h_layout)
        main_layout.addStretch(1)

        self.setLayout(main_layout)

    def toggle_password_visibility(self):
        mode = QLineEdit.Normal if self.show_password.isChecked() else QLineEdit.Password
        self.password.setEchoMode(mode)

    def login(self):
        user = self.username.text().strip()
        pwd = self.password.text()

        if not user or not pwd:
            QMessageBox.warning(self, "Error", "Please enter username and password.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=%s", (user,))
        result = cursor.fetchone()

        if result and bcrypt.checkpw(pwd.encode('utf-8'), result[0].encode('utf-8')):
            QMessageBox.information(self, "Success", "Login successful!")
            self.username.clear()
            self.password.clear()
            self.main_window.show_dashboard(user)
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials.")

        cursor.close()
        conn.close()


class LibraryPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()
        label = QLabel("Welcome to the Library System")
        label.setFont(QFont("Arial", 14))
        layout.addWidget(label)
        self.setLayout(layout)


class DashboardPanel(QFrame):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()
        welcome_label = QLabel(f"Welcome, {self.username}!")
        welcome_label.setFont(QFont("Arial", 14))
        layout.addWidget(welcome_label)

        borrowed_books_label = QLabel("Borrowed Books:")
        borrowed_books_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(borrowed_books_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)

        # Example data
        books = [
            {"title": "Python Basics", "due_date": datetime.now() + timedelta(days=3)},
            {"title": "Data Science 101", "due_date": datetime.now() + timedelta(days=7)},
        ]

        for book in books:
            book_label = QLabel(f"{book['title']} - Due: {book['due_date'].strftime('%Y-%m-%d')}")
            self.scroll_layout.addWidget(book_label)

        self.scroll_area.setWidget(scroll_content)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Library Management System")
        self.resize(600, 400)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_page = LoginPage(self)
        self.signup_page = SignupPage(self)

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.signup_page)

    def show_login(self):
        self.stack.setCurrentWidget(self.login_page)

    def show_signup(self):
        self.stack.setCurrentWidget(self.signup_page)

    def show_dashboard(self, username):
        self.dashboard = DashboardPanel(username)
        self.stack.addWidget(self.dashboard)
        self.stack.setCurrentWidget(self.dashboard)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

