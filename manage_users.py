import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import admin_dashboard
from user_form import UserForm

class ManageUsers:
    def __init__(self, root):
        self.root = root
        self.root.title("Manage Users - PharmaCare")
        self.root.geometry("1250x600")
        self.root.resizable(False, False)

        self.primary_color = "#2C3E50"
        self.secondary_color = "#3498DB"
        self.accent_color = "#E74C3C"
        self.bg_color = "#ECF0F1"
        self.white = "#FFFFFF"

        self.root.configure(bg=self.bg_color)
        self.create_layout()
        self.load_users()

    def create_layout(self):
        header = tk.Frame(self.root, bg=self.primary_color, height=70)
        header.pack(fill="x")

        tk.Label(
            header,
            text="Manage Users",
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

        search_frame = tk.Frame(self.root, bg=self.bg_color)
        search_frame.pack(fill="x", padx=20, pady=(10, 0))

        tk.Label(search_frame, text="Search (ID or Name):", font=("Arial", 12), bg=self.bg_color).pack(side="left", padx=5)

        self.search_entry = tk.Entry(search_frame, font=("Arial", 12), width=40)
        self.search_entry.pack(side="left", padx=5)

        tk.Button(
            search_frame,
            text="Search",
            bg=self.secondary_color,
            fg=self.white,
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.search_user
        ).pack(side="left", padx=5)

        tk.Button(
            search_frame,
            text="Show All",
            bg=self.secondary_color,
            fg=self.white,
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.load_users
        ).pack(side="left", padx=5)

        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        columns = ("id", "username", "full_name", "role", "email", "phone")
        self.user_table = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.user_table.heading(col, text=col.capitalize())
            self.user_table.column(col, width=150)

        self.user_table.pack(fill="both", expand=True)

        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(fill="x", padx=20, pady=10)

        tk.Button(
            btn_frame,
            text="Add User",
            bg=self.secondary_color,
            fg=self.white,
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.open_add_form
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Edit User",
            bg=self.secondary_color,
            fg=self.white,
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.open_edit_form
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Delete User",
            bg=self.accent_color,
            fg=self.white,
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.delete_user
        ).pack(side="left", padx=5)

    def db_connection(self):
        return sqlite3.connect("pharmacare.db")

    def load_users(self):
        conn = self.db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, full_name, role, email, phone FROM users")
        rows = cursor.fetchall()
        conn.close()

        self.user_table.delete(*self.user_table.get_children())
        for row in rows:
            self.user_table.insert("", "end", values=row)

    def search_user(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_users()
            return

        conn = self.db_connection()
        cursor = conn.cursor()

        if keyword.isdigit():
            cursor.execute("""
                SELECT user_id, username, full_name, role, email, phone
                FROM users WHERE user_id = ?
            """, (keyword,))
        else:
            cursor.execute("""
                SELECT user_id, username, full_name, role, email, phone
                FROM users WHERE full_name LIKE ? OR username LIKE ?
            """, (f"%{keyword}%", f"%{keyword}%"))

        rows = cursor.fetchall()
        conn.close()

        self.user_table.delete(*self.user_table.get_children())
        for row in rows:
            self.user_table.insert("", "end", values=row)

    def open_add_form(self):
        self.root.destroy()
        root = tk.Tk()
        UserForm(root, mode="add")
        root.mainloop()

    def open_edit_form(self):
        selected = self.user_table.selection()
        if not selected:
            messagebox.showerror("Error", "Select a user to edit")
            return

        user_data = self.user_table.item(selected[0])["values"]
        self.root.destroy()
        root = tk.Tk()
        UserForm(root, mode="edit", user_data=user_data)
        root.mainloop()

    def delete_user(self):
        selected = self.user_table.selection()
        if not selected:
            messagebox.showerror("Error", "Select a user to delete")
            return

        user_id = self.user_table.item(selected[0])["values"][0]
        confirm = messagebox.askyesno("Confirm", "Are you sure to delete this user?")
        if not confirm:
            return

        conn = self.db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Deleted", "User deleted successfully")
        self.load_users()

    def go_back(self):
        self.root.destroy()
        root = tk.Tk()
        admin_dashboard.AdminDashboard(root, 1, "Admin User")
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    ManageUsers(root)
    root.mainloop()
