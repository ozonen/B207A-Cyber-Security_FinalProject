from backend import crypto_utils
from backend.db import get_cursor


def add_entry(
    user_id: int,
    site_name: str,
    site_username: str,
    site_password: str,
    vault_key: bytes,
) -> int:
    encrypted_password = crypto_utils.encrypt_secret(site_password, vault_key)
    with get_cursor() as cursor:
        cursor.execute(
            "INSERT INTO vault_entries (user_id, site_name, site_username, encrypted_password) "
            "VALUES (%s, %s, %s, %s)",
            (user_id, site_name, site_username, encrypted_password),
        )
        return cursor.lastrowid


def list_entries(user_id: int, vault_key: bytes) -> list[dict]:
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT id, site_name, site_username, encrypted_password "
            "FROM vault_entries WHERE user_id = %s ORDER BY site_name",
            (user_id,),
        )
        rows = cursor.fetchall()

    for row in rows:
        row["password"] = crypto_utils.decrypt_secret(row.pop("encrypted_password"), vault_key)
    return rows


def delete_entry(entry_id: int, user_id: int) -> None:
    with get_cursor() as cursor:
        cursor.execute(
            "DELETE FROM vault_entries WHERE id = %s AND user_id = %s",
            (entry_id, user_id),
        )
