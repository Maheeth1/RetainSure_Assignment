import sqlite3
from werkzeug.security import generate_password_hash # Import necessary for init_db
from database import init_db # Import the init_db function from database.py

if __name__ == '__main__':
    init_db()
    print("Database initialized with sample data")