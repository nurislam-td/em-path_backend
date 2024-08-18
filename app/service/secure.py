import random
import string

import bcrypt

NUM = string.digits


def get_password_hash(password: str) -> bytes:
    salt = bcrypt.gensalt()
    password_b: bytes = password.encode()
    return bcrypt.hashpw(password_b, salt)


def verify_password(password: str, hash_password: bytes) -> bool:
    return bcrypt.checkpw(password=password.encode(), hashed_password=hash_password)


def generate_random_num(length: int = 6) -> str:
    return "".join(random.choices(NUM, k=length))
