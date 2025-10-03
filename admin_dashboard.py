import tkinter as tk
from tkinter import messagebox

# Import your modules
import manage_users
import manage_categories
import manage_items
import manage_purchase
import reports

class AdminDashboard:
    def __init__(self, root, user_id, full_name):
        self.root = root
        self.root.title("PharmaCare - Admin Dashboard")
        self.root.geometry("1250x600")
        self.root.resizable(False, False)

        self.primary_color = "#2C3E50"
        self.secondary_color = "#3498DB"
        self.accent_color = "#E74C3C"
        self.bg_color = "#ECF0F1"
        self.white = "#FFFFFF"

        self.user_id = user_id
        self.full_name = full_name

        self.root.configure(bg=self.bg_color)
        self.create_layout()

    def create_layout(self):
        header = tk.Frame(self.root, bg=self.primary_color, height=70)
        header.pack(fill="x")

        tk.Label(
            header,
            text=f"Admin Dashboard - {self.full_name}",
            font=("Arial", 20, "bold"),
            bg=self.primary_color,
            fg=self.white
        ).pack(side="left", padx=20)

        logout_btn = tk.Button(
            header,
            text="Logout",
            font=("Arial", 12, "bold"),
            bg=self.accent_color,
            fg=self.white,
            relief="flat",
            cursor="hand2",
            command=self.logout
        )
        logout_btn.pack(side="right", padx=20, pady=15, ipadx=10, ipady=5)

        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, fill="both", padx=50, pady=20)

        btn_style = {
            "font": ("Arial", 14, "bold"),
            "bg": self.secondary_color,
            "fg": self.white,
            "relief": "flat",
            "cursor": "hand2",
            "activebackground": "#2980B9",
            "activeforeground": self.white,
            "bd": 0,
            "width": 25,
            "height": 3
        }

        # Define buttons: (Label, Command, Row, Column)
        buttons = [
            ("Manage Users", self.open_manage_users, 0, 0),
            ("Manage Categories", self.open_manage_categories, 0, 1),
            ("Manage Items", self.open_manage_items, 1, 0),
            ("Manage Purchases", self.open_manage_purchase, 1, 1),
            ("Reports", self.open_reports, 2, 0)
        ]

        for text, command, row, col in buttons:
            btn = tk.Button(main_frame, text=text, command=command, **btn_style)
            btn.grid(row=row, column=col, padx=20, pady=20)

    # ---------------- Button Commands ----------------
    def open_manage_users(self):
        self.root.destroy()
        root = tk.Tk()
        manage_users.ManageUsers(root)
        root.mainloop()

    def open_manage_categories(self):
        self.root.destroy()
        root = tk.Tk()
        manage_categories.ManageCategories(root)
        root.mainloop()

    def open_manage_items(self):
        self.root.destroy()
        root = tk.Tk()
        manage_items.ManageItems(root)
        root.mainloop()

    def open_manage_purchase(self):
        self.root.destroy()
        root = tk.Tk()
        manage_purchase.ManagePurchase(root)
        root.mainloop()

    def open_reports(self):
        self.root.destroy()
        root = tk.Tk()
        reports.ReportsApp(root)
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
    AdminDashboard(root, 1, "Admin User")
    root.mainloop()
