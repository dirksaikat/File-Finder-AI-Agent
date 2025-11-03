# utils/verify_code.py (new helper)
import hashlib, os, random
from datetime import datetime, timedelta

def make_code_and_hash(ttl_minutes=10):
    code = f"{random.randint(100000, 999999)}"
    salt = os.urandom(16).hex()
    digest = hashlib.sha256((salt + code).encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)
    return code, salt, digest, expires_at

def verify_code_matches(input_code, salt, stored_digest):
    return hashlib.sha256((salt + input_code).encode()).hexdigest() == stored_digest
