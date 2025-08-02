import pytest
from app import app
import database # Import the database module itself
from database import get_db, init_db # Import these explicitly for direct use
import os
import sqlite3
import time # Import time for delays

# Change the scope of the fixture to 'session'
# This means the fixture's setup and teardown will run once per test session.
@pytest.fixture(scope='session')
def client():
    # Use a separate test database
    app.config['TESTING'] = True
    test_db_path = 'test_users.db'

    # Store original DATABASE path and set to test path for the duration of the session
    original_db_path = database.DATABASE
    database.DATABASE = test_db_path

    # --- SETUP (runs once at the beginning of the test session) ---
    # Ensure any residual test_users.db from a previous interrupted run is removed
    if os.path.exists(test_db_path):
        try:
            conn_check = sqlite3.connect(test_db_path)
            conn_check.close()
            time.sleep(0.1) # Give OS a moment to release
        except sqlite3.Error:
            pass # Connection might already be closed

        for i in range(5):
            try:
                os.remove(test_db_path)
                break
            except PermissionError:
                time.sleep(0.1)
        else:
            raise PermissionError(f"Could not remove {test_db_path} during initial setup. It's likely still in use from a prior run. Please close any programs accessing it and delete it manually if necessary.")

    # Initialize a clean test database within the app context for the session
    with app.app_context():
        init_db()

    # Create the test client for the session
    test_client = app.test_client()

    # Yield the client to all tests in the session
    yield test_client

    # --- TEARDOWN (runs once at the end of the test session) ---
    # Ensure all connections to the test database are closed
    try:
        conn = sqlite3.connect(test_db_path)
        conn.close()
        time.sleep(0.1) # Give OS a moment to release
    except sqlite3.Error:
        pass # Connection might already be closed or not exist

    # Attempt to remove the test database file
    if os.path.exists(test_db_path):
        for i in range(5):
            try:
                os.remove(test_db_path)
                print(f"\n[INFO] Successfully cleaned up {test_db_path} during teardown.")
                break
            except PermissionError:
                time.sleep(0.5) # Longer sleep for final cleanup
        else:
            print(f"\n[ERROR] Failed to remove {test_db_path} during final teardown after multiple retries. You may need to delete it manually.")

    # Revert DATABASE constant in database.py to its original value
    database.DATABASE = original_db_path


# --- Test Functions (No changes needed here) ---
def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"message": "User Management System API is running"}

def test_create_user(client):
    response = client.post('/users', json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 201
    assert "User created successfully" in response.json['message']
    assert "user_id" in response.json

def test_create_user_missing_data(client):
    response = client.post('/users', json={
        "name": "Test User",
        "email": "test@example.com"
        # Missing password
    })
    assert response.status_code == 400
    assert "Missing name, email, or password" in response.json['error']

def test_create_user_duplicate_email(client):
    # Create first user
    client.post('/users', json={
        "name": "Duplicate User",
        "email": "duplicate@example.com",
        "password": "password"
    })
    # Try to create with same email
    response = client.post('/users', json={
        "name": "Another User",
        "email": "duplicate@example.com",
        "password": "another_password"
    })
    assert response.status_code == 409
    assert "User with this email already exists" in response.json['error']

def test_get_all_users(client):
    response = client.get('/users')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) >= 3

def test_get_specific_user(client):
    # First, create a user to ensure we have one
    create_response = client.post('/users', json={
        "name": "Specific User",
        "email": "specific@example.com",
        "password": "password"
    })
    user_id = create_response.json['user_id']

    response = client.get(f'/user/{user_id}')
    assert response.status_code == 200
    assert response.json['name'] == "Specific User"
    assert response.json['email'] == "specific@example.com"

def test_get_nonexistent_user(client):
    response = client.get('/user/99999')
    assert response.status_code == 404
    assert "User not found" in response.json['message']

def test_update_user(client):
    # Create a user to update
    create_response = client.post('/users', json={
        "name": "User To Update",
        "email": "update@example.com",
        "password": "password"
    })
    user_id = create_response.json['user_id']

    update_response = client.put(f'/user/{user_id}', json={
        "name": "Updated User Name",
        "email": "updated@example.com"
    })
    assert update_response.status_code == 200
    assert "User updated successfully" in update_response.json['message']

    # Verify update
    get_response = client.get(f'/user/{user_id}')
    assert get_response.json['name'] == "Updated User Name"
    assert get_response.json['email'] == "updated@example.com"

def test_delete_user(client):
    # Create a user to delete
    create_response = client.post('/users', json={
        "name": "User To Delete",
        "email": "delete@example.com",
        "password": "password"
    })
    user_id = create_response.json['user_id']

    delete_response = client.delete(f'/user/{user_id}')
    assert delete_response.status_code == 200
    assert "User deleted successfully" in delete_response.json['message']

    # Verify deletion
    get_response = client.get(f'/user/{user_id}')
    assert get_response.status_code == 404

def test_search_users(client):
    # Ensure some users exist for search
    client.post('/users', json={"name": "Alice", "email": "alice@example.com", "password": "pass"})
    client.post('/users', json={"name": "Bob", "email": "bob_search@example.com", "password": "pass"})
    client.post('/users', json={"name": "Charlie", "email": "charlie@example.com", "password": "pass"})

    response = client.get('/search?name=ali')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) >= 1
    assert any(user['name'] == 'Alice' for user in response.json)

def test_search_users_no_name(client):
    response = client.get('/search')
    assert response.status_code == 400
    assert "Please provide a name to search" in response.json['error']

def test_login_success(client):
    response = client.post('/login', json={
        "email": "john@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json['status'] == "success"
    assert "user_id" in response.json

def test_login_failure_wrong_password(client):
    response = client.post('/login', json={
        "email": "john@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json['status'] == "failed"
    assert "Invalid email or password" in response.json['message']

def test_login_failure_nonexistent_email(client):
    response = client.post('/login', json={
        "email": "nonexistent@example.com",
        "password": "anypassword"
    })
    assert response.status_code == 401
    assert response.json['status'] == "failed"
    assert "Invalid email or password" in response.json['message']