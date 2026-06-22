import getpass
import secrets
import string
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"
ENV_PATH = PROJECT_ROOT / ".env"

APP_DB_NAME = "password_manager"
APP_DB_USER = "pm_app"


def install_python_dependencies() -> None:
    print("Installing Python dependencies from requirements.txt ...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(PROJECT_ROOT / "requirements.txt")],
        check=True,
    )


def generate_app_password(length: int = 24) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def run_schema(admin_conn) -> None:
    print("Creating database and tables from database/schema.sql ...")
    statements = SCHEMA_PATH.read_text(encoding="utf-8")
    cursor = admin_conn.cursor()
    for statement in statements.split(";"):
        statement = statement.strip()
        if statement:
            cursor.execute(statement)
    admin_conn.commit()
    cursor.close()


def create_app_user(admin_conn, app_password: str) -> None:
    print(f"Creating MySQL user '{APP_DB_USER}' ...")
    cursor = admin_conn.cursor()
    cursor.execute(
        f"CREATE USER IF NOT EXISTS '{APP_DB_USER}'@'localhost' IDENTIFIED BY %s",
        (app_password,),
    )
    cursor.execute(
        f"ALTER USER '{APP_DB_USER}'@'localhost' IDENTIFIED BY %s", (app_password,)
    )
    cursor.execute(
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON {APP_DB_NAME}.* TO '{APP_DB_USER}'@'localhost'"
    )
    cursor.execute("FLUSH PRIVILEGES")
    admin_conn.commit()
    cursor.close()


def generate_flask_secret_key() -> str:
    return secrets.token_hex(32)


def write_env_file(app_password: str, db_host: str, db_port: str, flask_secret_key: str) -> None:
    print(f"Writing connection settings to {ENV_PATH} ...")
    ENV_PATH.write_text(
        "\n".join(
            [
                f"DB_HOST={db_host}",
                f"DB_PORT={db_port}",
                f"DB_NAME={APP_DB_NAME}",
                f"DB_USER={APP_DB_USER}",
                f"DB_PASSWORD={app_password}",
                f"FLASK_SECRET_KEY={flask_secret_key}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    install_python_dependencies()

    import mysql.connector

    print("\nThis step needs MySQL ADMIN credentials ONCE, to create the database")
    print("and a separate, restricted application user. These admin credentials")
    print("are used only while this script runs and are never saved anywhere.\n")
    db_host = input("MySQL host [localhost]: ").strip() or "localhost"
    db_port = input("MySQL port [3306]: ").strip() or "3306"
    admin_user = input("MySQL admin username [root]: ").strip() or "root"
    admin_password = getpass.getpass("MySQL admin password: ")

    admin_conn = mysql.connector.connect(
        host=db_host, port=int(db_port), user=admin_user, password=admin_password
    )
    try:
        run_schema(admin_conn)
        app_password = generate_app_password()
        create_app_user(admin_conn, app_password)
    finally:
        admin_conn.close()

    flask_secret_key = generate_flask_secret_key()
    write_env_file(app_password, db_host, db_port, flask_secret_key)

    print("\nSetup complete.")
    print(f" - Database '{APP_DB_NAME}' and its tables are ready.")
    print(f" - Application MySQL user '{APP_DB_USER}' created with a generated password.")
    print(f" - Connection settings written to {ENV_PATH} (not committed to git).")
    print("\nYou can now run: python -m tests.manual_cli")


if __name__ == "__main__":
    main()
