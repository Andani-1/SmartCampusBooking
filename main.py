import tkinter as tk
from database import initialise_database
from gui.login import LoginWindow
from gui.lecturer_view import LecturerDashboard
from gui.admin_view import AdminDashboard
from gui.operator_view import OperatorDashboard

def launch_dashboard(user):
    root = tk.Tk()
    role = user.get_role()

    if role == "lecturer":
        LecturerDashboard(root, user)
    elif role == "admin":
        AdminDashboard(root, user)
    elif role == "operator":
        OperatorDashboard(root, user)

    root.mainloop()

if __name__ == "__main__":
    initialise_database()
    root = tk.Tk()
    LoginWindow(root, launch_dashboard)
    root.mainloop()
