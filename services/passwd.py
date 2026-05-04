import bcrypt

def hashed_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf8"), salt).decode("ascii")

def check_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf8"), password_hash.encode("utf8"))
