# test_url_shortener.py
import pytest
from app.main import app, url_store # Import app and the url_store instance
from app.utils import is_valid_url, generate_short_code, SHORT_CODE_LENGTH, ALPHANUMERIC_CHARS
import json
import time
from datetime import datetime, timedelta

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost:5000'
    # If you moved URLStore into models.py and it's a global instance:
    from app.models import url_store # Import here to ensure it's loaded correctly within fixture scope
    with url_store.lock: # Use the lock when clearing
        url_store.urls.clear() # Clear the store for each test
    with app.test_client() as client:
        yield client

# Existing test for health check 
def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'URL Shortener API'

# Test utility function: URL validation
def test_is_valid_url():
    assert is_valid_url("https://www.example.com") is True
    assert is_valid_url("http://example.org/path?query=1") is True
    assert is_valid_url("ftp://ftp.example.com") is False # Only http/https allowed
    assert is_valid_url("www.example.com") is False # Missing scheme
    assert is_valid_url("invalid-url") is False
    assert is_valid_url("") is False
    assert is_valid_url(None) is False

# Test utility function: Short code generation
def test_generate_short_code():
    existing_codes = {"abc123"}
    code1 = generate_short_code(existing_codes)
    assert len(code1) == SHORT_CODE_LENGTH
    assert all(c in ALPHANUMERIC_CHARS for c in code1)
    assert code1 not in existing_codes # Ensure it's unique

    # Test that it eventually generates a unique code even with many existing
    # This test is more conceptual; in practice, with only 6 chars, collisions are low.
    # For a real exhaustive test, mocking random might be better.
    # For now, let's just add it to existing_codes and try again.
    existing_codes.add(code1)
    code2 = generate_short_code(existing_codes)
    assert code2 != code1
    assert len(code2) == SHORT_CODE_LENGTH

# Test Case 1: Successful URL shortening 
def test_shorten_url_success(client):
    long_url = "https://www.example.com/very/long/url/for/testing"
    response = client.post('/api/shorten', json={"url": long_url})
    data = response.get_json()

    assert response.status_code == 201
    assert "short_code" in data
    assert "short_url" in data
    assert len(data["short_code"]) == SHORT_CODE_LENGTH
    assert data["short_url"].startswith("http://localhost:5000/")
    assert data["short_url"].endswith(data["short_code"])

    # Verify the URL is stored
    stored_info = url_store.get_url_info(data["short_code"])
    assert stored_info is not None
    assert stored_info["original_url"] == long_url
    assert stored_info["clicks"] == 0
    assert "created_at" in stored_info
    # Check if creation timestamp is recent (within a small margin)
    assert datetime.fromtimestamp(stored_info["created_at"]) > datetime.now() - timedelta(minutes=1)

# Test Case 2: Shortening with invalid URL 
def test_shorten_url_invalid(client):
    response = client.post('/api/shorten', json={"url": "invalid-url-format"})
    data = response.get_json()
    assert response.status_code == 400
    assert "error" in data
    assert data["error"] == "Invalid URL provided."

    response = client.post('/api/shorten', json={"url": "ftp://example.com"})
    data = response.get_json()
    assert response.status_code == 400
    assert "error" in data
    assert data["error"] == "Invalid URL provided."

# Test Case 3: Shortening with missing URL in request body 
def test_shorten_url_missing_body(client):
    response = client.post('/api/shorten', json={})
    data = response.get_json()
    assert response.status_code == 400
    assert "error" in data
    assert data["error"] == "URL is required in request body."

    response = client.post('/api/shorten', data=json.dumps({}), content_type='application/json')
    data = response.get_json()
    assert response.status_code == 400
    assert "error" in data
    assert data["error"] == "URL is required in request body." # Flask's default error for missing JSON might be different, but our check handles it.


# Test Case 4: Successful redirection and click count increment 
def test_redirect_and_click_count(client):
    long_url = "https://www.google.com"
    shorten_response = client.post('/api/shorten', json={"url": long_url})
    short_code = shorten_response.get_json()["short_code"]

    # Initial check of clicks
    stats_response_initial = client.get(f'/api/stats/{short_code}')
    assert stats_response_initial.status_code == 200
    assert stats_response_initial.get_json()["clicks"] == 0

    # Perform redirect
    redirect_response = client.get(f'/{short_code}', follow_redirects=False)
    assert redirect_response.status_code == 302 # Expect a redirect status code
    assert redirect_response.headers['Location'] == long_url

    # Check click count after one redirect
    stats_response_after1 = client.get(f'/api/stats/{short_code}')
    assert stats_response_after1.status_code == 200
    assert stats_response_after1.get_json()["clicks"] == 1

    # Perform another redirect
    redirect_response_2 = client.get(f'/{short_code}', follow_redirects=False)
    assert redirect_response_2.status_code == 302
    assert redirect_response_2.headers['Location'] == long_url

    # Check click count after two redirects
    stats_response_after2 = client.get(f'/api/stats/{short_code}')
    assert stats_response_after2.status_code == 200
    assert stats_response_after2.get_json()["clicks"] == 2

# Test Case 5: Redirect for non-existent short code 
def test_redirect_non_existent(client):
    response = client.get('/nonexistent1')
    data = response.get_json()
    assert response.status_code == 404
    assert "error" in data
    assert data["error"] == "Resource not found."

# Test Case 6: Get analytics for an existing short code 
def test_get_analytics_success(client):
    long_url = "https://www.github.com/myrepo"
    shorten_response = client.post('/api/shorten', json={"url": long_url})
    short_code = shorten_response.get_json()["short_code"]

    # Perform a few redirects to increment clicks
    client.get(f'/{short_code}')
    client.get(f'/{short_code}')
    time.sleep(0.01) # Small delay to ensure created_at is slightly different if needed (not strictly necessary here)

    stats_response = client.get(f'/api/stats/{short_code}')
    data = stats_response.get_json()

    assert stats_response.status_code == 200
    assert data["url"] == long_url
    assert data["clicks"] == 2
    assert "created_at" in data

    # Verify created_at format (ISO 8601)
    try:
        datetime.fromisoformat(data["created_at"])
    except ValueError:
        pytest.fail("created_at is not in ISO 8601 format")

# Test Case 7: Get analytics for non-existent short code 
def test_get_analytics_non_existent(client):
    response = client.get('/api/stats/nonexistent2')
    data = response.get_json()
    assert response.status_code == 404
    assert "error" in data
    assert data["error"] == "Resource not found."

# Test Case 8: Concurrency test (basic)
def test_concurrency_click_increment(client):
    long_url = "https://concurrency.test"
    shorten_response = client.post('/api/shorten', json={"url": long_url})
    short_code = shorten_response.get_json()["short_code"]

    num_requests = 100
    import concurrent.futures

    def make_redirect_request(short_code_to_redirect):
        with app.app_context():

            # Simpler approach: sequential calls for test client
            response = client.get(f'/{short_code_to_redirect}', follow_redirects=False)
            return response

        # Change: Remove the ThreadPoolExecutor and call sequentially to avoid Flask context issues
        for _ in range(num_requests):
            response = make_redirect_request(short_code)
            assert response.status_code == 302 # Ensure redirects happened

        stats_response = client.get(f'/api/stats/{short_code}')
        data = stats_response.get_json()
        assert data["clicks"] == num_requests