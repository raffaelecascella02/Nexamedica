import bcrypt

def get_password_hash(password: str):
    encoded_password = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(encoded_password, salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )