import re

# Example list of common passwords (extend this list as needed)

def is_strong_password(password: str) -> bool:
    common_passwords = ["password", "123456", "qwerty", "111111", "123123"]
    # Define the password constraints
    min_length = 8
    max_length = 20
    special_characters = "!@#$%^&*()-+"

    # Check the length of the password
    if len(password) < min_length or len(password) > max_length:
        return False

    # Check if the password is a common password
    if password in common_passwords:
        return False

    # Check for at least one uppercase letter
    if not re.search(r"[A-Z]", password):
        return False

    # Check for at least one lowercase letter
    if not re.search(r"[a-z]", password):
        return False

    # Check for at least one digit
    if not re.search(r"\d", password):
        return False

    # Check for at least one special character
    if not any(char in special_characters for char in password):
        return False

    return True