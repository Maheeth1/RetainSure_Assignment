from flask import Flask, jsonify, request, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import Schema, fields, validate, ValidationError
from database import (
    get_user_by_id,
    get_all_users_db,
    create_user_db,
    update_user_db,
    delete_user_db,
    search_users_db,
    get_user_by_email,
)
import logging
import os

app = Flask(__name__, static_folder='frontend/build/static', template_folder='frontend/build')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Marshmallow Schema
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    age = fields.Int(required=False, validate=validate.Range(min=1))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))

user_schema = UserSchema()
user_update_schema = UserSchema(partial=True)
users_schema = UserSchema(many=True)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.template_folder, path)):
        return send_from_directory(app.template_folder, path)
    else:
        return send_from_directory(app.template_folder, 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"message": "User Management System API is running"}), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        users = get_all_users_db()
        return jsonify(users_schema.dump(users)), 200
    except Exception as e:
        logging.error(f"Error fetching all users: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = get_user_by_id(user_id)
        if user:
            return user_schema.dump(user), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        logging.error(f"Error fetching user {user_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/users', methods=['POST'])
def create_user():
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "Invalid JSON data"}), 400
        data = user_schema.load(json_data)
        hashed_password = generate_password_hash(data['password'], method='sha256')
        age = data.get('age', None)
        user_id = create_user_db(data['name'], data['email'], hashed_password, age)
        if user_id:
            logging.info(f"User created successfully with ID: {user_id}")
            return jsonify({"message": "User created successfully", "user_id": user_id}), 201
        else:
            logging.warning(f"Email already exists: {data['email']}")
            return jsonify({"error": "User with this email already exists"}), 409
    except ValidationError as err:
        logging.warning(f"Validation error during user creation: {err.messages}")
        return jsonify(err.messages), 400
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "Invalid JSON data"}), 400
        data = user_update_schema.load(json_data, partial=True)
        if not data:
            return jsonify({"error": "No valid fields provided for update"}), 400
        if 'password' in data:
            data['password'] = generate_password_hash(data['password'], method='sha256')
        updated = update_user_db(
            user_id,
            name=data.get('name'),
            email=data.get('email'),
            password=data.get('password'),
            age=data.get('age')
        )
        if updated:
            logging.info(f"User {user_id} updated.")
            updated_user = get_user_by_id(user_id)
            return user_schema.dump(updated_user), 200
        else:
            logging.warning(f"User {user_id} not found or no changes.")
            return jsonify({"message": "User not found or no changes made"}), 404
    except ValidationError as err:
        logging.warning(f"Validation error during user update: {err.messages}")
        return jsonify(err.messages), 400
    except Exception as e:
        logging.error(f"Error updating user {user_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        deleted = delete_user_db(user_id)
        if deleted:
            logging.info(f"User {user_id} deleted.")
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
        return jsonify(users_schema.dump(users)), 200
    except Exception as e:
        logging.error(f"Error searching users: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "Invalid JSON data"}), 400

        email = json_data.get('email')
        password = json_data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = get_user_by_email(email)
        if user and check_password_hash(user['password'], password):
            logging.info(f"User {user['id']} logged in successfully.")
            return jsonify({"status": "success", "user_id": user['id'], "message": "Login successful"}), 200
        else:
            logging.warning(f"Login failed for email: {email}")
            return jsonify({"status": "failed", "message": "Invalid email or password"}), 401

    except Exception as e:
        logging.error(f"Error during login: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
