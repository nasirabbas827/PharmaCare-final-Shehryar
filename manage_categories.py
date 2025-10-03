import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from category_form import CategoryForm

class ManageCategories:
    def __init__(self, root):
        self.root = root
        self.root.title("Manage Categories")
        self.root.geometry("1250x600")  
        self.root.configure(bg="#ECF0F1")
        self.center_window(1250, 600)   


        self.primary_color = "#2C3E50"
        self.secondary_color = "#3498DB"
        self.accent_color = "#E74C3C"
        self.white = "#FFFFFF"

        self.create_widgets()
        self.load_categories()

    def center_window(self, width, height):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        title_frame = tk.Frame(self.root, bg=self.primary_color, pady=10)
        title_frame.pack(fill="x")

        tk.Label(
            title_frame,
            text="Manage Categories",
            font=("Arial", 20, "bold"),
            bg=self.primary_color,
            fg=self.white
        ).pack()

        search_frame = tk.Frame(self.root, bg="#ECF0F1", pady=10)
        search_frame.pack(fill="x", padx=20)

        tk.Label(
            search_frame,
            text="Search:",
            font=("Arial", 12, "bold"),
            bg="#ECF0F1",
            fg=self.primary_color
        ).pack(side="left")

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 12),
            bg="#F8F9FA",
            fg=self.primary_color,
            relief="flat"
        )
        search_entry.pack(side="left", padx=10, fill="x", expand=True)

        search_btn = tk.Button(
            search_frame,
            text="Search",
            font=("Arial", 12, "bold"),
            bg=self.secondary_color,
            fg=self.white,
            relief="flat",
            command=self.search_categories
        )
        search_btn.pack(side="left", padx=10)

        add_btn = tk.Button(
            search_frame,
            text="Add Category",
            font=("Arial", 12, "bold"),
            bg=self.secondary_color,
            fg=self.white,
            relief="flat",
            command=self.open_add_form
        )
        add_btn.pack(side="right")

        columns = ("#1", "#2")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.heading("#1", text="ID")
        self.tree.heading("#2", text="Category Name")

        self.tree.column("#1", width=50)
        self.tree.column("#2", width=300)

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        action_frame = tk.Frame(self.root, bg="#ECF0F1", pady=10)
        action_frame.pack(fill="x", padx=20)

        edit_btn = tk.Button(
            action_frame,
            text="Edit",
            font=("Arial", 12, "bold"),
            bg=self.secondary_color,
            fg=self.white,
            relief="flat",
            command=self.edit_category
        )
        edit_btn.pack(side="left", padx=10)

        delete_btn = tk.Button(
            action_frame,
            text="Delete",
            font=("Arial", 12, "bold"),
            bg=self.accent_color,
            fg=self.white,
            relief="flat",
            command=self.delete_category
        )
        delete_btn.pack(side="left", padx=10)

        back_btn = tk.Button(
            action_frame,
            text="Back",
            font=("Arial", 12, "bold"),
            bg=self.primary_color,
            fg=self.white,
            relief="flat",
            command=self.go_back
        )
        back_btn.pack(side="right")

    def load_categories(self):
        conn = sqlite3.connect('pharmacare.db')
        cursor = conn.cursor()
        cursor.execute("SELECT category_id, category_name FROM categories")
        rows = cursor.fetchall()
        conn.close()

        for i in self.tree.get_children():
            self.tree.delete(i)

        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def search_categories(self):
        search_text = self.search_var.get().strip()
        conn = sqlite3.connect('pharmacare.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category_id, category_name
            FROM categories
            WHERE category_name LIKE ?
        """, (f'%{search_text}%',))
        rows = cursor.fetchall()
        conn.close()

        for i in self.tree.get_children():
            self.tree.delete(i)

        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def open_add_form(self):
        form_window = tk.Toplevel(self.root)
        CategoryForm(form_window, refresh_callback=self.load_categories)

    def edit_category(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a category to edit!")
            return

        values = self.tree.item(selected[0], "values")
        category_id, category_name = values

        form_window = tk.Toplevel(self.root)
        CategoryForm(
            form_window,
            refresh_callback=self.load_categories,
            category_data=(category_id, category_name)
        )

    def delete_category(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a category to delete!")
            return

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this category?")
        if not confirm:
            return

        values = self.tree.item(selected[0], "values")
        category_id = values[0]

        conn = sqlite3.connect('pharmacare.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE category_id = ?", (category_id,))
        conn.commit()
        conn.close()

        self.load_categories()
        messagebox.showinfo("Success", "Category deleted successfully!")

    def go_back(self):
        self.root.destroy()
        import admin_dashboard
        root = tk.Tk()
        admin_dashboard.AdminDashboard(root, None, None)
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    ManageCategories(root)
    root.mainloop()
