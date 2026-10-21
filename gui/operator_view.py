import tkinter as tk
from tkinter import ttk
from database import get_connection


class OperatorDashboard:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title(f"System Operator – {user.get_username()}")
        self.root.geometry("1000x600")

        tk.Label(root, text=f"System Operator Dashboard",
                 bg="lightblue", font=("Arial", 12, "bold")).pack(fill=tk.X, pady=10)

        tk.Label(root, text="All Bookings Across All Campuses", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)

        self.tree = ttk.Treeview(root, columns=("campus", "date", "start", "duration", "user", "resource"),
                                 show="headings")
        self.tree.heading("campus", text="Campus")
        self.tree.heading("date", text="Date")
        self.tree.heading("start", text="Start")
        self.tree.heading("duration", text="Mins")
        self.tree.heading("user", text="Booked By")
        self.tree.heading("resource", text="Resource")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.load_all_bookings()

        frame_reports = tk.LabelFrame(root, text="Generate Reports")
        frame_reports.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(frame_reports, text="Most Used Resources (by Campus)", command=self.report_most_used).pack(
            side=tk.LEFT, padx=10, pady=10)
        tk.Button(frame_reports, text="Average Booking Duration (by Campus)", command=self.report_avg_duration).pack(
            side=tk.LEFT, padx=10, pady=10)

    def load_all_bookings(self):
        conn = get_connection()
        query = """
            SELECT c.name as campus_name, b.booking_date, b.start_time, b.duration_minutes, 
                   u.username, r.name as resource_name
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN resources r ON b.resource_id = r.id
            JOIN campuses c ON r.campus_id = c.id
            ORDER BY b.booking_date DESC
        """
        rows = conn.execute(query).fetchall()
        conn.close()

        for r in rows:
            self.tree.insert("", "end", values=(r["campus_name"], r["booking_date"], r["start_time"],
                                                r["duration_minutes"], r["username"], r["resource_name"]))

    def report_most_used(self):
        win = tk.Toplevel(self.root)
        win.title("Report: Most Used Resources")
        win.geometry("500x400")

        tree = ttk.Treeview(win, columns=("campus", "resource", "count"), show="headings")
        tree.heading("campus", text="Campus")
        tree.heading("resource", text="Resource")
        tree.heading("count", text="Total Bookings")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        conn = get_connection()
        query = """
            SELECT c.name as campus, r.name as resource, COUNT(b.id) as total
            FROM bookings b
            JOIN resources r ON b.resource_id = r.id
            JOIN campuses c ON r.campus_id = c.id
            GROUP BY r.id
            ORDER BY total DESC
        """
        rows = conn.execute(query).fetchall()
        conn.close()

        for r in rows:
            tree.insert("", "end", values=(r["campus"], r["resource"], r["total"]))

    def report_avg_duration(self):
        win = tk.Toplevel(self.root)
        win.title("Report: Average Booking Duration")
        win.geometry("500x400")

        tree = ttk.Treeview(win, columns=("campus", "avg_duration"), show="headings")
        tree.heading("campus", text="Campus")
        tree.heading("avg_duration", text="Average Duration (Mins)")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        conn = get_connection()
        query = """
            SELECT c.name as campus, AVG(b.duration_minutes) as avg_duration
            FROM bookings b
            JOIN resources r ON b.resource_id = r.id
            JOIN campuses c ON r.campus_id = c.id
            GROUP BY c.id
        """
        rows = conn.execute(query).fetchall()
        conn.close()

        for r in rows:
            avg = round(r["avg_duration"], 1) if r["avg_duration"] else 0
            tree.insert("", "end", values=(r["campus"], f"{avg} mins"))