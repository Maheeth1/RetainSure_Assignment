# TODO: Implement utility functions here
# Consider functions for:
# - Generating short codes
# - Validating URLs
# - Any other helper functions you need

# utils.py
import random
import string
from urllib.parse import urlparse

# Characters allowed in short codes (alphanumeric)
ALPHANUMERIC_CHARS = string.ascii_letters + string.digits
SHORT_CODE_LENGTH = 6 # As per requirements

def generate_short_code(existing_codes: set) -> str:
    """
    Generates a unique 6-character alphanumeric short code.
    'existing_codes' is a set of already used short codes to ensure uniqueness.
    """
    while True:
        # Generate a random 6-character string from alphanumeric characters
        short_code = ''.join(random.choices(ALPHANUMERIC_CHARS, k=SHORT_CODE_LENGTH))
        # Ensure the generated short code is unique
        if short_code not in existing_codes:
            return short_code

def is_valid_url(url: str) -> bool:
    """
    Validates if a given string is a well-formed URL.
    Checks for scheme (http/https) and network location.
    """
    try:
        result = urlparse(url)
        # A URL is considered valid if it has a scheme (e.g., http, https)
        # and a network location (e.g., example.com)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except ValueError:
        return False