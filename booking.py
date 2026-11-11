
from datetime import datetime, date
from database import connect_database
import csv




def validate_booking_date(booking_date):
    """Check that the booking date is valid and not in the past."""
    try:
        selected_date = datetime.strptime(
            booking_date, "%Y-%m-%d"
        ).date()

        if selected_date < date.today():
            return False, "Booking date cannot be in the past."
        else:
            return True, "Booking date is valid."

    except ValueError:
        return False, "Enter the date in YYYY-MM-DD format."


def validate_booking_time(start_time, end_time):
    """Check that both times are valid and the end is after the start."""
    try:
        start = datetime.strptime(start_time, "%H:%M").time()
        end = datetime.strptime(end_time, "%H:%M").time()

        if start >= end:
            return False, "End time must be later than start time."
        else:
            return True, "Booking times are valid."

    except ValueError:
        return False, "Enter times in HH:MM format, using 24-hour time."


def check_venue_availability(venue_id, booking_date, start_time, end_time):
    """Check whether a venue has overlapping active bookings."""
    connection = connect_database()

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT booking_id, start_time, end_time, status
            FROM bookings
            WHERE venue_id = ?
              AND booking_date = ?
              AND status IN ('Pending', 'Approved')
              AND start_time < ?
              AND end_time > ?
        """, (venue_id, booking_date, end_time, start_time))

        conflicts = cursor.fetchall()

        if conflicts:
            return False, conflicts

        return True, []

    finally:
        connection.close()

def create_booking(
    user_id, role, venue_id, event_name,
    booking_date, start_time, end_time,
    selected_equipment, other_details=""
):
    """Validate and save a new venue booking safely."""

    # Step 1: Validate the event name.
    if not isinstance(event_name, str) or not event_name.strip():
        return False, "Event name is required."

    event_name = event_name.strip()

    # Step 2: Validate the booking date.
    valid, message = validate_booking_date(booking_date)
    if not valid:
        return False, message

    # Step 3: Validate the booking time.
    valid, message = validate_booking_time(start_time, end_time)
    if not valid:
        return False, message

    # Step 4: Validate the role.
    if role not in ("student", "staff"):
        return False, "Invalid user role."

    # Step 5: Validate equipment before saving anything.
    allowed_equipment = {
        "Microphone",
        "Extension cord",
        "Projector",
        "Speakers",
        "Chairs",
        "Other equipment",
    }

    if selected_equipment is None:
        selected_equipment = []
    elif not isinstance(selected_equipment, (list, tuple, set)):
        return False, "Invalid equipment selection."

    selected_equipment = list(dict.fromkeys(selected_equipment))

    if any(item not in allowed_equipment for item in selected_equipment):
        return False, "Invalid equipment selection."

    if "Other equipment" in selected_equipment:
        if not isinstance(other_details, str) or not other_details.strip():
            return False, "Please describe the other equipment."

    connection = connect_database()

    try:
        # Lock the write transaction before checking availability.
        cursor = connection.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        # Step 6: Confirm the user exists and has the supplied role.
        cursor.execute(
            "SELECT role FROM users WHERE user_id = ?",
            (user_id,)
        )
        user = cursor.fetchone()

        if user is None or user[0] != role:
            connection.rollback()
            return False, "Invalid user account or role."

        # Step 7: Check that the venue exists and is active.
        cursor.execute("""
            SELECT venue_id
            FROM venues
            WHERE venue_id = ? AND is_active = 1
        """, (venue_id,))

        if cursor.fetchone() is None:
            connection.rollback()
            return False, "The selected venue does not exist or is inactive."

        # Step 8: Check overlapping bookings in this same transaction.
        cursor.execute("""
            SELECT booking_id
            FROM bookings
            WHERE venue_id = ?
              AND booking_date = ?
              AND status IN ('Pending', 'Approved')
              AND start_time < ?
              AND end_time > ?
        """, (venue_id, booking_date, end_time, start_time))

        if cursor.fetchone():
            connection.rollback()
            return False, "The venue is already booked for that time."

        # Step 9: Students require approval; staff bookings are approved.
        status = "Pending" if role == "student" else "Approved"

        # Step 10: Save the booking.
        cursor.execute("""
            INSERT INTO bookings (
                user_id, venue_id, event_name,
                booking_date, start_time, end_time,
                status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            venue_id,
            event_name,
            booking_date,
            start_time,
            end_time,
            status,
            datetime.now().isoformat(timespec="seconds")
        ))

        booking_id = cursor.lastrowid

        # Step 11: Save the selected equipment.
        for equipment in selected_equipment:
            details = (
                other_details.strip()
                if equipment == "Other equipment"
                else ""
            )

            cursor.execute("""
                INSERT INTO booking_equipment (
                    booking_id, equipment_name, other_details
                )
                VALUES (?, ?, ?)
            """, (booking_id, equipment, details))

        connection.commit()

        return True, (
            f"Booking created successfully. "
            f"Booking ID: {booking_id}. Status: {status}."
        )

    except Exception:
        connection.rollback()
        return False, "Unable to create booking. Please try again."

    finally:
        connection.close()


def approve_booking(booking_id, staff_user_id):
    """Approve a pending booking if the venue is still available."""

    connection = connect_database()
    cursor = connection.cursor()

    try:
        # Start a transaction to protect the availability check.
        cursor.execute("BEGIN IMMEDIATE")

        # Verify that the user is DSA staff.
        cursor.execute(
            "SELECT role FROM users WHERE user_id = ?",
            (staff_user_id,)
        )
        staff = cursor.fetchone()

        if staff is None or staff[0] != "staff":
            return False, "Only DSA staff can approve bookings."

        # Find the pending booking.
        cursor.execute("""
            SELECT venue_id, booking_date, start_time, end_time
            FROM bookings
            WHERE booking_id = ? AND status = 'Pending'
        """, (booking_id,))

        booking = cursor.fetchone()

        if booking is None:
            return False, "Pending booking not found."

        venue_id, booking_date, start_time, end_time = booking

        # Check for other conflicting pending or approved bookings.
        cursor.execute("""
            SELECT booking_id
            FROM bookings
            WHERE venue_id = ?
              AND booking_date = ?
              AND status IN ('Pending', 'Approved')
              AND booking_id != ?
              AND start_time < ?
              AND end_time > ?
        """, (
            venue_id, booking_date, booking_id,
            end_time, start_time
        ))

        if cursor.fetchone():
            return False, (
                "Cannot approve: another booking "
                "conflicts with this time slot."
            )

        # Approve the booking and record the reviewing staff member.
        cursor.execute("""
            UPDATE bookings
            SET status = 'Approved',
                reviewed_by = ?,
                reviewed_at = ?
            WHERE booking_id = ? AND status = 'Pending'
        """, (
            staff_user_id,
            datetime.now().isoformat(timespec="seconds"),
            booking_id
        ))

        connection.commit()
        return True, "Booking approved successfully."

    except Exception:
        connection.rollback()
        return False, "Unable to approve booking."

    finally:
        connection.close()


def reject_booking(booking_id, staff_user_id, reason=""):
    """Reject a pending booking with an optional reason."""

    connection = connect_database()
    cursor = connection.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        # Verify that the user is DSA staff.
        cursor.execute(
            "SELECT role FROM users WHERE user_id = ?",
            (staff_user_id,)
        )
        staff = cursor.fetchone()

        if staff is None or staff[0] != "staff":
            return False, "Only DSA staff can reject bookings."

        # Confirm that the booking is still pending.
        cursor.execute("""
            SELECT booking_id
            FROM bookings
            WHERE booking_id = ? AND status = 'Pending'
        """, (booking_id,))

        if cursor.fetchone() is None:
            return False, "Pending booking not found."

        # Reject the booking and save the optional reason.
        cursor.execute("""
            UPDATE bookings
            SET status = 'Rejected',
                reviewed_by = ?,
                reviewed_at = ?,
                rejection_reason = ?
            WHERE booking_id = ? AND status = 'Pending'
        """, (
            staff_user_id,
            datetime.now().isoformat(timespec="seconds"),
            reason.strip(),
            booking_id
        ))

        connection.commit()
        return True, "Booking rejected successfully."

    except Exception:
        connection.rollback()
        return False, "Unable to reject booking."

    finally:
        connection.close()


def request_booking_cancellation(booking_id, student_user_id, reason=""):
    """Allow a student to request cancellation of their own booking."""

    connection = connect_database()
    cursor = connection.cursor()

    try:
        # Find the booking and check its owner and status.
        cursor.execute("""
            SELECT user_id, status
            FROM bookings
            WHERE booking_id = ?
        """, (booking_id,))

        booking = cursor.fetchone()

        if booking is None:
            return False, "Booking not found."

        owner_id, status = booking

        # Only the student who owns the booking can request cancellation.
        if owner_id != student_user_id:
            return False, "You can only cancel your own booking."

        # Only active bookings can be cancelled.
        if status != "Approved":
            return False, (
                "Only approved bookings can be cancelled."
            )

        # Check for an existing pending cancellation request.
        cursor.execute("""
            SELECT cancellation_id
            FROM cancellation_requests
            WHERE booking_id = ? AND status = 'Pending'
        """, (booking_id,))

        if cursor.fetchone() is not None:
            return False, (
                "A cancellation request is already pending."
            )

        # Save the cancellation request.
        cursor.execute("""
            INSERT INTO cancellation_requests (
                booking_id, requested_by, status, reason
            )
            VALUES (?, ?, 'Pending', ?)
        """, (booking_id, student_user_id, reason.strip()))

        connection.commit()

        return True, (
            "Cancellation request submitted successfully. "
            "Waiting for DSA staff approval."
        )

    except Exception:
        connection.rollback()
        return False, "Unable to submit cancellation request."

    finally:
        connection.close()


def approve_cancellation(cancellation_id, staff_user_id):
    """Approve a student's cancellation request."""

    connection = connect_database()
    cursor = connection.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        # Check that the user is DSA staff.
        cursor.execute(
            "SELECT role FROM users WHERE user_id = ?",
            (staff_user_id,)
        )
        staff = cursor.fetchone()

        if staff is None or staff[0] != "staff":
            return False, "Only DSA staff can review cancellations."

        # Find the pending cancellation request.
        cursor.execute("""
            SELECT booking_id
            FROM cancellation_requests
            WHERE cancellation_id = ? AND status = 'Pending'
        """, (cancellation_id,))

        request = cursor.fetchone()

        if request is None:
            return False, "Pending cancellation request not found."

        booking_id = request[0]

        # Confirm that the original booking is still approved.
        cursor.execute("""
            SELECT booking_id
            FROM bookings
            WHERE booking_id = ? AND status = 'Approved'
        """, (booking_id,))

        if cursor.fetchone() is None:
            return False, "The original booking is not active."

        # Approve the cancellation request.
        cursor.execute("""
            UPDATE cancellation_requests
            SET status = 'Approved',
                reviewed_by = ?,
                reviewed_at = ?
            WHERE cancellation_id = ? AND status = 'Pending'
        """, (
            staff_user_id,
            datetime.now().isoformat(timespec="seconds"),
            cancellation_id
        ))

        # Cancel the original booking.
        cursor.execute("""
            UPDATE bookings
            SET status = 'Cancelled',
                reviewed_by = ?,
                reviewed_at = ?
            WHERE booking_id = ? AND status = 'Approved'
        """, (
            staff_user_id,
            datetime.now().isoformat(timespec="seconds"),
            booking_id
        ))

        connection.commit()
        return True, "Cancellation approved. Booking cancelled."

    except Exception:
        connection.rollback()
        return False, "Unable to approve cancellation."

    finally:
        connection.close()


def reject_cancellation(
    cancellation_id, staff_user_id, reason=""
):
    """Reject a student's cancellation request."""

    connection = connect_database()
    cursor = connection.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        # Check that the user is DSA staff.
        cursor.execute(
            "SELECT role FROM users WHERE user_id = ?",
            (staff_user_id,)
        )
        staff = cursor.fetchone()

        if staff is None or staff[0] != "staff":
            return False, "Only DSA staff can review cancellations."

        # Find the pending cancellation request.
        cursor.execute("""
            SELECT booking_id
            FROM cancellation_requests
            WHERE cancellation_id = ? AND status = 'Pending'
        """, (cancellation_id,))

        request = cursor.fetchone()

        if request is None:
            return False, "Pending cancellation request not found."

        booking_id = request[0]

        # The original booking must still be approved.
        cursor.execute("""
            SELECT booking_id
            FROM bookings
            WHERE booking_id = ? AND status = 'Approved'
        """, (booking_id,))

        if cursor.fetchone() is None:
            return False, "The original booking is not active."

        # Reject the cancellation request.
        cursor.execute("""
            UPDATE cancellation_requests
            SET status = 'Rejected',
                reviewed_by = ?,
                reviewed_at = ?,
                reason = ?
            WHERE cancellation_id = ? AND status = 'Pending'
        """, (
            staff_user_id,
            datetime.now().isoformat(timespec="seconds"),
            reason.strip(),
            cancellation_id
        ))

        connection.commit()
        return True, "Cancellation request rejected."

    except Exception:
        connection.rollback()
        return False, "Unable to reject cancellation."

    finally:
        connection.close()


def get_all_bookings():
    """Retrieve all bookings with their user and venue details."""

    connection = connect_database()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                b.booking_id,
                u.full_name,
                u.role,
                v.venue_name,
                b.event_name,
                b.booking_date,
                b.start_time,
                b.end_time,
                b.status
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN venues v ON b.venue_id = v.venue_id
            ORDER BY b.booking_date, b.start_time
        """)

        records = cursor.fetchall()

        bookings = []

        for record in records:
            booking = {
                "booking_id": record[0],
                "full_name": record[1],
                "role": record[2],
                "venue_name": record[3],
                "event_name": record[4],
                "booking_date": record[5],
                "start_time": record[6],
                "end_time": record[7],
                "status": record[8]
            }

            bookings.append(booking)

        return bookings

    finally:
        connection.close()


def export_bookings_to_csv(filename="booking_records.csv"):
    """Export all booking records to a CSV file."""

    bookings = get_all_bookings()

    if not bookings:
        return False, "There are no booking records to export."

    fieldnames = [
        "booking_id",
        "full_name",
        "role",
        "venue_name",
        "event_name",
        "booking_date",
        "start_time",
        "end_time",
        "status"
    ]

    try:
        with open(
            filename, "w", newline="", encoding="utf-8-sig"
        ) as file:
            writer = csv.DictWriter(
                file, fieldnames=fieldnames
            )

            writer.writeheader()

            for booking in bookings:
                writer.writerow(booking)

        return True, (
            f"Exported {len(bookings)} booking records "
            f"to {filename}."
        )

    except OSError:
        return False, "Unable to save the CSV file."


    
def get_booking_summary(booking_id):
    """Retrieve one booking and its selected equipment."""

    connection = connect_database()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                b.booking_id,
                u.full_name,
                u.role,
                v.venue_name,
                b.event_name,
                b.booking_date,
                b.start_time,
                b.end_time,
                b.status,
                b.rejection_reason
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN venues v ON b.venue_id = v.venue_id
            WHERE b.booking_id = ?
        """, (booking_id,))

        record = cursor.fetchone()

        if record is None:
            return None

        cursor.execute("""
            SELECT equipment_name, other_details
            FROM booking_equipment
            WHERE booking_id = ?
            ORDER BY equipment_name
        """, (booking_id,))

        equipment_records = cursor.fetchall()

        equipment = []

        for item in equipment_records:
            if item[1]:
                equipment.append(
                    f"{item[0]}: {item[1]}"
                )
            else:
                equipment.append(item[0])

        summary = {
            "booking_id": record[0],
            "full_name": record[1],
            "role": record[2],
            "venue_name": record[3],
            "event_name": record[4],
            "booking_date": record[5],
            "start_time": record[6],
            "end_time": record[7],
            "status": record[8],
            "rejection_reason": record[9],
            "equipment": equipment
        }

        return summary

    finally:
        connection.close()


def get_all_cancellation_requests():
    """Retrieve cancellation requests with their booking details."""

    connection = connect_database()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                cr.cancellation_id,
                cr.booking_id,
                requester.full_name,
                v.venue_name,
                b.event_name,
                b.booking_date,
                b.start_time,
                b.end_time,
                cr.status,
                cr.reason
            FROM cancellation_requests cr
            JOIN bookings b
                ON cr.booking_id = b.booking_id
            JOIN users requester
                ON cr.requested_by = requester.user_id
            JOIN venues v
                ON b.venue_id = v.venue_id
            ORDER BY cr.cancellation_id DESC
        """)

        rows = cursor.fetchall()

        requests = []

        for row in rows:
            requests.append({
                "cancellation_id": row[0],
                "booking_id": row[1],
                "requested_by": row[2],
                "venue_name": row[3],
                "event_name": row[4],
                "booking_date": row[5],
                "start_time": row[6],
                "end_time": row[7],
                "status": row[8],
                "reason": row[9]
            })

        return requests

    finally:
        connection.close()

def get_all_venues():
    """Retrieve all active venues for the booking form."""

    connection = connect_database()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT venue_id, venue_name
            FROM venues
            WHERE is_active = 1
            ORDER BY venue_id
        """)

        rows = cursor.fetchall()

        venues = []

        for row in rows:
            venues.append({
                "venue_id": row[0],
                "venue_name": row[1]
            })

        return venues

    finally:
        connection.close()


def cancel_staff_booking(booking_id, staff_user_id):
    """Allow staff to directly cancel their own approved booking."""
    connection = connect_database()

    try:
        cursor = connection.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        # Verify the account belongs to DSA staff.
        cursor.execute(
            "SELECT role FROM users WHERE user_id = ?",
            (staff_user_id,)
        )
        staff = cursor.fetchone()

        if staff is None or staff[0] != "staff":
            connection.rollback()
            return False, "Only DSA staff can use this function."

        # Staff can directly cancel only their own approved booking.
        cursor.execute("""
            SELECT booking_id
            FROM bookings
            WHERE booking_id = ?
              AND user_id = ?
              AND status = 'Approved'
        """, (booking_id, staff_user_id))

        if cursor.fetchone() is None:
            connection.rollback()
            return False, (
                "You can only directly cancel your own approved bookings."
            )

        cursor.execute("""
            UPDATE bookings
            SET status = 'Cancelled',
                reviewed_by = ?,
                reviewed_at = ?
            WHERE booking_id = ?
              AND user_id = ?
              AND status = 'Approved'
        """, (
            staff_user_id,
            datetime.now().isoformat(timespec="seconds"),
            booking_id,
            staff_user_id
        ))

        connection.commit()
        return True, "Your booking has been cancelled successfully."

    except Exception:
        connection.rollback()
        return False, "Unable to cancel the booking. Please try again."

    finally:
        connection.close()
