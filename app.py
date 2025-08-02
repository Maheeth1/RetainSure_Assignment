from flask import Flask, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, init_db, get_user_by_id, get_all_users_db, create_user_db, update_user_db, delete_user_db, search_users_db, get_user_by_email
import json
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the database on app startup (or ensure it's initialized)
# with app.app_context():
#     init_db()

# NEW: Route to serve the main HTML page
@app.route('/') # Or just '/' if you want the UI as the main entry point
def serve_ui():
    return render_template('index.html')

# @app.route('/')
# def home():
#     return jsonify({"message": "User Management System API is running"}), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        users = get_all_users_db()
        # Convert Row objects to dictionaries for jsonify
        users_list = [dict(user) for user in users]
        return jsonify(users_list), 200
    except Exception as e:
        logging.error(f"Error fetching all users: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/user/<int:user_id>', methods=['GET']) # Changed to int converter
def get_user(user_id):
    try:
        user = get_user_by_id(user_id)
        if user:
            return jsonify(dict(user)), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        logging.error(f"Error fetching user {user_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json() # Use get_json() for JSON data
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not all([name, email, password]):
            return jsonify({"error": "Missing name, email, or password"}), 400

        # Basic email validation
        if "@" not in email or "." not in email:
            return jsonify({"error": "Invalid email format"}), 400

        hashed_password = generate_password_hash(password)
        user_id = create_user_db(name, email, hashed_password)

        if user_id:
            logging.info(f"User created successfully with ID: {user_id}")
            return jsonify({"message": "User created successfully", "user_id": user_id}), 201
        else:
            logging.warning(f"Failed to create user: Email '{email}' might already exist.")
            return jsonify({"error": "User with this email already exists"}), 409 # Conflict
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        name = data.get('name')
        email = data.get('email')

        if not (name or email):
            return jsonify({"error": "No data provided for update"}), 400

        if email and ("@" not in email or "." not in email):
            return jsonify({"error": "Invalid email format"}), 400

        if update_user_db(user_id, name, email):
            logging.info(f"User {user_id} updated successfully.")
            return jsonify({"message": "User updated successfully"}), 200
        else:
            logging.warning(f"User {user_id} not found for update or no changes made.")
            return jsonify({"message": "User not found or no changes made"}), 404
    except Exception as e:
        logging.error(f"Error updating user {user_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        if delete_user_db(user_id):
            logging.info(f"User {user_id} deleted successfully.")
            return jsonify({"message": "User deleted successfully"}), 200
        else:
            logging.warning(f"User {user_id} not found for deletion.")
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        logging.error(f"Error deleting user {user_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/search', methods=['GET'])
def search_users():
    try:
        name = request.args.get('name')

        if not name:
            return jsonify({"error": "Please provide a name to search"}), 400

        users = search_users_db(name)
        users_list = [dict(user) for user in users]
        return jsonify(users_list), 200
    except Exception as e:
        logging.error(f"Error searching users: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return jsonify({"error": "Missing email or password"}), 400

        user = get_user_by_email(email)

        if user and check_password_hash(user['password'], password):
            logging.info(f"User {user['id']} logged in successfully.")
            return jsonify({"status": "success", "user_id": user['id'], "message": "Login successful"}), 200
        else:
            logging.warning(f"Login failed for email: {email}")
            return jsonify({"status": "failed", "message": "Invalid email or password"}), 401 # Unauthorized
    except Exception as e:
        logging.error(f"Error during login: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)