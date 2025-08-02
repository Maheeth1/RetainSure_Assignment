import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'users.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,                            -- Added age column, nullable
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        # Insert sample data if empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (name, age, email, password) VALUES (?, ?, ?, ?)",
                ('John Doe', 30, 'john@example.com', generate_password_hash('password123')))
            cursor.execute("INSERT INTO users (name, age, email, password) VALUES (?, ?, ?, ?)",
                ('Jane Smith', 28, 'jane@example.com', generate_password_hash('secret456')))
            cursor.execute("INSERT INTO users (name, age, email, password) VALUES (?, ?, ?, ?)",
                ('Bob Johnson', 40, 'bob@example.com', generate_password_hash('qwerty789')))
        conn.commit()

def get_user_by_id(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, age, email FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()

def get_user_by_email(email):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, age, email, password FROM users WHERE email = ?", (email,))
        return cursor.fetchone()

def get_all_users_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, age, email FROM users")
        return cursor.fetchall()

def create_user_db(name, email, password_hash, age=None):
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, age, email, password) VALUES (?, ?, ?, ?)",
                (name, age, email, password_hash)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

def update_user_db(user_id, name=None, email=None, password=None, age=None):
    with get_db() as conn:
        cursor = conn.cursor()

        # Build dynamic query depending on which fields are passed
        fields = []
        params = []
        if name is not None:
            fields.append('name = ?')
            params.append(name)
        if email is not None:
            fields.append('email = ?')
            params.append(email)
        if password is not None:
            fields.append('password = ?')
            params.append(password)
        if age is not None:
            fields.append('age = ?')
            params.append(age)

        if not fields:
            return False  # Nothing to update

        params.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, params)
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
        cursor.execute("SELECT id, name, age, email FROM users WHERE name LIKE ?", (f'%{name}%',))
        return cursor.fetchall()
