"""
Hash Checker module.

Computes MD5 / SHA1 / SHA256 digests for a file, and provides a comparison
helper for verifying file integrity against a known-good hash.
"""

import hashlib


def _hash_file(path, algo, chunk_size=65536):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_md5(path):
    return _hash_file(path, "md5")


def compute_sha1(path):
    return _hash_file(path, "sha1")


def compute_sha256(path):
    return _hash_file(path, "sha256")


def compute_all(path):
    return {
        "md5": compute_md5(path),
        "sha1": compute_sha1(path),
        "sha256": compute_sha256(path),
    }


def compare_hashes(hash_a, hash_b):
    return hash_a.strip().lower() == hash_b.strip().lower()
