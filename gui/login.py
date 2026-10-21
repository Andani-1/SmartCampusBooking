import tkinter as tk
from tkinter import messagebox
import sqlite3  # Needed to catch duplicate usernames
from database import get_connection
from models import Lecturer, CampusAdmin, SystemOperator


class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.root.title("Smart Campus")
        self.root.geometry("400x350")

        tk.Label(root, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        tk.Label(root, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        tk.Label(root, text="Role").pack(pady=5)
        self.role_var = tk.StringVar(value="Lecturer")
        tk.OptionMenu(root, self.role_var, "Lecturer", "Admin", "Operator").pack()

        tk.Label(root, text="Campus").pack(pady=5)
        self.campus_var = tk.StringVar(value="Johannesburg")
        tk.OptionMenu(root, self.campus_var, "Johannesburg", "Cape Town", "Durban").pack()

        tk.Button(root, text="Login", command=self.login, bg="blue", fg="white").pack(pady=10)
        tk.Button(root, text="Register", command=self.register, bg="blue", fg="white").pack()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Username and password required.")
            return

        conn = get_connection()
        user_row = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if not user_row:
            messagebox.showerror("Login failed", "Invalid credentials.")
            return

        role = user_row["role"]
        if role == "Lecturer":
            user = Lecturer(user_row["id"], user_row["username"], user_row["campus"])
        elif role == "Admin":
            user = CampusAdmin(user_row["id"], user_row["username"], user_row["campus"])
        else:
            user = SystemOperator(user_row["id"], user_row["username"])

        self.root.destroy()
        self.on_success(user)

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()
        campus = self.campus_var.get() if role in ("Lecturer", "Admin") else None

        if not username or not password:
            messagebox.showerror("Error", "Fill in all the fields.")
            return

        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO users (username, password, role, campus) VALUES (?,?,?,?)",
                (username, password, role, campus)
            )
            conn.commit()
            messagebox.showinfo("Success", "Account created. Log in.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        finally:
            conn.close()