# TODO: Implement your data models here
# Consider what data structures you'll need for:
# - Storing URL mappings
# - Tracking click counts
# - Managing URL metadata

# models.py
import threading
import time

class URLStore:
    def __init__(self):
        # Using a dictionary to store URL mappings
        # Key: short_code, Value: { "original_url": str, "clicks": int, "created_at": float }
        self.urls = {}
        # Using a lock to handle concurrent access to the urls dictionary
        self.lock = threading.Lock()

    def add_url(self, short_code: str, original_url: str):
        with self.lock:
            # Store original URL, initialize clicks to 0, and record creation timestamp
            self.urls[short_code] = {
                "original_url": original_url,
                "clicks": 0,
                "created_at": time.time()  # Unix timestamp for creation
            }

    def get_url_info(self, short_code: str):
        with self.lock:
            return self.urls.get(short_code)

    def increment_clicks(self, short_code: str):
        with self.lock:
            if short_code in self.urls:
                self.urls[short_code]["clicks"] += 1
                return True
            return False

    def is_short_code_taken(self, short_code: str) -> bool:
        with self.lock:
            return short_code in self.urls

# Initialize a global URL store instance
url_store = URLStore()