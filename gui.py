
import tkinter as tk
from tkinter import messagebox

from auth import login_user, register_student

from booking import (
    create_booking,
    get_all_bookings,
    get_booking_summary,
    request_booking_cancellation,
    approve_booking,
    reject_booking,
    export_bookings_to_csv,
    get_all_cancellation_requests,
    approve_cancellation,
    reject_cancellation,
    get_all_venues,
    cancel_staff_booking,
)




# Green theme colours
BG_COLOR = "#EAF5EC"
DARK_GREEN = "#176B45"
BUTTON_GREEN = "#218838"
HOVER_GREEN = "#145A32"
WHITE = "#FFFFFF"
TEXT_COLOR = "#244B35"
MUTED_GREEN = "#64816D"
BORDER_GREEN = "#C8E2CE"


def create_registration_window(root):
    """Open the student registration form."""

    window = tk.Toplevel(root)
    window.title("Student Registration")
    window.geometry("480x560")
    window.resizable(False, False)
    window.configure(bg=BG_COLOR)
    window.transient(root)

    tk.Label(
        window,
        text="STUDENT REGISTRATION",
        font=("Arial", 18, "bold"),
        bg=BG_COLOR,
        fg=DARK_GREEN
    ).pack(pady=(25, 5))

    tk.Label(
        window,
        text="Create your Nilai University account",
        font=("Arial", 10),
        bg=BG_COLOR,
        fg=MUTED_GREEN
    ).pack(pady=(0, 15))

    form = tk.Frame(
        window,
        bg=WHITE,
        padx=25,
        pady=20,
        highlightbackground=BORDER_GREEN,
        highlightthickness=1
    )
    form.pack(padx=30, fill="x")

    # Registration input fields
    fields = [
        ("Student ID (up to 15 digits)", False),
        ("Full Name", False),
        ("Password (minimum 8 characters)", True),
        ("Confirm Password", True)
    ]

    entries = []

    for label_text, is_password in fields:
        tk.Label(
            form,
            text=label_text,
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=TEXT_COLOR
        ).pack(anchor="w", pady=(5, 0))

        entry = tk.Entry(
            form,
            font=("Arial", 11),
            show="*" if is_password else "",
            relief="solid",
            bd=1
        )
        entry.pack(fill="x", pady=(5, 10), ipady=4)
        entries.append(entry)

    def handle_registration():
        """Validate and submit the student registration form."""

        student_id = entries[0].get().strip()
        full_name = entries[1].get().strip()
        password = entries[2].get()
        confirm_password = entries[3].get()

        if not all([student_id, full_name, password, confirm_password]):
            messagebox.showerror(
                "Missing Information",
                "Please complete all fields.",
                parent=window
            )
            return

        success, message = register_student(
            student_id,
            full_name,
            password,
            confirm_password
        )

        if success:
            messagebox.showinfo(
                "Registration Successful",
                message,
                parent=window
            )
            window.destroy()
        else:
            messagebox.showerror(
                "Registration Failed",
                message,
                parent=window
            )

    tk.Button(
        form,
        text="REGISTER",
        command=handle_registration,
        font=("Arial", 11, "bold"),
        bg=BUTTON_GREEN,
        fg=WHITE,
        activebackground=HOVER_GREEN,
        activeforeground=WHITE,
        cursor="hand2",
        relief="flat",
        bd=0,
        pady=9
    ).pack(fill="x", pady=(10, 0))

    tk.Button(
        window,
        text="CLOSE",
        command=window.destroy,
        font=("Arial", 10),
        bg=BG_COLOR,
        fg=DARK_GREEN,
        activebackground=BORDER_GREEN,
        cursor="hand2",
        relief="flat"
    ).pack(pady=12)

    entries[0].focus_set()


def create_login_window():
    """Create the green-themed login window."""

    root = tk.Tk()
    root.title("Nilai University Venue Booking System")
    root.geometry("500x500")
    root.resizable(False, False)
    root.configure(bg=BG_COLOR)

    tk.Label(
        root,
        text="NILAI UNIVERSITY",
        font=("Arial", 21, "bold"),
        bg=BG_COLOR,
        fg=DARK_GREEN
    ).pack(pady=(30, 5))

    tk.Label(
        root,
        text="Venue Booking System",
        font=("Arial", 13),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(pady=(0, 22))

    form = tk.Frame(
        root,
        bg=WHITE,
        padx=28,
        pady=24,
        highlightbackground=BORDER_GREEN,
        highlightthickness=1
    )
    form.pack(padx=35, fill="x")

    tk.Label(
        form,
        text="Student ID / Staff ID",
        font=("Arial", 10, "bold"),
        bg=WHITE,
        fg=TEXT_COLOR
    ).pack(anchor="w")

    user_id_entry = tk.Entry(form, font=("Arial", 11), relief="solid", bd=1)
    user_id_entry.pack(fill="x", pady=(7, 18), ipady=5)

    tk.Label(
        form,
        text="Password",
        font=("Arial", 10, "bold"),
        bg=WHITE,
        fg=TEXT_COLOR
    ).pack(anchor="w")

    password_entry = tk.Entry(
        form, font=("Arial", 11), show="*", relief="solid", bd=1
    )
    password_entry.pack(fill="x", pady=(7, 18), ipady=5)

    def handle_login():
        """Validate login fields and authenticate the user."""

        user_code = user_id_entry.get().strip()
        password = password_entry.get()

        if not user_code or not password:
            messagebox.showerror(
                "Missing Information",
                "Please enter your ID and password.",
                parent=root
            )
            return

        user, message = login_user(user_code, password)

        if user is None:
            messagebox.showerror(
                "Login Failed", message, parent=root
            )
            return

       
        # Open the correct dashboard based on the user's role.
        if user["role"] == "student":
            create_student_dashboard(root, user)

        elif user["role"] == "staff":
            create_staff_dashboard(root, user)

    tk.Button(
        form,
        text="LOGIN",
        command=handle_login,
        font=("Arial", 11, "bold"),
        bg=BUTTON_GREEN,
        fg=WHITE,
        activebackground=HOVER_GREEN,
        activeforeground=WHITE,
        cursor="hand2",
        relief="flat",
        bd=0,
        pady=10
    ).pack(fill="x", pady=(2, 0))

    tk.Button(
        root,
        text="REGISTER AS A STUDENT",
        command=lambda: create_registration_window(root),
        font=("Arial", 10, "bold"),
        bg=BG_COLOR,
        fg=DARK_GREEN,
        activebackground=BORDER_GREEN,
        cursor="hand2",
        relief="flat",
        bd=0
    ).pack(pady=(15, 5))

    tk.Label(
        root,
        text="Student and DSA Staff Access",
        font=("Arial", 9),
        bg=BG_COLOR,
        fg=MUTED_GREEN
    ).pack(pady=5)

    user_id_entry.focus_set()
    root.mainloop()


def create_student_dashboard(root, user):
    """Display the main dashboard for a logged-in student."""

    dashboard = tk.Toplevel(root)
    dashboard.title("Student Dashboard")
    dashboard.geometry("850x600")
    dashboard.configure(bg=BG_COLOR)
    dashboard.minsize(700, 500)

    tk.Label(
        dashboard,
        text="STUDENT DASHBOARD",
        font=("Arial", 22, "bold"),
        bg=BG_COLOR,
        fg=DARK_GREEN
    ).pack(pady=(25, 5))

    tk.Label(
        dashboard,
        text=f"Welcome, {user['full_name']}!",
        font=("Arial", 12),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(pady=(0, 15))

    buttons = tk.Frame(dashboard, bg=BG_COLOR)
    buttons.pack(fill="x", padx=25, pady=10)

    tk.Button(
        buttons,
        text="New Venue Booking",
        command=lambda: create_booking_window(dashboard, user),
        bg=BUTTON_GREEN,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        pady=8
    ).pack(fill="x", pady=5)


    tk.Button(
        buttons,
        text="View All Bookings",
        command=lambda: show_student_bookings(dashboard),
        bg=BUTTON_GREEN,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        pady=8
    ).pack(fill="x", pady=5)

    tk.Button(
        buttons,
        text="View Booking Summary",
        command=lambda: show_booking_summary(dashboard),
        bg=BUTTON_GREEN,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        pady=8
    ).pack(fill="x", pady=5)

    tk.Button(
        buttons,
        text="Request Booking Cancellation",
        command=lambda: request_cancellation_window(
            dashboard, user
        ),
        bg=BUTTON_GREEN,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        pady=8
    ).pack(fill="x", pady=5)

    tk.Button(
        buttons,
        text="Logout",
        command=dashboard.destroy,
        bg=DARK_GREEN,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        pady=8
    ).pack(fill="x", pady=5)

    tk.Label(
        dashboard,
        text="Nilai University Venue Booking System",
        font=("Arial", 9),
        bg=BG_COLOR,
        fg=MUTED_GREEN
    ).pack(side="bottom", pady=15)

def show_student_bookings(parent):
    """Display all booking records in a table."""

    from tkinter import ttk

    window = tk.Toplevel(parent)
    window.title("All Booking Records")
    window.geometry("1000x450")
    window.configure(bg=BG_COLOR)

    tk.Label(
        window,
        text="ALL BOOKING RECORDS",
        font=("Arial", 18, "bold"),
        bg=BG_COLOR,
        fg=DARK_GREEN
    ).pack(pady=15)

    columns = (
        "ID", "Name", "Venue", "Event",
        "Date", "Start", "End", "Status"
    )

    table = ttk.Treeview(
        window,
        columns=columns,
        show="headings"
    )

    for column in columns:
        table.heading(column, text=column)
        table.column(column, width=110, anchor="center")

    table.column("ID", width=55)
    table.column("Event", width=180)

    scrollbar = ttk.Scrollbar(
        window,
        orient="vertical",
        command=table.yview
    )
    table.configure(yscrollcommand=scrollbar.set)

    table.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(15, 0),
        pady=10
    )
    scrollbar.pack(side="right", fill="y", padx=(0, 15), pady=10)

    bookings = get_all_bookings()

    for booking in bookings:
        table.insert(
            "",
            "end",
            values=(
                booking["booking_id"],
                booking["full_name"],
                booking["venue_name"],
                booking["event_name"],
                booking["booking_date"],
                booking["start_time"],
                booking["end_time"],
                booking["status"]
            )
        )

    if not bookings:
        messagebox.showinfo(
            "No Records",
            "There are no booking records yet.",
            parent=window
        )


def show_booking_summary(parent):
    """Display the summary for one booking."""

    window = tk.Toplevel(parent)
    window.title("Booking Summary")
    window.geometry("520x550")
    window.configure(bg=BG_COLOR)
    window.resizable(False, False)

    tk.Label(
        window,
        text="BOOKING SUMMARY",
        font=("Arial", 20, "bold"),
        bg=BG_COLOR,
        fg=DARK_GREEN
    ).pack(pady=(25, 15))

    form = tk.Frame(
        window,
        bg=WHITE,
        padx=25,
        pady=20
    )
    form.pack(fill="x", padx=30)

    tk.Label(
        form,
        text="Enter Booking ID",
        font=("Arial", 10, "bold"),
        bg=WHITE,
        fg=TEXT_COLOR
    ).pack(anchor="w")

    booking_id_entry = tk.Entry(form, font=("Arial", 11))
    booking_id_entry.pack(fill="x", pady=8)

    result_frame = tk.Frame(
        window,
        bg=WHITE,
        padx=20,
        pady=15
    )
    result_frame.pack(fill="both", expand=True, padx=30, pady=15)

    def search_booking():
        """Find and display the selected booking."""

        booking_id_text = booking_id_entry.get().strip()

        if not booking_id_text.isdigit():
            messagebox.showerror(
                "Invalid Booking ID",
                "Please enter a numeric Booking ID.",
                parent=window
            )
            return

        summary = get_booking_summary(int(booking_id_text))

        if summary is None:
            messagebox.showerror(
                "Not Found",
                "No booking was found with that ID.",
                parent=window
            )
            return

        # Clear the previous summary before displaying another.
        for widget in result_frame.winfo_children():
            widget.destroy()

        details = [
            ("Booking ID", summary["booking_id"]),
            ("Name", summary["full_name"]),
            ("Role", summary["role"].title()),
            ("Venue", summary["venue_name"]),
            ("Event", summary["event_name"]),
            ("Date", summary["booking_date"]),
            (
                "Time",
                f"{summary['start_time']} - "
                f"{summary['end_time']}"
            ),
            ("Status", summary["status"]),
            (
                "Equipment",
                ", ".join(summary["equipment"])
                if summary["equipment"]
                else "None"
            )
        ]

        if summary["rejection_reason"]:
            details.append(
                ("Rejection Reason", summary["rejection_reason"])
            )

        for label_text, value in details:
            tk.Label(
                result_frame,
                text=f"{label_text}: {value}",
                font=("Arial", 10),
                bg=WHITE,
                fg=TEXT_COLOR,
                anchor="w",
                wraplength=430,
                justify="left"
            ).pack(fill="x", pady=3)

    tk.Button(
        form,
        text="SEARCH BOOKING",
        command=search_booking,
        font=("Arial", 10, "bold"),
        bg=BUTTON_GREEN,
        fg=WHITE,
        activebackground=HOVER_GREEN,
        activeforeground=WHITE,
        cursor="hand2",
        relief="flat",
        pady=8
    ).pack(fill="x", pady=(5, 0))


def request_cancellation_window(parent, user):
    """Allow a student to request cancellation of a booking."""

    window = tk.Toplevel(parent)
    window.title("Request Booking Cancellation")
    window.geometry("520x420")
    window.configure(bg=BG_COLOR)
    window.resizable(False, False)

    tk.Label(
        window,
        text="REQUEST CANCELLATION",
        font=("Arial", 18, "bold"),
        bg=BG_COLOR,
        fg=DARK_GREEN
    ).pack(pady=(25, 8))

    tk.Label(
        window,
        text="Your request must be reviewed by DSA staff.",
        font=("Arial", 10),
        bg=BG_COLOR,
        fg=MUTED_GREEN
    ).pack(pady=(0, 15))

    form = tk.Frame(
        window,
        bg=WHITE,
        padx=25,
        pady=20
    )
    form.pack(fill="x", padx=30)

    tk.Label(
        form,
        text="Booking ID",
        font=("Arial", 10, "bold"),
        bg=WHITE,
        fg=TEXT_COLOR
    ).pack(anchor="w")

    booking_id_entry = tk.Entry(form, font=("Arial", 11))
    booking_id_entry.pack(fill="x", pady=(5, 15))

    tk.Label(
        form,
        text="Reason for Cancellation (optional)",
        font=("Arial", 10, "bold"),
        bg=WHITE,
        fg=TEXT_COLOR
    ).pack(anchor="w")

    reason_entry = tk.Entry(form, font=("Arial", 11))
    reason_entry.pack(fill="x", pady=(5, 15))

    def submit_request():
        """Validate and submit the cancellation request."""

        booking_id_text = booking_id_entry.get().strip()

        if not booking_id_text.isdigit():
            messagebox.showerror(
                "Invalid Booking ID",
                "Please enter a numeric Booking ID.",
                parent=window
            )
            return

        success, message = request_booking_cancellation(
            int(booking_id_text),
            user["user_id"],
            reason_entry.get()
        )

        if success:
            messagebox.showinfo(
                "Request Submitted",
                message,
                parent=window
            )
            window.destroy()
        else:
            messagebox.showerror(
                "Request Failed",
                message,
                parent=window
            )

    tk.Button(
        form,
        text="SUBMIT CANCELLATION REQUEST",
        command=submit_request,
        font=("Arial", 10, "bold"),
        bg=BUTTON_GREEN,
        fg=WHITE,
        activebackground=HOVER_GREEN,
        activeforeground=WHITE,
        cursor="hand2",
        relief="flat",
        pady=9
    ).pack(fill="x")

    tk.Label(
        window,
        text="The booking remains active until DSA approves.",
        font=("Arial", 9),
        bg=BG_COLOR,
        fg=MUTED_GREEN
    ).pack(pady=15)


def create_staff_dashboard(root, user):
    """Display the main dashboard for DSA staff."""

    dashboard = tk.Toplevel(root)
    dashboard.title("DSA Staff Dashboard")
    dashboard.geometry("850x600")
    dashboard.configure(bg=BG_COLOR)
    dashboard.minsize(700, 500)

    tk.Label(
        dashboard,
        text="DSA STAFF DASHBOARD",
        font=("Arial", 22, "bold"),
        bg=BG_COLOR,
        fg=DARK_GREEN
    ).pack(pady=(25, 5))

    tk.Label(
        dashboard,
        text=f"Welcome, {user['full_name']}!",
        font=("Arial", 12),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(pady=(0, 15))

    buttons = tk.Frame(dashboard, bg=BG_COLOR)
    buttons.pack(fill="x", padx=25, pady=10)

    tk.Button(
        buttons,
        text="View All Bookings",
        command=lambda: show_student_bookings(dashboard),
        bg=BUTTON_GREEN,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        pady=8
    ).pack(fill="x", pady=5)

    tk.Button(
        buttons,
        text="Approve / Reject Bookings",
        command=lambda: booking_review_window(dashboard, user),
        bg=BUTTON_GREEN,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        pady=8
    ).pack(fill="x", pady=5)

    tk.Button(
        buttons,
        text="Review Cancellation Requests",
        command=lambda: cancellation_review_window(dashboard, user),
        bg=BUTTON_GREEN,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        pady=8
    ).pack(fill="x", pady=5)

    tk.Button(
        buttons,
        text="Create Staff Booking",
        command=lambda: create_booking_window(dashboard, user),
        bg=BUTTON_GREEN,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        pady=8
    ).pack(fill="x", pady=5)


    tk.Button(
        buttons,
        text="Cancel My Confirmed Booking",
        command=lambda: staff_cancel_booking_window(
            dashboard, user
        ),
        bg=BUTTON_GREEN,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        pady=8
    ).pack(fill="x", pady=5)

    tk.Button(
        buttons,
        text="Export Bookings to CSV",
        command=export_bookings_window,
        bg=BUTTON_GREEN,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        pady=8
    ).pack(fill="x", pady=5)

    tk.Button(
        buttons,
        text="Logout",
        command=dashboard.destroy,
        bg=DARK_GREEN,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        pady=8
    ).pack(fill="x", pady=5)

    tk.Label(
        dashboard,
        text="Nilai University Venue Booking System",
        font=("Arial", 9),
        bg=BG_COLOR,
        fg=MUTED_GREEN
    ).pack(side="bottom", pady=15)


def booking_review_window(parent, user):
    """Allow DSA staff to approve or reject student bookings."""

    from tkinter import ttk

    window = tk.Toplevel(parent)
    window.title("Review Booking Requests")
    window.geometry("1000x550")
    window.configure(bg=BG_COLOR)

    tk.Label(
        window,
        text="REVIEW BOOKING REQUESTS",
        font=("Arial", 20, "bold"),
        bg=BG_COLOR,
        fg=DARK_GREEN
    ).pack(pady=15)

    tk.Label(
        window,
        text="Select a pending booking, then approve or reject it.",
        font=("Arial", 10),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(pady=(0, 10))

    columns = (
        "ID", "Name", "Venue", "Event",
        "Date", "Start", "End", "Status"
    )

    table = ttk.Treeview(
        window,
        columns=columns,
        show="headings",
        height=10
    )

    for column in columns:
        table.heading(column, text=column)
        table.column(column, width=110, anchor="center")

    table.column("ID", width=50)
    table.column("Event", width=160)
    table.pack(fill="both", expand=True, padx=15, pady=5)

    def refresh_pending_bookings():
        """Refresh the list of pending booking requests."""

        for item in table.get_children():
            table.delete(item)

        for booking in get_all_bookings():
            if booking["status"] == "Pending" and booking["role"] == "student":
                table.insert(
                    "",
                    "end",
                    values=(
                        booking["booking_id"],
                        booking["full_name"],
                        booking["venue_name"],
                        booking["event_name"],
                        booking["booking_date"],
                        booking["start_time"],
                        booking["end_time"],
                        booking["status"]
                    )
                )

    tk.Label(
        window,
        text="Selected Booking ID",
        font=("Arial", 10, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(pady=(10, 0))

    booking_id_entry = tk.Entry(window, font=("Arial", 11))
    booking_id_entry.pack(pady=5)

    def select_booking(event):
        """Copy the selected table row's booking ID into the entry."""

        selected = table.selection()

        if selected:
            values = table.item(selected[0], "values")
            booking_id_entry.delete(0, tk.END)
            booking_id_entry.insert(0, values[0])

    table.bind("<<TreeviewSelect>>", select_booking)

    tk.Label(
        window,
        text="Rejection Reason (optional)",
        font=("Arial", 10, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(pady=(5, 0))

    reason_entry = tk.Entry(window, font=("Arial", 11), width=50)
    reason_entry.pack(pady=5)

    def approve_selected_booking():
        """Approve the selected pending booking."""

        booking_id = booking_id_entry.get().strip()

        if not booking_id.isdigit():
            messagebox.showerror(
                "Invalid Booking ID",
                "Please select a booking or enter a numeric Booking ID.",
                parent=window
            )
            return

        success, message = approve_booking(
            int(booking_id),
            user["user_id"]
        )

        if success:
            messagebox.showinfo(
                "Booking Approved",
                message,
                parent=window
            )
            refresh_pending_bookings()
            booking_id_entry.delete(0, tk.END)
        else:
            messagebox.showerror(
                "Approval Failed",
                message,
                parent=window
            )
            refresh_pending_bookings()

    def reject_selected_booking():
        """Reject the selected pending booking."""

        booking_id = booking_id_entry.get().strip()

        if not booking_id.isdigit():
            messagebox.showerror(
                "Invalid Booking ID",
                "Please select a booking or enter a numeric Booking ID.",
                parent=window
            )
            return

        success, message = reject_booking(
            int(booking_id),
            user["user_id"],
            reason_entry.get().strip()
        )

        if success:
            messagebox.showinfo(
                "Booking Rejected",
                message,
                parent=window
            )
            refresh_pending_bookings()
            booking_id_entry.delete(0, tk.END)
            reason_entry.delete(0, tk.END)
        else:
            messagebox.showerror(
                "Rejection Failed",
                message,
                parent=window
            )
            refresh_pending_bookings()

    buttons = tk.Frame(window, bg=BG_COLOR)
    buttons.pack(pady=15)

    tk.Button(
        buttons,
        text="APPROVE BOOKING",
        command=approve_selected_booking,
        bg=BUTTON_GREEN,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        padx=15,
        pady=8
    ).pack(side="left", padx=10)

    tk.Button(
        buttons,
        text="REJECT BOOKING",
        command=reject_selected_booking,
        bg="#B83232",
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        padx=15,
        pady=8
    ).pack(side="left", padx=10)

    refresh_pending_bookings()


def cancellation_review_window(parent, user):
    """Allow DSA staff to review student cancellation requests."""

    from tkinter import ttk

    window = tk.Toplevel(parent)
    window.title("Review Cancellation Requests")
    window.geometry("1050x500")
    window.configure(bg=BG_COLOR)

    tk.Label(
        window,
        text="REVIEW CANCELLATION REQUESTS",
        font=("Arial", 19, "bold"),
        bg=BG_COLOR,
        fg=DARK_GREEN
    ).pack(pady=15)

    columns = (
        "Request ID", "Booking ID", "Student", "Venue",
        "Event", "Date", "Status", "Reason"
    )

    table = ttk.Treeview(
        window,
        columns=columns,
        show="headings",
        height=10
    )

    for column in columns:
        table.heading(column, text=column)
        table.column(column, width=110, anchor="center")

    table.column("Request ID", width=80)
    table.column("Booking ID", width=80)
    table.column("Student", width=130)
    table.column("Venue", width=130)
    table.column("Event", width=140)
    table.column("Reason", width=150)

    table.pack(fill="both", expand=True, padx=15, pady=10)

    def refresh_requests():
        """Refresh the list of pending cancellation requests."""

        for item in table.get_children():
            table.delete(item)

        for request in get_all_cancellation_requests():
            if request["status"] == "Pending":
                table.insert(
                    "",
                    "end",
                    values=(
                        request["cancellation_id"],
                        request["booking_id"],
                        request["requested_by"],
                        request["venue_name"],
                        request["event_name"],
                        request["booking_date"],
                        request["status"],
                        request["reason"] or ""
                    )
                )

    def get_selected_request_id():
        """Return the selected cancellation request ID."""

        selected = table.selection()

        if not selected:
            messagebox.showerror(
                "No Selection",
                "Please select a cancellation request first.",
                parent=window
            )
            return None

        values = table.item(selected[0], "values")
        return int(values[0])

    def approve_selected_request():
        """Approve the selected cancellation request."""

        cancellation_id = get_selected_request_id()

        if cancellation_id is None:
            return

        success, message = approve_cancellation(
            cancellation_id,
            user["user_id"]
        )

        if success:
            messagebox.showinfo(
                "Cancellation Approved",
                message,
                parent=window
            )
            refresh_requests()
        else:
            messagebox.showerror(
                "Approval Failed",
                message,
                parent=window
            )
            refresh_requests()

    def reject_selected_request():
        """Reject the selected cancellation request."""

        cancellation_id = get_selected_request_id()

        if cancellation_id is None:
            return

        reason = reason_entry.get().strip()

        success, message = reject_cancellation(
            cancellation_id,
            user["user_id"],
            reason
        )

        if success:
            messagebox.showinfo(
                "Cancellation Rejected",
                message,
                parent=window
            )
            reason_entry.delete(0, tk.END)
            refresh_requests()
        else:
            messagebox.showerror(
                "Rejection Failed",
                message,
                parent=window
            )
            refresh_requests()

    tk.Label(
        window,
        text="Reason for Rejection (optional)",
        font=("Arial", 10, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(pady=(5, 0))

    reason_entry = tk.Entry(window, font=("Arial", 11), width=50)
    reason_entry.pack(pady=5)

    buttons = tk.Frame(window, bg=BG_COLOR)
    buttons.pack(pady=12)

    tk.Button(
        buttons,
        text="APPROVE CANCELLATION",
        command=approve_selected_request,
        bg=BUTTON_GREEN,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        padx=12,
        pady=8
    ).pack(side="left", padx=10)

    tk.Button(
        buttons,
        text="REJECT CANCELLATION",
        command=reject_selected_request,
        bg="#B83232",
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        padx=12,
        pady=8
    ).pack(side="left", padx=10)

    refresh_requests()

def create_booking_window(parent, user):
    """Display the form for creating a venue booking."""

    from tkinter import ttk

    window = tk.Toplevel(parent)
    window.title("New Venue Booking")
    window.geometry("600x750")
    window.configure(bg=BG_COLOR)
    window.resizable(False, False)

    tk.Label(
        window,
        text="NEW VENUE BOOKING",
        font=("Arial", 20, "bold"),
        bg=BG_COLOR,
        fg=DARK_GREEN
    ).pack(pady=(15, 5))

    tk.Label(
        window,
        text="Complete the details below.",
        font=("Arial", 10),
        bg=BG_COLOR,
        fg=MUTED_GREEN
    ).pack(pady=(0, 10))

    form = tk.Frame(
        window,
        bg=WHITE,
        padx=25,
        pady=15
    )
    form.pack(fill="both", expand=True, padx=25, pady=(0, 15))

    # Event name
    tk.Label(
        form,
        text="Event Name",
        bg=WHITE,
        fg=TEXT_COLOR,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    event_entry = tk.Entry(form, font=("Arial", 11))
    event_entry.pack(fill="x", pady=(4, 10))

    # Venue selection
    tk.Label(
        form,
        text="Select Venue",
        bg=WHITE,
        fg=TEXT_COLOR,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    venues = get_all_venues()
    venue_names = [venue["venue_name"] for venue in venues]
    venue_lookup = {
        venue["venue_name"]: venue["venue_id"]
        for venue in venues
    }

    venue_combo = ttk.Combobox(
        form,
        values=venue_names,
        state="readonly",
        font=("Arial", 10)
    )
    venue_combo.pack(fill="x", pady=(4, 10))

    # Booking date
    tk.Label(
        form,
        text="Booking Date (YYYY-MM-DD)",
        bg=WHITE,
        fg=TEXT_COLOR,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    date_entry = tk.Entry(form, font=("Arial", 11))
    date_entry.pack(fill="x", pady=(4, 10))
    

    # Start time
    tk.Label(
        form,
        text="Start Time (HH:MM, 24-hour format)",
        bg=WHITE,
        fg=TEXT_COLOR,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    start_entry = tk.Entry(form, font=("Arial", 11))
    start_entry.pack(fill="x", pady=(4, 10))

    # End time
    tk.Label(
        form,
        text="End Time (HH:MM, 24-hour format)",
        bg=WHITE,
        fg=TEXT_COLOR,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    end_entry = tk.Entry(form, font=("Arial", 11))
    end_entry.pack(fill="x", pady=(4, 10))

    # Equipment checkboxes
    tk.Label(
        form,
        text="Equipment Required",
        bg=WHITE,
        fg=TEXT_COLOR,
        font=("Arial", 10, "bold")
    ).pack(anchor="w", pady=(2, 4))

    equipment_names = [
        "Microphone",
        "Extension cord",
        "Projector",
        "Speakers",
        "Chairs",
        "Other equipment"
    ]

    equipment_vars = {}

    equipment_frame = tk.Frame(form, bg=WHITE)
    equipment_frame.pack(fill="x")

    for equipment in equipment_names:
        variable = tk.BooleanVar(value=False)
        equipment_vars[equipment] = variable

        tk.Checkbutton(
            equipment_frame,
            text=equipment,
            variable=variable,
            bg=WHITE,
            fg=TEXT_COLOR,
            activebackground=WHITE,
            selectcolor=BG_COLOR,
            font=("Arial", 10)
        ).pack(anchor="w")

    tk.Label(
        form,
        text="Other Equipment Details (if selected)",
        bg=WHITE,
        fg=TEXT_COLOR,
        font=("Arial", 10, "bold")
    ).pack(anchor="w", pady=(5, 0))

    other_entry = tk.Entry(form, font=("Arial", 11))
    other_entry.pack(fill="x", pady=(4, 10))

    def submit_booking():
        """Validate and submit the booking form."""

        event_name = event_entry.get().strip()
        venue_name = venue_combo.get()
        booking_date = date_entry.get().strip()
        start_time = start_entry.get().strip()
        end_time = end_entry.get().strip()

        selected_equipment = [
            name
            for name, variable in equipment_vars.items()
            if variable.get()
        ]

        other_details = other_entry.get().strip()

        if not event_name:
            messagebox.showerror(
                "Missing Event Name",
                "Please enter an event name.",
                parent=window
            )
            return

        elif not venue_name:
            messagebox.showerror(
                "Missing Venue",
                "Please select a venue.",
                parent=window
            )
            return

        elif (
            "Other equipment" in selected_equipment
            and not other_details
        ):
            messagebox.showerror(
                "Missing Equipment Details",
                "Please describe the other equipment required.",
                parent=window
            )
            return

        success, message = create_booking(
            user["user_id"],
            user["role"],
            venue_lookup[venue_name],
            event_name,
            booking_date,
            start_time,
            end_time,
            selected_equipment,
            other_details
        )

        if success:
            messagebox.showinfo(
                "Booking Submitted",
                message,
                parent=window
            )
            window.destroy()
        else:
            messagebox.showerror(
                "Booking Failed",
                message,
                parent=window
            )

    tk.Button(
        form,
        text="SUBMIT BOOKING",
        command=submit_booking,
        bg=BUTTON_GREEN,
        fg=WHITE,
        activebackground=HOVER_GREEN,
        activeforeground=WHITE,
        font=("Arial", 11, "bold"),
        cursor="hand2",
        relief="flat",
        pady=10
    ).pack(fill="x", pady=(5, 0))


def export_bookings_window():
    """Export all booking records to a CSV file."""

    from tkinter import filedialog

    filename = filedialog.asksaveasfilename(
        title="Save Booking Records",
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        initialfile="booking_records.csv"
    )

    if not filename:
        return

    success, message = export_bookings_to_csv(filename)

    if success:
        messagebox.showinfo(
            "Export Successful",
            message
        )
    else:
        messagebox.showerror(
            "Export Failed",
            message
        )


def staff_cancel_booking_window(parent, user):
    """Allow staff to cancel their own confirmed booking."""

    window = tk.Toplevel(parent)
    window.title("Cancel My Confirmed Booking")
    window.geometry("450x280")
    window.configure(bg=BG_COLOR)
    window.resizable(False, False)

    tk.Label(
        window,
        text="CANCEL MY CONFIRMED BOOKING",
        font=("Arial", 16, "bold"),
        bg=BG_COLOR,
        fg=DARK_GREEN,
        wraplength=400
    ).pack(pady=(25, 15))

    tk.Label(
        window,
        text="Enter your approved Booking ID:",
        font=("Arial", 10, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(pady=(5, 5))

    booking_id_entry = tk.Entry(window, font=("Arial", 11))
    booking_id_entry.pack(fill="x", padx=40, pady=5)

    def submit_cancellation():
        booking_id_text = booking_id_entry.get().strip()

        if not booking_id_text.isdigit():
            messagebox.showerror(
                "Invalid Booking ID",
                "Please enter a numeric Booking ID.",
                parent=window
            )
            return

        success, message = cancel_staff_booking(
            int(booking_id_text),
            user["user_id"]
        )

        if success:
            messagebox.showinfo(
                "Booking Cancelled",
                message,
                parent=window
            )
            window.destroy()
        else:
            messagebox.showerror(
                "Cancellation Failed",
                message,
                parent=window
            )

    tk.Button(
        window,
        text="CANCEL BOOKING",
        command=submit_cancellation,
        bg=BUTTON_GREEN,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        cursor="hand2",
        relief="flat",
        pady=9
    ).pack(fill="x", padx=40, pady=15)

    tk.Label(
        window,
        text="Only your own approved bookings can be cancelled directly.",
        font=("Arial", 9),
        bg=BG_COLOR,
        fg=MUTED_GREEN,
        wraplength=390
    ).pack(pady=5)

if __name__ == "__main__":
    create_login_window()
