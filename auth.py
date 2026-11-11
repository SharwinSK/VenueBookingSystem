
import hashlib
import secrets
import sqlite3
from datetime import datetime

from database import connect_database


PASSWORD_ITERATIONS = 600000
MIN_PASSWORD_LENGTH = 8
MAX_STUDENT_ID_LENGTH = 15


def hash_password(password):
    """Hash a password securely using a random salt."""
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS
    )

    return f"{salt.hex()}${password_hash.hex()}"


def verify_password(password, stored_hash):
    """Verify a password against its stored salted hash."""
    if not isinstance(password, str):
        return False

    if not isinstance(stored_hash, str):
        return False

    try:
        salt_hex, hash_hex = stored_hash.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            PASSWORD_ITERATIONS
        )

        return secrets.compare_digest(
            actual_hash,
            expected_hash
        )

    except (ValueError, TypeError):
        return False


def register_student(student_id, full_name, password, confirm_password):
    """Validate student details and create a new account."""

    if not all(
        isinstance(value, str)
        for value in (student_id, full_name, password, confirm_password)
    ):
        return False, "Please enter valid registration details."

    student_id = student_id.strip()
    full_name = full_name.strip()

    if (
        not student_id.isdigit()
        or len(student_id) > MAX_STUDENT_ID_LENGTH
    ):
        return False, "Student ID must contain 1 to 15 digits."

    elif not full_name:
        return False, "Full name is required."

    elif len(password) < MIN_PASSWORD_LENGTH:
        return False, "Password must contain at least 8 characters."

    elif password != confirm_password:
        return False, "Passwords do not match."

    password_hash = hash_password(password)
    connection = connect_database()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO users (
                user_code,
                full_name,
                password_hash,
                role,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            student_id,
            full_name,
            password_hash,
            "student",
            datetime.now().isoformat(timespec="seconds")
        ))

        connection.commit()
        return True, "Student registration successful."

    except sqlite3.IntegrityError as error:
        connection.rollback()

        if "users.user_code" in str(error):
            return False, "This Student ID is already registered."

        return False, "Registration failed. Please check the details."

    except sqlite3.Error:
        connection.rollback()
        return False, "Registration failed. Please try again."

    finally:
        connection.close()


def login_user(user_code, password):
    """Authenticate a user and return their account details."""

    if not isinstance(user_code, str) or not isinstance(password, str):
        return None, "Please enter your ID and password."

    user_code = user_code.strip()

    if not user_code or not password:
        return None, "Please enter your ID and password."

    connection = connect_database()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                user_id,
                user_code,
                full_name,
                password_hash,
                role
            FROM users
            WHERE user_code = ?
        """, (user_code,))

        user = cursor.fetchone()

    except sqlite3.Error:
        return None, "Unable to access the database. Please try again."

    finally:
        connection.close()

    if user is None:
        return None, "Invalid ID or password."

    user_id, saved_code, full_name, stored_hash, role = user

    if not verify_password(password, stored_hash):
        return None, "Invalid ID or password."

    user_details = {
        "user_id": user_id,
        "user_code": saved_code,
        "full_name": full_name,
        "role": role
    }

    return user_details, "Login successful."
