import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class UserForm:
    def __init__(self, root, mode="add", user_data=None, admin_id=None, admin_name="Admin User"):
        self.root = root
        self.mode = mode
        self.user_data = user_data
        self.admin_id = admin_id
        self.admin_name = admin_name

        self.root.title("User Form - PharmaCare")
        self.root.geometry("1250x600")
        self.root.resizable(False, False)
        self.center_window(1250, 600)

        # Colors
        self.primary_color = "#2C3E50"
        self.secondary_color = "#3498DB"
        self.accent_color = "#E74C3C"
        self.bg_color = "#ECF0F1"
        self.white = "#FFFFFF"

        self.root.configure(bg=self.bg_color)
        self.create_layout()

        if self.mode == "edit" and self.user_data:
            self.fill_form()

    def center_window(self, width, height):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def db_connection(self):
        return sqlite3.connect("pharmacare.db")

    def create_layout(self):
        # Header
        header = tk.Frame(self.root, bg=self.primary_color, height=70)
        header.pack(fill="x")
        title_text = "Add New User" if self.mode == "add" else f"Edit User (ID: {self.user_data[0] if self.user_data else ''})"
        tk.Label(
            header,
            text=title_text,
            font=("Arial", 20, "bold"),
            bg=self.primary_color,
            fg=self.white
        ).pack(side="left", padx=20)

        back_btn = tk.Button(
            header,
            text="Back",
            font=("Arial", 12, "bold"),
            bg=self.accent_color,
            fg=self.white,
            relief="flat",
            cursor="hand2",
            command=self.go_back
        )
        back_btn.pack(side="right", padx=20, pady=15, ipadx=10, ipady=5)

        # Form Frame
        form_frame = tk.Frame(self.root, bg=self.white)
        form_frame.pack(padx=20, pady=12, fill="both", expand=True)

        # Left and Right Columns
        left_col = tk.Frame(form_frame, bg=self.white)
        left_col.pack(side="left", fill="both", expand=True, padx=(10,5), pady=10)

        right_col = tk.Frame(form_frame, bg=self.white)
        right_col.pack(side="right", fill="both", expand=True, padx=(5,10), pady=10)

        lbl_cfg = {"font": ("Arial", 12, "bold"), "bg": self.white, "anchor": "w"}
        entry_cfg = {"font": ("Arial", 12), "bg": "#F8F9FA", "relief": "flat"}

        # Fields split across two columns
        left_fields = ["Full Name", "Username", "Password"]
        right_fields = ["Role", "Email", "Phone"]
        self.entries = {}

        for label in left_fields:
            tk.Label(left_col, text=label, **lbl_cfg).pack(fill="x", pady=(4,0))
            entry = tk.Entry(left_col, **entry_cfg, show="*" if label=="Password" else "")
            entry.pack(fill="x", pady=4, ipady=6)
            self.entries[label.lower().replace(" ", "_")] = entry

        for label in right_fields:
            tk.Label(right_col, text=label, **lbl_cfg).pack(fill="x", pady=(4,0))
            entry = tk.Entry(right_col, **entry_cfg)
            entry.pack(fill="x", pady=4, ipady=6)
            self.entries[label.lower().replace(" ", "_")] = entry

        # Action Buttons
        action_frame = tk.Frame(self.root, bg=self.bg_color)
        action_frame.pack(fill="x", padx=20, pady=(6, 20))

        btn_text = "Save User" if self.mode == "add" else "Update User"
        tk.Button(
            action_frame,
            text=btn_text,
            font=("Arial", 12, "bold"),
            bg=self.secondary_color,
            fg=self.white,
            relief="flat",
            cursor="hand2",
            command=self.save_user
        ).pack(side="left", padx=6, ipadx=10, ipady=5)



    def fill_form(self):
        user_id, username, full_name, role, email, phone = self.user_data
        self.entries["full_name"].insert(0, full_name)
        self.entries["username"].insert(0, username)
        self.entries["password"].insert(0, "")  # Password not fetched
        self.entries["role"].insert(0, role)
        self.entries["email"].insert(0, email if email else "")
        self.entries["phone"].insert(0, phone if phone else "")

    def save_user(self):
        data = {k: v.get().strip() for k, v in self.entries.items()}

        if not data["full_name"] or not data["username"] or not data["role"]:
            messagebox.showerror("Error", "Full Name, Username, and Role are required")
            return

        conn = self.db_connection()
        cursor = conn.cursor()

        try:
            if self.mode == "add":
                cursor.execute("""
                    INSERT INTO users (username, password, full_name, role, email, phone)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    data["username"],
                    data["password"] if data["password"] else "",
                    data["full_name"],
                    data["role"],
                    data["email"],
                    data["phone"]
                ))
                conn.commit()
                messagebox.showinfo("Success", "User created successfully")
            else:
                user_id = self.user_data[0]
                cursor.execute("""
                    UPDATE users
                    SET username = ?, full_name = ?, role = ?, email = ?, phone = ?
                    WHERE user_id = ?
                """, (
                    data["username"],
                    data["full_name"],
                    data["role"],
                    data["email"],
                    data["phone"],
                    user_id
                ))
                conn.commit()
                messagebox.showinfo("Success", "User updated successfully")

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username or Email already exists")
        finally:
            conn.close()
            self.close_form()

    def go_back(self):
        # try open admin_dashboard if available, otherwise just close
        try:
            import admin_dashboard
            self.root.destroy()
            root = tk.Tk()
            admin_dashboard.AdminDashboard(root, self.admin_id, self.admin_name)
            root.mainloop()
        except Exception:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    UserForm(root, mode="add")
    root.mainloop()
