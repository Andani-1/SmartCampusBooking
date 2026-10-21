import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from database import get_connection


class AdminDashboard:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title(f"Admin – {user.get_username()} – {user.get_campus()}")
        self.root.geometry("800x600")

        tk.Label(root, text=f"Campus Administrator Dashboard: {user.get_campus()}",
                 bg="lightgreen", font=("Arial", 12, "bold")).pack(fill=tk.X, pady=10)

        # --- Section 1: Add Resource ---
        frame_add = tk.LabelFrame(root, text="Add New Resource")
        frame_add.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(frame_add, text="Resource Code (e.g. LAB-01):").grid(row=0, column=0, padx=5, pady=5)
        self.code_entry = tk.Entry(frame_add)
        self.code_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_add, text="Resource Name:").grid(row=0, column=2, padx=5, pady=5)
        self.name_entry = tk.Entry(frame_add)
        self.name_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(frame_add, text="Add Resource", command=self.add_resource, bg="brown", fg="white").grid(row=0, column=4,padx=10)
        # --- Section 2: View Resources ---
        tk.Label(root, text="Resources at this Campus", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)
        self.tree = ttk.Treeview(root, columns=("id", "code", "name"), show="headings", height=8)
        self.tree.heading("id", text="ID")
        self.tree.heading("code", text="Code")
        self.tree.heading("name", text="Name")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.load_resources()

        tk.Button(root, text="Remove Selected Resource", command=self.remove_resource, bg="red", fg="white").pack(
            pady=5)

        tk.Button(root, text="View All Bookings for this Campus", command=self.view_campus_bookings).pack(pady=10)

    def load_resources(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = get_connection()
        campus_row = conn.execute("SELECT id FROM campuses WHERE name=?", (self.user.get_campus(),)).fetchone()

        if not campus_row:

            conn.execute("INSERT INTO campuses (name) VALUES (?)", (self.user.get_campus(),))
            conn.commit()
            campus_row = conn.execute("SELECT id FROM campuses WHERE name=?", (self.user.get_campus(),)).fetchone()

        self.campus_id = campus_row["id"]

        rows = conn.execute("SELECT id, resource_code, name FROM resources WHERE campus_id=?",
                            (self.campus_id,)).fetchall()
        for r in rows:
            self.tree.insert("", "end", values=(r["id"], r["resource_code"], r["name"]))
        conn.close()

    def add_resource(self):
        code = self.code_entry.get().strip().upper()
        name = self.name_entry.get().strip()

        if not code or not name:
            messagebox.showerror("Error", "Both code and name are required.")
            return

        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO resources (resource_code, name, campus_id) VALUES (?, ?, ?)",
                (code, name, self.campus_id)
            )
            conn.commit()
            messagebox.showinfo("Success", f"Resource {code} added.")
            self.code_entry.delete(0, tk.END)
            self.name_entry.delete(0, tk.END)
            self.load_resources()  # Refresh the table
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Duplicate Resource Code detected. Code must be unique.")
        finally:
            conn.close()

    def remove_resource(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a resource to remove.")
            return

        resource_id = self.tree.item(selected[0])["values"][0]

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this resource?")
        if confirm:
            conn = get_connection()
            # First delete any bookings linked to this resource to prevent database errors
            conn.execute("DELETE FROM bookings WHERE resource_id=?", (resource_id,))
            conn.execute("DELETE FROM resources WHERE id=?", (resource_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", "Resource removed.")
            self.load_resources()

    def view_campus_bookings(self):
        win = tk.Toplevel(self.root)
        win.title(f"Bookings - {self.user.get_campus()}")
        win.geometry("700x400")

        tree = ttk.Treeview(win, columns=("date", "start", "duration", "user", "resource"), show="headings")
        tree.heading("date", text="Date")
        tree.heading("start", text="Start")
        tree.heading("duration", text="Mins")
        tree.heading("user", text="Booked By")
        tree.heading("resource", text="Resource")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        conn = get_connection()
        query = """
            SELECT b.booking_date, b.start_time, b.duration_minutes, u.username, r.name
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN resources r ON b.resource_id = r.id
            WHERE r.campus_id = ?
        """
        rows = conn.execute(query, (self.campus_id,)).fetchall()
        conn.close()

        for r in rows:
            tree.insert("", "end",
                        values=(r["booking_date"], r["start_time"], r["duration_minutes"], r["username"], r["name"]))