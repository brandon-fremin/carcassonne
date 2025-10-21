import hashlib

def sha256(data) -> str:
    m = hashlib.sha256()
    m.update(str(data).encode())
    return m.hexdigest()