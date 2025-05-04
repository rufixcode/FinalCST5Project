import mysql.connector
import bcrypt

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="librarydb"
    )

def insert_admin(username, plain_password):
    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt())

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert the admin user into the admins table
    cursor.execute("INSERT INTO admins (username, password) VALUES (%s, %s)", (username, hashed_password))

    # Commit the transaction and close the connection
    conn.commit()
    cursor.close()
    conn.close()

    print(f"Admin {username} inserted successfully.")

# Example usage: Insert an admin with the username 'admin' and password 'admin_password'
insert_admin('admin', '123456')
