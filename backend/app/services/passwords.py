from __future__ import annotations

import bcrypt


def hash_password(plain: str) -> str:
    data = plain.encode("utf-8")
    if len(data) > 72:
        data = data[:72]
    hashed = bcrypt.hashpw(data, bcrypt.gensalt())
    return hashed.decode("ascii")


def verify_password(plain: str, password_hash: str) -> bool:
    data = plain.encode("utf-8")
    if len(data) > 72:
        data = data[:72]
    try:
        return bcrypt.checkpw(data, password_hash.encode("ascii"))
    except ValueError:
        return False
