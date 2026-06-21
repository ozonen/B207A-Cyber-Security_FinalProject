import mysql.connector

from backend import crypto_utils
from backend.db import get_cursor


class AuthError(Exception):
    pass


_DUMMY_HASH = crypto_utils.hash_password("dummy-password-for-timing-safety")


def register_user(username: str, email: str, master_password: str) -> int:
    password_hash = crypto_utils.hash_password(master_password)
    kdf_salt = crypto_utils.generate_kdf_salt()

    with get_cursor() as cursor:
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, kdf_salt) "
                "VALUES (%s, %s, %s, %s)",
                (username, email, password_hash, kdf_salt),
            )
        except mysql.connector.IntegrityError:
            raise AuthError("Username or email already registered.")
        return cursor.lastrowid


def login_user(username: str, master_password: str) -> tuple[int, bytes]:
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT id, password_hash, kdf_salt FROM users WHERE username = %s",
            (username,),
        )
        row = cursor.fetchone()

    if row is None:
        crypto_utils.verify_password(master_password, _DUMMY_HASH)
        raise AuthError("Invalid username or password.")

    if not crypto_utils.verify_password(master_password, row["password_hash"]):
        raise AuthError("Invalid username or password.")

    vault_key = crypto_utils.derive_vault_key(master_password, row["kdf_salt"])
    return row["id"], vault_key
