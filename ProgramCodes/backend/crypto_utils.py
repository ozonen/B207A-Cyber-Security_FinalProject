import base64
import os

import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

PBKDF2_ITERATIONS = 600_000
KDF_SALT_BYTES = 16


def generate_kdf_salt() -> bytes:
    return os.urandom(KDF_SALT_BYTES)


def hash_password(master_password: str) -> str:
    hashed = bcrypt.hashpw(master_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(master_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(master_password.encode("utf-8"), password_hash.encode("utf-8"))


def derive_vault_key(master_password: str, kdf_salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=kdf_salt,
        iterations=PBKDF2_ITERATIONS,
    )
    raw_key = kdf.derive(master_password.encode("utf-8"))
    return base64.urlsafe_b64encode(raw_key)


def encrypt_secret(plaintext: str, vault_key: bytes) -> str:
    fernet = Fernet(vault_key)
    token = fernet.encrypt(plaintext.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_secret(token: str, vault_key: bytes) -> str:
    fernet = Fernet(vault_key)
    plaintext = fernet.decrypt(token.encode("utf-8"))
    return plaintext.decode("utf-8")
