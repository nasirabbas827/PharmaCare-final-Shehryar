import os
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from item_form import ItemForm

class ManageItems:
    def __init__(self, root, admin_id=None, admin_name="Admin User"):
        self.root = root
        self.root.title("Manage Items - PharmaCare")
        self.root.geometry("1250x600")
        self.root.resizable(False, False)
        self.center_window(1250, 600)

        # Theme (same as login)
        self.primary_color = "#2C3E50"
        self.secondary_color = "#3498DB"
        self.accent_color = "#E74C3C"
        self.bg_color = "#ECF0F1"
        self.white = "#FFFFFF"

        self.admin_id = admin_id
        self.admin_name = admin_name

        self.root.configure(bg=self.bg_color)
        self.create_layout()
        self.load_items()

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
        tk.Label(
            header,
            text="Manage Items",
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

        # Search area
        search_frame = tk.Frame(self.root, bg=self.bg_color)
        search_frame.pack(fill="x", padx=20, pady=(12, 0))

        tk.Label(search_frame, text="Search (ID or Name):", font=("Arial", 12), bg=self.bg_color).pack(side="left", padx=(0,8))
        self.search_entry = tk.Entry(search_frame, font=("Arial", 12), width=40)
        self.search_entry.pack(side="left", padx=(0,8))
        self.search_entry.bind("<Return>", lambda e: self.search_items())

        tk.Button(
            search_frame,
            text="Search",
            bg=self.secondary_color,
            fg=self.white,
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.search_items
        ).pack(side="left", padx=6)

        tk.Button(
            search_frame,
            text="Show All",
            bg=self.secondary_color,
            fg=self.white,
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.load_items
        ).pack(side="left", padx=6)

        # Table frame
        table_frame = tk.Frame(self.root, bg=self.white)
        table_frame.pack(fill="both", expand=True, padx=20, pady=12)

        columns = ("item_id", "item_name", "category", "purchase_price", "sale_price", "stock", "expiry_date", "created_date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        headings = {
            "item_id": "ID",
            "item_name": "Name",
            "category": "Category",
            "purchase_price": "Purchase Price",
            "sale_price": "Sale Price",
            "stock": "Stock",
            "expiry_date": "Expiry",
            "created_date": "Created"
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            # width tuning
            if col in ("item_name", "category"):
                self.tree.column(col, width=180)
            elif col in ("purchase_price", "sale_price"):
                self.tree.column(col, width=110, anchor="e")
            elif col in ("created_date", "expiry_date"):
                self.tree.column(col, width=130)
            else:
                self.tree.column(col, width=80)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Buttons
        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(fill="x", padx=20, pady=(6,20))

        tk.Button(
            btn_frame,
            text="Add Item",
            bg=self.secondary_color,
            fg=self.white,
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.open_add_form
        ).pack(side="left", padx=6)

        tk.Button(
            btn_frame,
            text="Edit Item",
            bg=self.secondary_color,
            fg=self.white,
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.open_edit_form
        ).pack(side="left", padx=6)

        tk.Button(
            btn_frame,
            text="Delete Item",
            bg=self.accent_color,
            fg=self.white,
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.delete_item
        ).pack(side="left", padx=6)

    def load_items(self):
        conn = self.db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.item_id, m.item_name, c.category_name, m.purchase_price, m.sale_price, 
                   m.stock, m.expiry_date, m.created_date
            FROM medical_items m
            LEFT JOIN categories c ON m.category_id = c.category_id
            ORDER BY m.item_id DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        for r in rows:
            # normalize None expiry
            expiry = r[6] if r[6] is not None else ""
            created = r[7] if r[7] is not None else ""
            self.tree.insert("", "end", values=(r[0], r[1], r[2] or "", r[3], r[4], r[5] or 0, expiry, created))

    def search_items(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_items()
            return

        conn = self.db_connection()
        cursor = conn.cursor()
        if keyword.isdigit():
            cursor.execute("""
                SELECT m.item_id, m.item_name, c.category_name, m.purchase_price, m.sale_price, 
                       m.stock, m.expiry_date, m.created_date
                FROM medical_items m
                LEFT JOIN categories c ON m.category_id = c.category_id
                WHERE m.item_id = ?
            """, (int(keyword),))
        else:
            like = f"%{keyword}%"
            cursor.execute("""
                SELECT m.item_id, m.item_name, c.category_name, m.purchase_price, m.sale_price, 
                       m.stock, m.expiry_date, m.created_date
                FROM medical_items m
                LEFT JOIN categories c ON m.category_id = c.category_id
                WHERE m.item_name LIKE ?
            """, (like,))
        rows = cursor.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        for r in rows:
            expiry = r[6] if r[6] is not None else ""
            created = r[7] if r[7] is not None else ""
            self.tree.insert("", "end", values=(r[0], r[1], r[2] or "", r[3], r[4], r[5] or 0, expiry, created))

    def get_selected_item_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"][0]

    def open_add_form(self):
        # destroy current and open form in add mode
        self.root.destroy()
        root = tk.Tk()
        ItemForm(root, mode="add")
        root.mainloop()

    def open_edit_form(self):
        item_id = self.get_selected_item_id()
        if not item_id:
            messagebox.showerror("Error", "Select an item to edit.")
            return

        # fetch full item data
        conn = self.db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT item_id, image, item_name, category_id, description, manufacturer, 
                   purchase_price, sale_price, stock, expiry_date
            FROM medical_items WHERE item_id = ?
        """, (item_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            messagebox.showerror("Error", "Item not found.")
            return

        self.root.destroy()
        root = tk.Tk()
        ItemForm(root, mode="edit", item_data=row)
        root.mainloop()

    def delete_item(self):
        item_id = self.get_selected_item_id()
        if not item_id:
            messagebox.showerror("Error", "Select an item to delete.")
            return

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this item?")
        if not confirm:
            return

        # optionally delete image file stored in images/
        try:
            conn = self.db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT image FROM medical_items WHERE item_id = ?", (item_id,))
            img_row = cursor.fetchone()
            if img_row and img_row[0]:
                img_path = img_row[0]
                try:
                    if os.path.exists(img_path):
                        os.remove(img_path)
                except Exception:
                    pass

            cursor.execute("DELETE FROM medical_items WHERE item_id = ?", (item_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", "Item deleted successfully.")
            self.load_items()
        except sqlite3.Error as e:
            messagebox.showerror("DB Error", f"An error occurred: {e}")

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
    ManageItems(root)
    root.mainloop()
