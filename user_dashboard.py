import tkinter as tk
from tkinter import messagebox
import manage_sales  # Ensure this file exists with ManageSales class

class UserDashboard:
    def __init__(self, root, user_id, full_name):
        self.root = root
        self.user_id = user_id
        self.full_name = full_name
        self.root.title("PharmaCare Management System - User Dashboard")
        self.root.geometry("1250x600")
        self.root.resizable(False, False)

        # Colors
        self.primary_color = "#2C3E50"
        self.secondary_color = "#3498DB"
        self.accent_color = "#E74C3C"
        self.bg_color = "#ECF0F1"
        self.white = "#FFFFFF"

        self.root.configure(bg=self.bg_color)

        # Center window
        self.center_window()

        self.create_widgets()

    def center_window(self):
        self.root.update_idletasks()
        width = 1250
        height = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Main content frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, fill="both")

        # Welcome message
        tk.Label(
            main_frame,
            text=f"Welcome, {self.full_name}",
            font=("Arial", 24, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        ).pack(pady=(50, 30))

        tk.Label(
            main_frame,
            text="Access your pharmacy services below:",
            font=("Arial", 14),
            bg=self.bg_color,
            fg="#7F8C8D"
        ).pack(pady=(0, 40))

        # Buttons frame
        btn_frame = tk.Frame(main_frame, bg=self.bg_color)
        btn_frame.pack()

        btn_style = {
            "font": ("Arial", 14, "bold"),
            "fg": self.white,
            "relief": "flat",
            "cursor": "hand2",
            "activebackground": "#2980B9",
            "activeforeground": self.white,
            "width": 25,
            "height": 2,
            "bd": 0
        }

        # Manage Sales button
        sales_style = btn_style.copy()
        sales_style["bg"] = self.secondary_color
        tk.Button(btn_frame, text="Manage Sales", command=self.open_manage_sales, **sales_style).pack(pady=15)

        # Logout button
        logout_style = btn_style.copy()
        logout_style["bg"] = self.accent_color
        tk.Button(btn_frame, text="Logout", command=self.logout, **logout_style).pack(pady=15)

    def open_manage_sales(self):
        self.root.destroy()
        root = tk.Tk()
        manage_sales.ManageSales(root, admin_id=self.user_id, admin_name=self.full_name)
        root.mainloop()

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            from app import PharmaCareLogin  # Correct import
            root = tk.Tk()
            PharmaCareLogin(root)
            root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = UserDashboard(root, 1, "Regular User")
    root.mainloop()
