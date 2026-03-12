"""
License Manager for ID Card Printer
Tracks upgrade/license status so users are not repeatedly prompted
to pay for an upgrade they already own.
"""

import json
import os
import hashlib

LICENSE_FILE = 'license.json'


def load_license():
    """Load license data from license.json. Returns empty dict if not found."""
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_license(data):
    """Save license data to license.json."""
    with open(LICENSE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def _compute_key_hash(license_key):
    """Return a simple hash of the license key for storage."""
    return hashlib.sha256(license_key.strip().upper().encode()).hexdigest()


def activate_license(license_key):
    """
    Activate the application with the provided license key.
    Persists the activation so the user is never prompted again.

    The key must be non-empty and at least 8 characters long.

    Returns (success: bool, message: str)
    """
    if not license_key or not license_key.strip():
        return False, "License key cannot be empty."

    if len(license_key.strip()) < 8:
        return False, "Invalid license key format. Please check your key and try again."

    data = load_license()
    data['activated'] = True
    data['key_hash'] = _compute_key_hash(license_key)
    save_license(data)
    return True, "License activated successfully. Thank you!"


def is_activated():
    """Return True if this installation already has an active license."""
    data = load_license()
    return bool(data.get('activated', False))


def deactivate_license():
    """Remove the stored license (for testing/support purposes)."""
    data = load_license()
    data['activated'] = False
    data.pop('key_hash', None)
    save_license(data)
