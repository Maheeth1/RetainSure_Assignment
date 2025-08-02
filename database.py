import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash # For password hashing

DATABASE = 'users.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Allows access to columns by name
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        # Insert sample data with hashed passwords if table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                           ('John Doe', 'john@example.com', generate_password_hash('password123')))
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                           ('Jane Smith', 'jane@example.com', generate_password_hash('secret456')))
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                           ('Bob Johnson', 'bob@example.com', generate_password_hash('qwerty789')))
        conn.commit()

def get_user_by_id(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()

def get_user_by_email(email):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, password FROM users WHERE email = ?", (email,))
        return cursor.fetchone()

def get_all_users_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users")
        return cursor.fetchall()

def create_user_db(name, email, password_hash):
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                           (name, email, password_hash))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

def update_user_db(user_id, name=None, email=None):
    with get_db() as conn:
        cursor = conn.cursor()
        if name and email:
            cursor.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (name, email, user_id))
        elif name:
            cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
        elif email:
            cursor.execute("UPDATE users SET email = ? WHERE id = ?", (email, user_id)) # Corrected line
        else:
            return False
        conn.commit()
        return cursor.rowcount > 0

def delete_user_db(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0

def search_users_db(name):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE name LIKE ?", (f'%{name}%',))
        return cursor.fetchall()