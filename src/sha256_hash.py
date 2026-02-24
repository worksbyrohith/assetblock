"""
sha256_hash.py — SHA-256 hashing utility for AssetBlock.
Generates a unique fingerprint for every uploaded file.
"""

import hashlib


def generate_hash(file_bytes: bytes) -> str:
    """Generate SHA-256 hash from file bytes."""
    sha256 = hashlib.sha256()
    sha256.update(file_bytes)
    return sha256.hexdigest()


def hash_string(text: str) -> str:
    """Generate SHA-256 hash from a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
