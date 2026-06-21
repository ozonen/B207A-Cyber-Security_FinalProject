import secrets
import string

_LOWER = string.ascii_lowercase
_UPPER = string.ascii_uppercase
_DIGITS = string.digits
_SYMBOLS = "!@#$%^&*()-_=+[]{}"


def generate_password(length: int = 16, use_symbols: bool = True) -> str:
    if length < 8:
        raise ValueError("Password length must be at least 8 characters.")

    categories = [_LOWER, _UPPER, _DIGITS]
    if use_symbols:
        categories.append(_SYMBOLS)

    password_chars = [secrets.choice(category) for category in categories]
    all_chars = "".join(categories)
    password_chars += [secrets.choice(all_chars) for _ in range(length - len(categories))]

    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)
