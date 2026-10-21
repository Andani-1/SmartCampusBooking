import tkinter as tk
from tkinter import messagebox, ttk
from database import get_connection
from booking_rules import validate_booking, CAMPUS_RULES
from datetime import datetime

class LecturerDashboard:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title(f"Lecturer – {user.get_username()} – {user.get_campus()}")
        self.root.geometry("900x600")

        policy = CAMPUS_RULES.get(user.get_campus(), {})
        tk.Label(root, text=f"Campus: {user.get_campus()} | Policy: {policy.get('description', '')}",
                 bg="grey").pack(fill=tk.X, pady=5)

        tk.Label(root, text="Available Resources").pack(anchor="w", padx=10)
        self.tree = ttk.Treeview(root, columns=("id", "code", "name"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("code", text="Code")
        self.tree.heading("name", text="Name")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.load_resources()

        frame = tk.Frame(root)
        frame.pack(pady=10)

        tk.Label(frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0)
        self.date_entry = tk.Entry(frame)
        self.date_entry.grid(row=0, column=1)

        tk.Label(frame, text="Start Hour (0–23):").grid(row=0, column=2)
        self.hour_entry = tk.Entry(frame)
        self.hour_entry.grid(row=0, column=3)

        tk.Label(frame, text="Duration (min):").grid(row=0, column=4)
        self.duration_entry = tk.Entry(frame)
        self.duration_entry.grid(row=0, column=5)

        tk.Button(frame, text="Book Selected Resource", command=self.make_booking).grid(row=0, column=6, padx=10)
        tk.Button(root, text="View My Bookings", command=self.view_bookings).pack(pady=5)

    def load_resources(self):
        conn = get_connection()

        campus_row = conn.execute("SELECT id FROM campuses WHERE name=?", (self.user.get_campus(),)).fetchone()
        if campus_row:
            rows = conn.execute(
                "SELECT id, resource_code, name FROM resources WHERE campus_id=?",
                (campus_row["id"],)
            ).fetchall()
            for r in rows:
                self.tree.insert("", "end", values=(r["id"], r["resource_code"], r["name"]))
        conn.close()

    def make_booking(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a resource first.")
            return

        resource_id = self.tree.item(selected[0])["values"][0]

        try:
            date_str = self.date_entry.get().strip()
            start_hour = int(self.hour_entry.get().strip())
            duration = int(self.duration_entry.get().strip())
            datetime.strptime(date_str, "%Y-%m-%d")  # validate format
        except ValueError:
            messagebox.showerror("Error", "Enter a valid date (YYYY-MM-DD) and numbers for hour/duration.")
            return

        valid, msg = validate_booking(self.user.get_campus(), start_hour, duration)
        if not valid:
            messagebox.showerror("Booking rule violation", msg)
            return

        conn = get_connection()
        end_hour = start_hour + duration / 60
        existing = conn.execute(
            "SELECT start_time, duration_minutes FROM bookings WHERE resource_id=? AND booking_date=? AND status='active'",
            (resource_id, date_str)
        ).fetchall()

        for row in existing:
            ex_start = int(row["start_time"].split(":")[0])
            ex_end = ex_start + row["duration_minutes"] / 60
            if start_hour < ex_end and end_hour > ex_start:
                conn.close()
                messagebox.showerror("Conflict", "This resource is already booked during that time.")
                return

        conn.execute(
            "INSERT INTO bookings (resource_id, user_id, booking_date, start_time, duration_minutes) VALUES (?,?,?,?,?)",
            (resource_id, self.user.get_id(), date_str, f"{start_hour:02d}:00", duration)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Booking created.")

    def view_bookings(self):
        win = tk.Toplevel(self.root)
        win.title("My Bookings")
        tree = ttk.Treeview(win, columns=("id", "date", "start", "duration", "status"), show="headings")
        for col in ("id", "date", "start", "duration", "status"):
            tree.heading(col, text=col.capitalize())
        tree.pack(fill=tk.BOTH, expand=True)

        conn = get_connection()
        rows = conn.execute(
            "SELECT id, booking_date, start_time, duration_minutes, status FROM bookings WHERE user_id=?",
            (self.user.get_id(),)
        ).fetchall()
        conn.close()

        for r in rows:
            tree.insert("", "end",
                        values=(r["id"], r["booking_date"], r["start_time"], r["duration_minutes"], r["status"]))