import sys
import bcrypt
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QStackedWidget, QLabel, QHBoxLayout, QCheckBox,
    QMainWindow, QInputDialog, QTableWidget, QTableWidgetItem
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from datetime import datetime


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="librarydb"
    )


class AdminLogin(QWidget):
    def __init__(self, admin_window):
        super().__init__()
        self.admin_window = admin_window
        layout = QVBoxLayout()

        self.title = QLabel("Admin Login")
        self.title.setFont(QFont("Arial", 16, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.admin_login)

        layout.addWidget(self.title)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.login_btn)
        self.setLayout(layout)

    def admin_login(self):
        user = self.username.text().strip()
        pwd = self.password.text().strip()

        if not user or not pwd:
            QMessageBox.warning(self, "Error", "Please enter credentials.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM admins WHERE username=%s", (user,))
        result = cursor.fetchone()
        if result and bcrypt.checkpw(pwd.encode(), result[0].encode()):
            QMessageBox.information(self, "Login", "Welcome, Admin!")
            self.admin_window.show_dashboard()
        else:
            QMessageBox.warning(self, "Error", "Invalid admin credentials.")
        cursor.close()
        conn.close()


class AdminDashboard(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.view_borrowed_btn = QPushButton("📚 View Borrowed Books")
        self.view_borrowed_btn.clicked.connect(self.view_borrowed)

        self.view_overdue_btn = QPushButton("⏰ View Overdue Books")
        self.view_overdue_btn.clicked.connect(self.view_overdue)

        self.add_book_btn = QPushButton("➕ Add Book")
        self.add_book_btn.clicked.connect(self.add_book)

        self.remove_book_btn = QPushButton("➖ Remove Book")
        self.remove_book_btn.clicked.connect(self.remove_book)

        self.table = QTableWidget()
        layout.addWidget(self.view_borrowed_btn)
        layout.addWidget(self.view_overdue_btn)
        layout.addWidget(self.add_book_btn)
        layout.addWidget(self.remove_book_btn)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def view_borrowed(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, book_title, due_date FROM borrowed_books")
        results = cursor.fetchall()
        self.display_table(results, ["User", "Book Title", "Due Date"])
        cursor.close()
        conn.close()

    def view_overdue(self):
        today = datetime.today().strftime('%Y-%m-%d')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, book_title, due_date FROM borrowed_books WHERE due_date < %s", (today,))
        results = cursor.fetchall()
        self.display_table(results, ["User", "Overdue Book", "Due Date"])
        cursor.close()
        conn.close()

    def add_book(self):
        title, ok1 = QInputDialog.getText(self, "Add Book", "Enter book title:")
        author, ok2 = QInputDialog.getText(self, "Add Book", "Enter author name:")
        if ok1 and ok2 and title and author:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO books (title, author) VALUES (%s, %s)", (title, author))
            conn.commit()
            QMessageBox.information(self, "Success", "Book added to catalog.")
            cursor.close()
            conn.close()

    def remove_book(self):
        title, ok = QInputDialog.getText(self, "Remove Book", "Enter exact book title:")
        if ok and title:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM books WHERE title = %s", (title,))
            conn.commit()
            QMessageBox.information(self, "Removed", "Book removed from catalog.")
            cursor.close()
            conn.close()

    def display_table(self, data, headers):
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(data):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))


class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Panel - KnowledgeHub")
        self.resize(700, 500)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_screen = AdminLogin(self)
        self.dashboard = AdminDashboard()

        self.stack.addWidget(self.login_screen)
        self.stack.addWidget(self.dashboard)

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminWindow()
    window.show()
    sys.exit(app.exec_())
