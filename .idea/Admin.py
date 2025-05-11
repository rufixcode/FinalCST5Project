# Enhanced Admin Library System UI
import sys
import bcrypt
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox,
    QStackedWidget, QLabel, QHBoxLayout, QInputDialog, QTableWidget, QTableWidgetItem,
    QMainWindow, QDialog, QFormLayout, QDialogButtonBox, QFrame, QScrollArea,
    QDateEdit, QDoubleSpinBox, QComboBox, QCheckBox, QGroupBox
)
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon
from PyQt5.QtCore import Qt, QDate
from datetime import datetime, timedelta
from functools import partial
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp
from PyQt5.QtCore import QTimer
from datetime import date

# Consistent styling
BUTTON_STYLE = """
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
    QPushButton:pressed {
        background-color: #3e8e41;
    }
"""

TABLE_STYLE = """
    QTableWidget {
        alternate-background-color: #f0f0f0;
        border: 1px solid #d0d0d0;
    }
    QHeaderView::section {
        background-color: #4CAF50;
        color: white;
        padding: 4px;
        font-weight: bold;
    }
"""

def get_db_connection():
    return mysql.connector.connect(host="localhost", user="root", password="", database="librarydb")


class BookDialog(QDialog):
    def __init__(self, parent=None, book_data=None):
        super().__init__(parent)
        self.setWindowTitle("Book Details")
        self.resize(400, 200)
        
        layout = QFormLayout(self)
        
        self.title_edit = QLineEdit()
        self.author_edit = QLineEdit()


        self.available_check = QCheckBox("Available")
        self.available_check.setChecked(True)
        
        layout.addRow("Title:", self.title_edit)
        layout.addRow("Author:", self.author_edit)
        layout.addRow("Status:", self.available_check)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        # Fill data if editing
        if book_data:
            self.title_edit.setText(book_data[1])
            self.author_edit.setText(book_data[2])
            self.available_check.setChecked(book_data[3] == 1)
            
    def get_book_data(self):
        return {
            'title': self.title_edit.text(),
            'author': self.author_edit.text(),
            'available': 1 if self.available_check.isChecked() else 0
        }


class BorrowedBookDialog(QDialog):
    def __init__(self, parent=None, borrowed_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Borrowed Book")
        self.resize(400, 200)
        
        layout = QFormLayout(self)
        
        self.username_edit = QLineEdit()
        self.username_edit.setReadOnly(True)
        
        self.book_title_edit = QLineEdit()
        self.book_title_edit.setReadOnly(True)
        
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate().addDays(14))
        
        self.penalty_edit = QDoubleSpinBox()
        self.penalty_edit.setRange(0, 1000)
        self.penalty_edit.setSingleStep(0.5)
        self.penalty_edit.setPrefix("$")
        
        # Add claimed checkbox
        self.claimed_checkbox = QCheckBox("Book Claimed")
        
        layout.addRow("Username:", self.username_edit)
        layout.addRow("Book Title:", self.book_title_edit)
        layout.addRow("Due Date:", self.due_date_edit)
        layout.addRow("Penalty:", self.penalty_edit)
        layout.addRow("Status:", self.claimed_checkbox)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        # Fill data if editing
        if borrowed_data:
            self.borrow_id = borrowed_data[0]
            self.username_edit.setText(borrowed_data[1])
            self.book_title_edit.setText(borrowed_data[3])

            due_date = borrowed_data[4]
            if isinstance(due_date, date):
                qdate = QDate(due_date.year, due_date.month, due_date.day)
            else:
                qdate = QDate.fromString(str(due_date), "yyyy-MM-dd")

            self.due_date_edit.setDate(qdate)
            
            # Set claimed status if it's available in the data (position 5)
            if len(borrowed_data) > 5:
                self.claimed_checkbox.setChecked(borrowed_data[5] == 1)
            
    def get_borrowed_data(self):
        return {
            'due_date': self.due_date_edit.date().toString("yyyy-MM-dd"),
            'penalty': self.penalty_edit.value(),
            'is_claimed': 1 if self.claimed_checkbox.isChecked() else 0
        }



class MemberDialog(QDialog):
    def __init__(self, parent=None, member_data=None):
        super().__init__(parent)
        self.setWindowTitle("Member Details")
        self.resize(400, 200)
        
        layout = QFormLayout(self)
        
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        
        # Only show password fields when adding new member
        if not member_data:
            layout.addRow("Username:", self.username_edit)
            layout.addRow("Password:", self.password_edit)
        else:
            layout.addRow("Username:", self.username_edit)
            self.password_edit = None  # Don't edit password directly
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        # Fill data if editing
        if member_data:
            self.member_id = member_data[0]
            self.username_edit.setText(member_data[1])
            
    def get_member_data(self):
        data = {'username': self.username_edit.text()}
        if self.password_edit:
            data['password'] = self.password_edit.text()
        return data


class AdminDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Admin")
        self.resize(400, 220)
        
        layout = QFormLayout(self)
        
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        
        layout.addRow("Username:", self.username_edit)
        layout.addRow("Password:", self.password_edit)
        layout.addRow("Confirm Password:", self.confirm_password_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
    def validate_and_accept(self):
        if self.password_edit.text() != self.confirm_password_edit.text():
            QMessageBox.warning(self, "Error", "Passwords don't match!")
            return
        
        if not self.username_edit.text() or not self.password_edit.text():
            QMessageBox.warning(self, "Error", "All fields are required!")
            return
            
        self.accept()
        
    def get_admin_data(self):
        return {
            'username': self.username_edit.text(),
            'password': self.password_edit.text()
        }


class CredentialDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Super Admin Verification")
        layout = QFormLayout(self)

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)

        layout.addRow("Username:", self.username)
        layout.addRow("Password:", self.password)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_credentials(self):
        return self.username.text(), self.password.text()


class AdminLogin(QWidget):
    def __init__(self, admin_window):
        super().__init__()
        self.admin_window = admin_window
        layout = QVBoxLayout()

        self.title = QLabel("Admin Login")
        self.title.setFont(QFont("Arial", 18, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.admin_login)
        self.login_btn.setStyleSheet(BUTTON_STYLE)

        form = QVBoxLayout()
        form.setAlignment(Qt.AlignCenter)
        form.setSpacing(10)
        form.addWidget(self.title)
        form.addWidget(self.username)
        form.addWidget(self.password)
        form.addWidget(self.login_btn)

        wrapper = QHBoxLayout()
        wrapper.addStretch()
        wrapper.addLayout(form)
        wrapper.addStretch()

        layout.addStretch()
        layout.addLayout(wrapper)
        layout.addStretch()

        self.setLayout(layout)

    def admin_login(self):
        user = self.username.text().strip()
        pwd = self.password.text().strip()

        if not user or not pwd:
            QMessageBox.warning(self, "Error", "Please enter credentials.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT adminid, password FROM admins WHERE username=%s", (user,))
        result = cursor.fetchone()

        if result and result[1] and bcrypt.checkpw(pwd.encode(), result[1].encode()):
            self.admin_window.current_admin_id = result[0]
            self.admin_window.current_admin_username = user
            self.admin_window.show_dashboard()
            QTimer.singleShot(0, self.admin_window.show_dashboard)
            print("Login attempt for:", user)
            print("DB hash:", result[1])
        else:
            QMessageBox.warning(self, "Error", "Invalid admin credentials.")

        cursor.close()
        conn.close()


class AdminDashboard(QWidget):
    def __init__(self, admin_window):
        super().__init__()
        self.admin_window = admin_window
        self.main_layout = QHBoxLayout(self)

        # Create sidebar
        self.sidebar = QVBoxLayout()
        self.sidebar.setAlignment(Qt.AlignTop)
        self.sidebar.setSpacing(5)

        # Create sidebar buttons
        buttons = {
            "View All Books": self.view_all_books,
            "View Borrowed Books": self.view_borrowed,
            "View Overdue Books": self.view_overdue,
            "View Members": self.view_members,
            "Manage Admins": self.admin_window.manage_admins,
            "Logout": self.admin_window.logout
        }

        for name, method in buttons.items():
            if name == "Manage Admins":
                self.sidebar.addStretch()


            btn = QPushButton(name)
            btn.clicked.connect(method)
            btn.setFixedHeight(40)
            btn.setStyleSheet(BUTTON_STYLE)
            self.sidebar.addWidget(btn)

        sidebar_widget = QFrame()
        sidebar_widget.setLayout(self.sidebar)
        sidebar_widget.setFixedWidth(200)

        # Create main content area
        self.content_area = QVBoxLayout()
        
        # Add header and action buttons area
        self.header_layout = QHBoxLayout()
        self.page_title = QLabel("Dashboard")
        self.page_title.setFont(QFont("Arial", 16, QFont.Bold))
        self.header_layout.addWidget(self.page_title)
        self.header_layout.addStretch()
        
        # Action buttons container
        self.action_buttons = QHBoxLayout()
        self.header_layout.addLayout(self.action_buttons)
        
        self.content_area.addLayout(self.header_layout)
        
        # Add table
        self.table = QTableWidget()
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        self.content_area.addWidget(self.table)
        
        # Create main content widget
        content_widget = QFrame()
        content_widget.setLayout(self.content_area)
        
        # Add sidebar and content to main layout
        self.main_layout.addWidget(sidebar_widget)
        self.main_layout.addWidget(content_widget)

    def clear_action_buttons(self):
        # Clear existing action buttons
        while self.action_buttons.count():
            item = self.action_buttons.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

    def display_table(self, data, headers):
        self.table.setSortingEnabled(False)
        self.table.clearContents()
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(data):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setSortingEnabled(True)

    def view_borrowed(self):
        self.page_title.setText("Borrowed Books")
        self.clear_action_buttons()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, id, book_title, due_date, is_claimed FROM borrowed_books")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        headers = ["ID", "User", "Book ID", "Book Title", "Due Date", "Claimed", "Actions"]
        self.table.setSortingEnabled(False)
        self.table.clearContents()
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        
        for i, row in enumerate(data):
            for j in range(5):
                self.table.setItem(i, j, QTableWidgetItem(str(row[j])))
            
            # Add claimed status
            claimed_status = "Yes" if row[5] == 1 else "No"
            claimed_item = QTableWidgetItem(claimed_status)
            if row[5] == 1:
                claimed_item.setForeground(QColor("green"))
            else:
                claimed_item.setForeground(QColor("blue"))
            self.table.setItem(i, 5, claimed_item)

            from functools import partial
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet(BUTTON_STYLE)
            edit_btn.clicked.connect(partial(self.edit_borrowed_book, row))
            
            return_btn = QPushButton("Return")
            return_btn.setStyleSheet(BUTTON_STYLE)
            return_btn.clicked.connect(partial(self.return_book, row[0]))

            action_widget = QWidget(self.table)
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(return_btn)
            action_widget.setLayout(action_layout)

            self.table.setCellWidget(i, 6, action_widget)

            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()
            self.table.setSortingEnabled(True)

    
    def edit_borrowed_book(self, data):
        dialog = BorrowedBookDialog(self, data)


        if dialog.exec_() == QDialog.Accepted:
            borrowed_data = dialog.get_borrowed_data()
            print(borrowed_data)

            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                    "UPDATE borrowed_books SET due_date = %s, is_claimed = %s WHERE id = %s",
                    (borrowed_data['due_date'], borrowed_data['is_claimed'], data[0])
                    )
                    conn.commit()

                QMessageBox.information(self, "Success", "Borrowed book updated successfully!")
                self.view_borrowed()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update borrowed book: {e}")





    def return_book(self, borrow_id):
        reply = QMessageBox.question(
            self, "Confirm Return", 
            "Are you sure you want to mark this book as returned?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get book ID first
            cursor.execute("SELECT id FROM borrowed_books WHERE id = %s", (borrow_id,))
            id = cursor.fetchone()[0]
            
            # Update book availability
            cursor.execute("UPDATE books SET available = 1 WHERE id = %s", (id,))
            
            # Remove borrowed record
            cursor.execute("DELETE FROM borrowed_books WHERE id = %s", (borrow_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            QMessageBox.information(self, "Success", "Book has been returned successfully!")
            self.view_borrowed()

    def view_overdue(self):
        self.page_title.setText("Overdue Books")
        self.clear_action_buttons()

        try:
            today = datetime.today().strftime('%Y-%m-%d')
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, id, book_title, due_date FROM borrowed_books WHERE due_date < %s",
                (today,)
            )
            data = cursor.fetchall()
            cursor.close()
            conn.close()

            headers = ["ID", "User", "Book ID", "Overdue Book", "Due Date", "Days Overdue", "Est. Penalty", "Actions"]
            self.table.setSortingEnabled(False)
            self.table.clearContents()
            self.table.setRowCount(len(data))
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)

            today_date = datetime.today()

            for i, row in enumerate(data):
                for j in range(5):
                    self.table.setItem(i, j, QTableWidgetItem(str(row[j])))

                # Calculate days overdue
                due_date = datetime.strptime(str(row[4]), "%Y-%m-%d")
                days_overdue = (today_date - due_date).days
                self.table.setItem(i, 5, QTableWidgetItem(str(days_overdue)))

                # Calculate penalty ($0.50 per day)
                penalty = days_overdue * 0.5
                self.table.setItem(i, 6, QTableWidgetItem(f"${penalty:.2f}"))

                # Add action buttons
                edit_btn = QPushButton("Edit")
                edit_btn.setStyleSheet(BUTTON_STYLE)
                edit_btn.clicked.connect(partial(self.edit_borrowed_book, row))

                collect_btn = QPushButton("Collect & Return")
                collect_btn.setStyleSheet(BUTTON_STYLE)
                collect_btn.clicked.connect(partial(self.collect_and_return, row[0], penalty))

                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(0, 0, 0, 0)
                action_layout.addWidget(edit_btn)
                action_layout.addWidget(collect_btn)
                action_widget.setLayout(action_layout)

                self.table.setCellWidget(i, 7, action_widget)

            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()
            self.table.setSortingEnabled(True)
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error displaying overdue books: {e}")
    
    def collect_and_return(self, borrow_id, penalty):
        reply = QMessageBox.question(
            self, 
            "Confirm Collection", 
            f"Collect ${penalty:.2f} penalty and mark as returned?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get book ID first
            cursor.execute("SELECT id FROM borrowed_books WHERE id = %s", (borrow_id,))
            id = cursor.fetchone()[0]
            
            # Update book availability
            cursor.execute("UPDATE books SET available = 1 WHERE id = %s", (id,))
            
            # Remove borrowed record
            cursor.execute("DELETE FROM borrowed_books WHERE id = %s", (borrow_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            QMessageBox.information(
                self, 
                "Success", 
                f"Penalty of ${penalty:.2f} collected and book has been returned!"
            )
            self.view_overdue()

    def view_all_books(self):
        self.page_title.setText("All Books")
        self.clear_action_buttons()
        
        # Add book button
        add_book_btn = QPushButton("Add Book")
        add_book_btn.setStyleSheet(BUTTON_STYLE)
        add_book_btn.clicked.connect(self.add_book)
        self.action_buttons.addWidget(add_book_btn)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author, available FROM books")
        data = cursor.fetchall()
        
        cursor.execute("SELECT DISTINCT id FROM borrowed_books")
        borrowed_ids = set(row[0] for row in cursor.fetchall())
        cursor.close()
        conn.close()
        
        headers = ["ID", "Title", "Author", "Available", "Actions"]
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(data):
            for j in range(4):
                if j == 3:  # Available column
                    status = "Yes" if row[j] == 1 else "No"
                    self.table.setItem(i, j, QTableWidgetItem(status))
                else:
                    self.table.setItem(i, j, QTableWidgetItem(str(row[j])))
            
            # Add action buttons
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(5)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet(BUTTON_STYLE)
            edit_btn.clicked.connect(lambda _, idx=i, data=row: self.edit_book(data))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet(BUTTON_STYLE)
            delete_btn.clicked.connect(lambda _, idx=i, id=row[0]: self.delete_book(id))
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            
            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(i, 4, action_widget)
        
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def add_book(self):
        dialog = BookDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            book_data = dialog.get_book_data()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO books (title, author, available) VALUES (%s, %s, %s)",
                (book_data['title'], book_data['author'], book_data['available'])
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            QMessageBox.information(self, "Success", "Book added successfully!")
            self.view_all_books()
    
    def edit_book(self, book_data):
        dialog = BookDialog(self, book_data)
        if dialog.exec_() == QDialog.Accepted:
            updated_data = dialog.get_book_data()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE books SET title = %s, author = %s, available = %s WHERE id = %s",
                (updated_data['title'], updated_data['author'], updated_data['available'], book_data[0])
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            QMessageBox.information(self, "Success", "Book updated successfully!")
            self.view_all_books()
    
    def delete_book(self, id):
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            "Are you sure you want to delete this book?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if book is borrowed
            cursor.execute("SELECT COUNT(*) FROM borrowed_books WHERE id = %s", (id,))
            if cursor.fetchone()[0] > 0:
                QMessageBox.warning(
                    self, 
                    "Error", 
                    "This book is currently borrowed and cannot be deleted!"
                )
                cursor.close()
                conn.close()
                return
            
            cursor.execute("DELETE FROM books WHERE id = %s", (id,))
            conn.commit()
            cursor.close()
            conn.close()
            
            QMessageBox.information(self, "Success", "Book deleted successfully!")
            self.view_all_books()
            

    def view_members(self):
        self.page_title.setText("Library Members")
        self.clear_action_buttons()
        
        # Add member button
        add_member_btn = QPushButton("Add Member")
        add_member_btn.setStyleSheet(BUTTON_STYLE)
        add_member_btn.clicked.connect(self.add_member)
        self.action_buttons.addWidget(add_member_btn)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users")
        data = cursor.fetchall()
        
        # For each member, get their borrowed books count
        for i, row in enumerate(data):
            cursor.execute("SELECT COUNT(*) FROM borrowed_books WHERE username = %s", (row[1],))
            borrowed_count = cursor.fetchone()[0]
            data[i] = data[i] + (borrowed_count,)
        
        cursor.close()
        conn.close()
        
        headers = ["ID", "Username", "Books Borrowed", "Actions"]
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        for i, row in enumerate(data):
            for j in range(3):
                self.table.setItem(i, j, QTableWidgetItem(str(row[j])))
            
            # Add action buttons
            action_layout = QHBoxLayout()
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet(BUTTON_STYLE)
            edit_btn.clicked.connect(lambda _, idx=i, data=row: self.edit_member(data))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet(BUTTON_STYLE)
            delete_btn.clicked.connect(lambda _, idx=i, id=row[0], name=row[1]: self.delete_member(id, name))
            
            view_books_btn = QPushButton("View Books")
            view_books_btn.setStyleSheet(BUTTON_STYLE)
            view_books_btn.clicked.connect(lambda _, username=row[1]: self.view_member_books(username))
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addWidget(view_books_btn)
            
            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(i, 3, action_widget)
    
    def add_member(self):
        dialog = MemberDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            member_data = dialog.get_member_data()
            
            if not member_data['username'] or not member_data['password']:
                QMessageBox.warning(self, "Error", "All fields are required!")
                return
            
            hashed_password = bcrypt.hashpw(member_data['password'].encode(), bcrypt.gensalt()).decode()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    (member_data['username'], hashed_password)
                )
                conn.commit()
                QMessageBox.information(self, "Success", "Member added successfully!")
            except mysql.connector.IntegrityError:
                QMessageBox.warning(self, "Error", "Username already exists!")
            
            cursor.close()
            conn.close()
            self.view_members()
    
    def edit_member(self, member_data):
        dialog = MemberDialog(self, member_data)
        if dialog.exec_() == QDialog.Accepted:
            updated_data = dialog.get_member_data()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute(
                    "UPDATE users SET username = %s WHERE id = %s",
                    (updated_data['username'], member_data[0])
                )
                
                # Update username in borrowed_books table
                cursor.execute(
                    "UPDATE borrowed_books SET username = %s WHERE username = %s",
                    (updated_data['username'], member_data[1])
                )
                conn.commit()
                QMessageBox.information(self, "Success", "Member updated successfully!")
            except mysql.connector.IntegrityError:
                QMessageBox.warning(self, "Error", "Username already exists!")
            
            cursor.close()
            conn.close()
            self.view_members()
    
    def delete_member(self, member_id, username):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if member has borrowed books
        cursor.execute("SELECT COUNT(*) FROM borrowed_books WHERE username = %s", (username,))
        borrowed_count = cursor.fetchone()[0]
        
        if borrowed_count > 0:
            QMessageBox.warning(
                self, 
                "Error", 
                f"This member has {borrowed_count} borrowed books and cannot be deleted!"
            )
            cursor.close()
            conn.close()
            return
        
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            "Are you sure you want to delete this member?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            cursor.execute("DELETE FROM users WHERE id = %s", (member_id,))
            conn.commit()
            QMessageBox.information(self, "Success", "Member deleted successfully!")
            
        cursor.close()
        conn.close()
        self.view_members()
    
    def view_member_books(self, username):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Books Borrowed by {username}")
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        table = QTableWidget()
        table.setStyleSheet(TABLE_STYLE)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT book_title, due_date, is_claimed FROM borrowed_books WHERE username = %s", 
            (username,)
        )
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        headers = ["Book Title", "Due Date", "Status", "Claimed"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(data))
        
        today = datetime.today().date()
        
        for i, (title, due_date, is_claimed) in enumerate(data):
            table.setItem(i, 0, QTableWidgetItem(title))
            table.setItem(i, 1, QTableWidgetItem(str(due_date)))
            
            due_date_obj = datetime.strptime(str(due_date), "%Y-%m-%d").date()
            status = "On Time"
            if due_date_obj < today:
                status = "Overdue"
                days_overdue = (today - due_date_obj).days
                penalty = days_overdue * 0.5
                status += f" ({days_overdue} days, ${penalty:.2f} penalty)"
            
            status_item = QTableWidgetItem(status)
            if "Overdue" in status:
                status_item.setForeground(QColor("red"))
            else:
                status_item.setForeground(QColor("green"))
            table.setItem(i, 2, status_item)
            
            # Add claimed status
            claimed_status = "Yes" if is_claimed == 1 else "No"
            claimed_item = QTableWidgetItem(claimed_status)
            if is_claimed == 1:
                claimed_item.setForeground(QColor("green"))
            else:
                claimed_item.setForeground(QColor("blue"))
            table.setItem(i, 3, claimed_item)
        
        table.resizeColumnsToContents()
        layout.addWidget(table)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(BUTTON_STYLE)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)
        
        dialog.exec_()


class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KnowledgeHub Admin Panel")
        self.setGeometry(300, 150, 1000, 600)

        self.current_admin_id = None
        self.current_admin_username = None

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_screen = AdminLogin(self)
        self.dashboard = AdminDashboard(self)

        self.stack.addWidget(self.login_screen)
        self.stack.addWidget(self.dashboard)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Confirm Exit", "Do you really want to close the app?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard)
        self.dashboard.view_all_books()  # Default view

    def show_login(self):
        self.stack.setCurrentWidget(self.login_screen)

    def logout(self):
        self.current_admin_id = None
        self.current_admin_username = None
        self.show_login()

    def manage_admins(self):
        dialog = CredentialDialog()
        if dialog.exec_() == QDialog.Accepted:
            user, pwd = dialog.get_credentials()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT adminid, password FROM admins WHERE username=%s", (user,))
            result = cursor.fetchone()
            if result and result[0] == 2 and bcrypt.checkpw(pwd.encode(), result[1].encode()):
                self._show_admin_management()
            else:
                QMessageBox.warning(self, "Access Denied", "Invalid or unauthorized credentials.")
            cursor.close()
            conn.close()
    
    def _show_admin_management(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Admins")
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Add admin button
        add_admin_btn = QPushButton("Add Admin")
        add_admin_btn.setStyleSheet(BUTTON_STYLE)
        add_admin_btn.clicked.connect(lambda: self._add_admin(dialog))
        layout.addWidget(add_admin_btn, alignment=Qt.AlignLeft)
        
        # Admin table
        table = QTableWidget()
        table.setStyleSheet(TABLE_STYLE)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT adminid, username FROM admins WHERE adminid != 2")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        headers = ["ID", "Username", "Actions"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(data))
        
        for i, (admin_id, username) in enumerate(data):
            table.setItem(i, 0, QTableWidgetItem(str(admin_id)))
            table.setItem(i, 1, QTableWidgetItem(username))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet(BUTTON_STYLE)
            delete_btn.clicked.connect(lambda _, id=admin_id: self._delete_admin(id, dialog))
            
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(delete_btn)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            table.setCellWidget(i, 2, btn_widget)
        
        table.resizeColumnsToContents()
        layout.addWidget(table)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(BUTTON_STYLE)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)
        
        dialog.exec_()
    
    def _add_admin(self, parent_dialog):
        dialog = AdminDialog(parent_dialog)
        if dialog.exec_() == QDialog.Accepted:
            admin_data = dialog.get_admin_data()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                hashed = bcrypt.hashpw(admin_data['password'].encode(), bcrypt.gensalt()).decode()
                cursor.execute(
                    "INSERT INTO admins (username, password) VALUES (%s, %s)", 
                    (admin_data['username'], hashed)
                )
                conn.commit()
                QMessageBox.information(parent_dialog, "Success", "Admin added successfully!")
                
                # Refresh admin list
                parent_dialog.close()
                self._show_admin_management()
            except mysql.connector.IntegrityError:
                QMessageBox.warning(parent_dialog, "Error", "Username already exists!")
            
            cursor.close()
            conn.close()
    
    def _delete_admin(self, admin_id, parent_dialog):
        reply = QMessageBox.question(
            parent_dialog, 
            "Confirm Deletion", 
            "Are you sure you want to delete this admin?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM admins WHERE adminid = %s", (admin_id,))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Refresh admin list
            parent_dialog.close()
            self._show_admin_management()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#e0f7fa"))
    palette.setColor(QPalette.Base, QColor("#ffffff"))
    app.setPalette(palette)

    window = AdminWindow()
    window.show()
    sys.exit(app.exec_())