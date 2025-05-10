import sys
import bcrypt
import mysql.connector
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QStackedWidget, QLabel, QHBoxLayout, QCheckBox,
    QMainWindow, QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt




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
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(18)
        form_container.setMaximumWidth(450)
        form_container.setStyleSheet("""
                background-color: #fefefe;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            """)

        # Optional logo
        # logo = QLabel()
        # logo.setPixmap(QPixmap("logo.png").scaled(80, 80, Qt.KeepAspectRatio))
        # logo.setAlignment(Qt.AlignCenter)
        # form_layout.addWidget(logo)

        self.title = QLabel("Create Your Account")
        self.title.setFont(QFont("Segoe UI", 16, QFont.Bold))
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
        self.show_password.setStyleSheet("font-size: 12px;")
        self.show_password.stateChanged.connect(self.toggle_password_visibility)
        form_layout.addWidget(self.show_password)

        self.signup_button = QPushButton("Sign Up")
        self.signup_button.setCursor(Qt.PointingHandCursor)
        self.signup_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 8px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
        self.signup_button.clicked.connect(self.signup)
        form_layout.addWidget(self.signup_button)

        self.switch_button = QPushButton("Already have an account? Log in")
        self.switch_button.setCursor(Qt.PointingHandCursor)
        self.switch_button.setStyleSheet("color: #555; background: none; border: none;")
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
            self.main_window.current_user = user
            self.main_window.Main_screen()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials.")

        cursor.close()
        conn.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Library Management System")
        self.resize(600, 400)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.current_user = None

        self.login_page = LoginPage(self)
        self.signup_page = SignupPage(self)
        self.blank_screen = QWidget()
        self.blank_screen.setStyleSheet("background-color: white;")

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.signup_page)
        self.stack.addWidget(self.blank_screen)

    def show_home(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author FROM books WHERE id NOT IN (SELECT book_id FROM borrowed_books)")
        books = cursor.fetchall()
        cursor.close()
        conn.close()

        home_panel = QWidget()
        main_layout = QVBoxLayout(home_panel)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        # Header section with search bar
        header_container = QWidget()
        header_container.setStyleSheet("background-color: #f5f5f5; border-radius: 12px; padding: 10px;")
        header_layout = QHBoxLayout(header_container)

        title = QLabel("Library Catalog")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")

        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search by title, author, or genre...")
        search_bar.setStyleSheet("""
            padding: 8px 12px;
            border-radius: 18px;
            border: 1px solid #bdc3c7;
            background-color: white;
            font-size: 13px;
        """)
        search_bar.setMinimumWidth(300)
        search_bar.setMaximumWidth(400)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(search_bar)

        main_layout.addWidget(header_container)

        # "Available Books" label
        section_label = QLabel("Available Books")
        section_label.setFont(QFont("Segoe UI", 14))
        section_label.setStyleSheet("color: #34495e; margin-top: 10px;")
        main_layout.addWidget(section_label)

        # Create a flow layout using a grid
        books_container = QWidget()
        books_container.setStyleSheet("background-color: white;")
        grid_layout = QHBoxLayout(books_container)
        grid_layout.setSpacing(20)

        scrollArea = QWidget()
        scroll_layout = QVBoxLayout(scrollArea)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # Create a row container that will wrap books
        flow_container = QWidget()
        flow_layout = QHBoxLayout(flow_container)
        flow_layout.setSpacing(15)
        flow_layout.setAlignment(Qt.AlignLeft)

        if books:
            book_counter = 0
            row_limit = 3  # Number of books per row

            for book_id, book_title, author in books:
                # Create book card
                book_card = QWidget()
                book_card.setFixedWidth(220)
                book_card.setMinimumHeight(280)
                book_card.setStyleSheet("""
                    background-color: white;
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                """)

                card_layout = QVBoxLayout(book_card)
                card_layout.setContentsMargins(0, 0, 0, 0)

                # Book cover placeholder
                cover = QLabel()
                cover.setFixedHeight(140)
                cover.setStyleSheet(f"""
                    background-color: #{hash(book_title) % 0xffffff:06x};
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                """)
                cover_layout = QVBoxLayout(cover)
                cover_layout.setAlignment(Qt.AlignCenter)

                book_icon = QLabel("📚")
                book_icon.setFont(QFont("Arial", 24))
                book_icon.setStyleSheet("background-color: transparent; color: rgba(255, 255, 255, 0.8);")
                cover_layout.addWidget(book_icon)

                # Book details
                details_container = QWidget()
                details_layout = QVBoxLayout(details_container)
                details_layout.setContentsMargins(15, 15, 15, 15)
                details_layout.setSpacing(5)

                title_label = QLabel(book_title)
                title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
                title_label.setWordWrap(True)
                title_label.setStyleSheet("color: #333;")

                author_label = QLabel(f"by {author}")
                author_label.setFont(QFont("Segoe UI", 9))
                author_label.setStyleSheet("color: #555;")
                author_label.setWordWrap(True)

                status_label = QLabel("Available")
                status_label.setFont(QFont("Segoe UI", 8))
                status_label.setStyleSheet("color: #27ae60; font-weight: bold;")

                borrow_btn = QPushButton("Borrow Book")
                borrow_btn.setCursor(Qt.PointingHandCursor)
                borrow_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border-radius: 15px;
                        padding: 8px;
                        font-weight: bold;
                        font-size: 10px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                borrow_btn.clicked.connect(lambda _, b_id=book_id, b_title=book_title: self.borrow_book(b_id, b_title))

                details_layout.addWidget(title_label)
                details_layout.addWidget(author_label)
                details_layout.addWidget(status_label)
                details_layout.addWidget(borrow_btn)

                card_layout.addWidget(cover)
                card_layout.addWidget(details_container)

                flow_layout.addWidget(book_card)
                book_counter += 1

                # Create a new row after reaching the limit
                if book_counter % row_limit == 0 and book_counter < len(books):
                    scroll_layout.addWidget(flow_container)
                    flow_container = QWidget()
                    flow_layout = QHBoxLayout(flow_container)
                    flow_layout.setSpacing(15)
                    flow_layout.setAlignment(Qt.AlignLeft)

            # Add the last row if it's not empty
            scroll_layout.addWidget(flow_container)

        else:
            empty_label = QLabel("No books are currently available in the library.")
            empty_label.setStyleSheet("color: #7f8c8d; font-size: 14px; margin: 40px;")
            empty_label.setAlignment(Qt.AlignCenter)
            scroll_layout.addWidget(empty_label)

        grid_layout.addWidget(scrollArea)
        main_layout.addWidget(books_container, 1)

        # Clear old widgets
        for i in reversed(range(self.main_panel_layout.count())):
            widget = self.main_panel_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.main_panel_layout.addWidget(home_panel)

    def show_login(self):
        self.stack.setCurrentWidget(self.login_page)

    def show_signup(self):
        self.stack.setCurrentWidget(self.signup_page)

    def logout_clicked(self):
        self.stack.setCurrentWidget(self.login_page)
        self.showNormal()
        QMessageBox.information(self, "Success", "Logout successful!")

    def borrow_book(self, book_id, book_title):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
            cursor.execute("""
                INSERT INTO borrowed_books (username, book_id, book_title, due_date)
                VALUES (%s, %s, %s, %s)
            """, (self.current_user, book_id, book_title, due_date))
            conn.commit()
            QMessageBox.information(self, "Success", f"You borrowed '{book_title}'. Due on {due_date}.")
            self.show_home()  # Refresh the list
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def show_borrowed_books(self):
     try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT book_title, due_date FROM borrowed_books
            WHERE username = %s
        """, (self.current_user,))
        books = cursor.fetchall()
        cursor.close()
        conn.close()

        book_panel = QWidget()
        layout = QVBoxLayout(book_panel)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QLabel("📚 Borrowed Books")
        header.setFont(QFont("Georgia", 22, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignLeft)
        layout.addWidget(header)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)


        # Book List
        if books:
            for title, due_date in books:
                card = QWidget()
                card_layout = QHBoxLayout(card)
                card_layout.setContentsMargins(15, 10, 15, 10)
                card_layout.setSpacing(20)

                icon = QLabel("📖")
                icon.setFont(QFont("Arial", 20))
                icon.setFixedWidth(40)

                title_label = QLabel(title)
                title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))


                due_label = QLabel(f"Due: {due_date}")
                due_label.setFont(QFont("Segoe UI", 10))
                due_label.setStyleSheet("color: #e67e22;")

                card_layout.addWidget(icon)
                card_layout.addWidget(title_label)
                card_layout.addStretch()
                card_layout.addWidget(due_label)

                card.setStyleSheet("""
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #dcdcdc;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
            """)

                scroll_layout.addWidget(card)




        else:
            empty_msg = QLabel("You haven’t borrowed any books yet.\nExplore the catalog and start reading!")
            empty_msg.setFont(QFont("Segoe UI", 12))
            empty_msg.setAlignment(Qt.AlignCenter)
            empty_msg.setStyleSheet("color: #7f8c8d; padding: 40px;")
            scroll_layout.addWidget(empty_msg)

        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        if self.main_panel_layout is not None:
            for i in reversed(range(self.main_panel_layout.count())):
                widget = self.main_panel_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)

        self.main_panel_layout.addWidget(book_panel)
     except Exception as e:
         print(f"[error] failed to show books : {e}")

    def get_borrowed_books(self, username):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
          SELECT book_title, due_date 
          FROM borrowed_books 
          WHERE username = %s
        """, (username,))
        books = cursor.fetchall()
        cursor.close()
        conn.close()
        return books

    def Main_screen(self):
        # Top navigation bar
        top_panel = QWidget()
        top_panel.setFixedHeight(70)
        top_panel.setStyleSheet("""
            background-color: #A1C6EA;
            border-bottom: 2px solid #7FB3D5;
        """)

        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(20, 10, 20, 10)
        top_layout.setSpacing(15)

        button_style = """
            QPushButton {
                background-color: #ffffff;
                color: #34495e;
                border: none;
                padding: 10px 18px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d6eaf8;
            }
        """

        home_btn = QPushButton("🏠 Home")
        home_btn.setStyleSheet(button_style)
        home_btn.clicked.connect(self.show_home)

        books_btn = QPushButton("📚 My Books")
        books_btn.setStyleSheet(button_style)
        books_btn.clicked.connect(self.show_borrowed_books)

        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setStyleSheet(button_style)
        # settings_btn.clicked.connect(...)  # Optional

        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setStyleSheet(button_style)
        logout_btn.clicked.connect(self.logout_clicked)

        # Add buttons
        for btn in [home_btn, books_btn, settings_btn, logout_btn]:
            top_layout.addWidget(btn)

        top_layout.addStretch()

        # Main content area
        self.main_panel = QWidget()
        self.main_panel.setStyleSheet("background-color: #fdfdfd; border-top: 1px solid #ddd;")
        self.main_panel_layout = QVBoxLayout(self.main_panel)
        self.main_panel_layout.setContentsMargins(20, 20, 20, 20)

        # Container
        container = QWidget()
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(top_panel)
        self.main_layout.addWidget(self.main_panel)

        self.stack.addWidget(container)
        self.stack.setCurrentWidget(container)
        self.showMaximized()

        self.show_home()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())