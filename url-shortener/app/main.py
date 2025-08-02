# main.py
from flask import Flask, request, jsonify, redirect, url_for, abort
from datetime import datetime
from app.models import url_store # Import the global URL store
from app.utils import generate_short_code, is_valid_url, ALPHANUMERIC_CHARS, SHORT_CODE_LENGTH # Import utility functions

app = Flask(__name__)

app.config['SERVER_NAME'] = 'localhost:5000'

# Health check endpoints provided in the starter code 
@app.route('/')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "URL Shortener API"
    })

@app.route('/api/health')
def api_health():
    return jsonify({
        "status": "ok",
        "message": "URL Shortener API is running"
    })

# Core Requirement 1: Shorten URL Endpoint 
@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required in request body."}), 400

    original_url = data['url']

    # Validate URL 
    if not is_valid_url(original_url):
        return jsonify({"error": "Invalid URL provided."}), 400

    # Generate a unique short code 
    # We pass existing_codes from the url_store for uniqueness check.
    # Note: In a real-world scenario, you might have a more robust way to manage
    # short code generation and collisions, potentially involving retries or
    # pre-generating codes. For this in-memory solution, directly checking
    # against url_store is sufficient and thread-safe due to the lock in URLStore.
    existing_codes_set = set(url_store.urls.keys())
    short_code = generate_short_code(existing_codes_set)

    # Store the mapping 
    url_store.add_url(short_code, original_url)

    short_url = url_for('redirect_to_long_url', short_code=short_code, _external=True)

    return jsonify({
        "short_code": short_code,
        "short_url": short_url
    }), 201

# Core Requirement 2: Redirect Endpoint 
@app.route('/<short_code>')
def redirect_to_long_url(short_code):
    url_info = url_store.get_url_info(short_code)

    if not url_info:
        # Return 404 if short code doesn't exist 
        abort(404)

    # Track each redirect (increment click count) 
    url_store.increment_clicks(short_code)

    return redirect(url_info["original_url"])

# Core Requirement 3: Analytics Endpoint 
@app.route('/api/stats/<short_code>')
def get_url_stats(short_code):
    url_info = url_store.get_url_info(short_code)

    if not url_info:
        # Return 404 if short code doesn't exist 
        abort(404)

    # Return click count, creation timestamp, and original URL 
    created_at_dt = datetime.fromtimestamp(url_info["created_at"])
    # Format timestamp as ISO 8601 string
    created_at_iso = created_at_dt.isoformat()

    return jsonify({
        "url": url_info["original_url"],
        "clicks": url_info["clicks"],
        "created_at": created_at_iso
    }), 200

# Basic error handling for 404
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)