
import sqlite3
import hashlib
import secrets
from datetime import datetime
from getpass import getpass


# Database configuration
DATABASE_NAME = "venueBooking.db"
PASSWORD_ITERATIONS = 600000
MIN_PASSWORD_LENGTH = 8


def connect_database():
    """Connect to the SQLite database and enable foreign keys."""
    connection = sqlite3.connect(DATABASE_NAME)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables():
    """Create all required database tables if they do not exist."""

    connection = connect_database()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_code VARCHAR(15) UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
                    CHECK (role IN ('student', 'staff')),
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS venues (
                venue_id INTEGER PRIMARY KEY,
                venue_name TEXT UNIQUE NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                venue_id INTEGER NOT NULL,
                event_name TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending'
                    CHECK (
                        status IN (
                            'Pending', 'Approved',
                            'Rejected', 'Cancelled'
                        )
                    ),
                reviewed_by INTEGER,
                reviewed_at TEXT,
                rejection_reason TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id)
                    REFERENCES users(user_id),
                FOREIGN KEY (venue_id)
                    REFERENCES venues(venue_id),
                FOREIGN KEY (reviewed_by)
                    REFERENCES users(user_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS booking_equipment (
                booking_id INTEGER NOT NULL,
                equipment_name TEXT NOT NULL,
                other_details TEXT,
                PRIMARY KEY (booking_id, equipment_name),
                FOREIGN KEY (booking_id)
                    REFERENCES bookings(booking_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cancellation_requests (
                cancellation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER NOT NULL,
                requested_by INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending'
                    CHECK (
                        status IN ('Pending', 'Approved', 'Rejected')
                    ),
                reviewed_by INTEGER,
                reviewed_at TEXT,
                reason TEXT,
                FOREIGN KEY (booking_id)
                    REFERENCES bookings(booking_id),
                FOREIGN KEY (requested_by)
                    REFERENCES users(user_id),
                FOREIGN KEY (reviewed_by)
                    REFERENCES users(user_id)
            )
        """)

        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


def insert_venues():
    """Insert the university venues without duplicating existing entries."""

    venues = [
        (1, "Classroom R301"),
        (2, "Classroom R302"),
        (3, "Classroom R303"),
        (4, "Classroom R304"),
        (5, "Classroom R305"),
        (6, "Classroom R306"),
        (7, "Classroom T101"),
        (8, "Classroom T102"),
        (9, "Classroom T103"),
        (10, "Classroom T104"),
        (11, "Lecture Hall LH201"),
        (12, "Lecture Hall LH202"),
        (13, "Lecture Hall LH203"),
        (14, "Lecture Hall LH204"),
        (15, "Lecture Hall S501"),
        (16, "Lecture Hall S502"),
        (17, "President Hall"),
        (18, "PH Foyer"),
        (19, "PH VIP Room"),
        (20, "Gymnasium"),
        (21, "PH WalkWay"),
        (22, "Resource Centre"),
        (23, "RC WalkWay"),
        (24, "Common Room"),
        (25, "Meeting of Minds"),
        (26, "Cafeteria"),
        (27, "Badminton Court"),
        (28, "Tennis Court"),
        (29, "Basketball Court"),
        (30, "Volleyball Court"),
        (31, "Main Field"),
        (32, "RC Field"),
        (33, "Lakeside Field"),
        (34, "Netball Court"),
        (35, "4 in 1 Court"),
        (36, "Others")
    ]

    connection = connect_database()

    try:
        cursor = connection.cursor()

        cursor.executemany("""
            INSERT OR IGNORE INTO venues (venue_id, venue_name)
            VALUES (?, ?)
        """, venues)

        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


def create_demo_staff_account():
    """Create the  DSA staff account if it is absent."""

    staff_id = "DSA001"
    full_name = "DSA  Staff"

    connection = connect_database()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT user_id FROM users WHERE user_code = ?",
            (staff_id,)
        )

        if cursor.fetchone():
            print("DSA  account already exists.")
            return False

        while True:
            password = getpass("Create a demo staff password: ")
            confirm_password = getpass(
                "Confirm the demo staff password: "
            )

            if len(password) < MIN_PASSWORD_LENGTH:
                print(
                    "Password must contain at least "
                    f"{MIN_PASSWORD_LENGTH} characters."
                )
            elif password != confirm_password:
                print("Passwords do not match. Please try again.")
            else:
                break

        # Generate a unique salt and hash the password.
        salt = secrets.token_bytes(16)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            PASSWORD_ITERATIONS
        )

        stored_hash = salt.hex() + "$" + password_hash.hex()

        cursor.execute("""
            INSERT INTO users (
                user_code, full_name, password_hash, role, created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            staff_id,
            full_name,
            stored_hash,
            "staff",
            datetime.now().isoformat(timespec="seconds")
        ))

        connection.commit()
        print("DSA  account created successfully.")
        return True

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


def create_staff_account():
    """Create an additional DSA staff account."""

    staff_id = input("Enter new Staff ID (e.g. DSA002): ").strip()
    full_name = input("Enter staff full name: ").strip()

    if not staff_id or not full_name:
        print("Staff ID and full name are required.")
        return False

    if len(staff_id) > 15:
        print("Staff ID must not exceed 15 characters.")
        return False

    connection = connect_database()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT user_id FROM users WHERE user_code = ?",
            (staff_id,)
        )

        if cursor.fetchone():
            print("This Staff ID already exists. Choose another ID.")
            return False

        password = getpass("Create staff password: ")
        confirm_password = getpass("Confirm staff password: ")

        if len(password) < MIN_PASSWORD_LENGTH:
            print(
                f"Password must contain at least "
                f"{MIN_PASSWORD_LENGTH} characters."
            )
            return False

        elif password != confirm_password:
            print("Passwords do not match.")
            return False

        salt = secrets.token_bytes(16)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            PASSWORD_ITERATIONS
        )

        stored_hash = f"{salt.hex()}${password_hash.hex()}"

        cursor.execute("""
            INSERT INTO users (
                user_code, full_name, password_hash, role, created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            staff_id,
            full_name,
            stored_hash,
            "staff",
            datetime.now().isoformat(timespec="seconds")
        ))

        connection.commit()
        print(f"Staff account {staff_id} created successfully.")
        return True

    except sqlite3.IntegrityError:
        connection.rollback()
        print("This Staff ID already exists.")
        return False

    except sqlite3.Error:
        connection.rollback()
        print("Unable to create staff account.")
        return False

    finally:
        connection.close()



if __name__ == "__main__":
    create_tables()
    insert_venues()

    create_demo_staff_account()

    print("Database tables are ready.")
    print("University venues are ready.")

    while True:
        choice = input(
            "Create another staff account? (y/n): "
        ).strip().lower()

        if choice == "y":
            create_staff_account()

        elif choice == "n":
            print("Staff account setup finished.")
            break

        else:
            print("Please enter y or n.")
