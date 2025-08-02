import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
import database
import sqlite3
import time

@pytest.fixture(scope='session')
def client():
    # Use a separate test database for isolation
    app.config['TESTING'] = True
    test_db_path = 'test_users.db'

    # Backup original DATABASE path and switch to test DB
    original_db_path = database.DATABASE
    database.DATABASE = test_db_path

    # Clean up leftover test DB file if exists,
    # with retries in case of file locks on Windows
    if os.path.exists(test_db_path):
        for i in range(5):
            try:
                os.remove(test_db_path)
                break
            except PermissionError:
                time.sleep(0.1)
        else:
            raise PermissionError(f"Unable to remove {test_db_path}. Close programs and delete manually.")

    with app.app_context():
        database.init_db()

    test_client = app.test_client()

    yield test_client

    # Tear down: close connections and remove test DB
    try:
        conn = sqlite3.connect(test_db_path)
        conn.close()
        time.sleep(0.1)
    except sqlite3.Error:
        pass

    if os.path.exists(test_db_path):
        for i in range(5):
            try:
                os.remove(test_db_path)
                break
            except PermissionError:
                time.sleep(0.5)

    # Restore original DB path
    database.DATABASE = original_db_path


# Fixture to create a known user for login tests
@pytest.fixture(scope='session', autouse=True)
def setup_test_users(client):
    # Create 'john@example.com' for login tests
    response = client.post('/users', json={
        "name": "John",
        "email": "john@example.com",
        "password": "password123",
        "age": 35
    })
    # Ignore if user already exists or created
    yield


# --- Test Functions ---

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {"message": "User Management System API is running"}


def test_create_user(client):
    response = client.post('/users', json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword",
        "age": 30
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
    # Marshmallow returns a dict keyed by field name
    assert "password" in response.json
    assert "Missing data for required field" in response.json["password"][0]


def test_create_user_duplicate_email(client):
    # Create user for duplication test
    client.post('/users', json={
        "name": "Duplicate User",
        "email": "duplicate@example.com",
        "password": "password123",
        "age": 25
    })
    # Attempt duplicate create
    response = client.post('/users', json={
        "name": "Another User",
        "email": "duplicate@example.com",
        "password": "anotherpassword",
        "age": 26
    })
    assert response.status_code == 409
    assert "User with this email already exists" in response.json['error']


def test_get_all_users(client):
    response = client.get('/users')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) >= 3  # Should have initial sample + test created users


def test_get_specific_user(client):
    # Create user first
    create_response = client.post('/users', json={
        "name": "Specific User",
        "email": "specific@example.com",
        "password": "password123",
        "age": 40
    })
    user_id = create_response.json['user_id']

    response = client.get(f'/user/{user_id}')
    assert response.status_code == 200
    assert response.json['name'] == "Specific User"
    assert response.json['email'] == "specific@example.com"


def test_get_nonexistent_user(client):
    response = client.get('/user/999999')
    assert response.status_code == 404
    assert "User not found" in response.json['message']


def test_update_user(client):
    # Create user for update
    create_response = client.post('/users', json={
        "name": "User To Update",
        "email": "update@example.com",
        "password": "password123",
        "age": 30
    })
    user_id = create_response.json['user_id']

    update_response = client.put(f'/user/{user_id}', json={
        "name": "Updated User Name",
        "email": "updated@example.com",
        "age": 31
    })
    assert update_response.status_code == 200
    # Since response returns updated user JSON, check fields
    assert update_response.json['name'] == "Updated User Name"
    assert update_response.json['email'] == "updated@example.com"
    assert update_response.json['age'] == 31


def test_delete_user(client):
    # Create user for deletion
    create_response = client.post('/users', json={
        "name": "User To Delete",
        "email": "delete@example.com",
        "password": "password123",
        "age": 33
    })
    user_id = create_response.json['user_id']

    delete_response = client.delete(f'/user/{user_id}')
    assert delete_response.status_code == 200
    assert "User deleted successfully" in delete_response.json['message']

    # Verify deleted
    get_response = client.get(f'/user/{user_id}')
    assert get_response.status_code == 404


def test_search_users(client):
    # Create users to search
    client.post('/users', json={"name": "Alice", "email": "alice@example.com", "password": "pass1234", "age": 27})
    client.post('/users', json={"name": "Bob", "email": "bob_search@example.com", "password": "pass1234", "age": 28})
    client.post('/users', json={"name": "Charlie", "email": "charlie@example.com", "password": "pass1234", "age": 29})

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
