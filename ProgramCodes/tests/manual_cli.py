from backend.auth import AuthError, login_user, register_user
from backend.password_generator import generate_password
from backend.vault import add_entry, delete_entry, list_entries

session = {"user_id": None, "vault_key": None, "username": None}


def cmd_register():
    username = input("Choose a username: ").strip()
    email = input("Email: ").strip()
    password = input("Choose a master password: ").strip()
    try:
        user_id = register_user(username, email, password)
        print(f"Registered user '{username}' with id {user_id}.")
    except AuthError as e:
        print(f"Registration failed: {e}")


def cmd_login():
    username = input("Username: ").strip()
    password = input("Master password: ").strip()
    try:
        user_id, vault_key = login_user(username, password)
        session.update(user_id=user_id, vault_key=vault_key, username=username)
        print(f"Logged in as '{username}'.")
    except AuthError as e:
        print(f"Login failed: {e}")


def require_login() -> bool:
    if session["user_id"] is None:
        print("You must log in first.")
        return False
    return True


def cmd_generate():
    length = int(input("Password length [16]: ") or 16)
    print("Generated password:", generate_password(length))


def cmd_add():
    if not require_login():
        return
    site_name = input("Site name: ").strip()
    site_username = input("Site username/email: ").strip()
    choice = input("Generate a random password? [y/N]: ").strip().lower()
    if choice == "y":
        site_password = generate_password()
        print("Generated password:", site_password)
    else:
        site_password = input("Site password: ").strip()
    entry_id = add_entry(session["user_id"], site_name, site_username, site_password, session["vault_key"])
    print(f"Saved entry id {entry_id}.")


def cmd_list():
    if not require_login():
        return
    entries = list_entries(session["user_id"], session["vault_key"])
    if not entries:
        print("No saved entries.")
    for entry in entries:
        print(f"[{entry['id']}] {entry['site_name']} | {entry['site_username']} | {entry['password']}")


def cmd_delete():
    if not require_login():
        return
    entry_id = int(input("Entry id to delete: "))
    delete_entry(entry_id, session["user_id"])
    print("Deleted (if it existed and belonged to you).")


MENU = {
    "1": ("Register", cmd_register),
    "2": ("Login", cmd_login),
    "3": ("Generate password", cmd_generate),
    "4": ("Add vault entry", cmd_add),
    "5": ("List vault entries", cmd_list),
    "6": ("Delete vault entry", cmd_delete),
    "0": ("Exit", None),
}


def main():
    while True:
        print("\n--- Password Manager CLI ---")
        for key, (label, _) in MENU.items():
            print(f"{key}. {label}")
        choice = input("Choose: ").strip()
        if choice == "0":
            break
        action = MENU.get(choice)
        if action is None:
            print("Invalid choice.")
            continue
        action[1]()


if __name__ == "__main__":
    main()
