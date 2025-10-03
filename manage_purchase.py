import os
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class ManagePurchase:
    def __init__(self, root, admin_id=None, admin_name="Admin User"):
        self.root = root
        self.root.title("Purchases - PharmaCare")
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

        # cart will be list of dicts: {item_id, item_name, qty, purchase_price, subtotal}
        self.cart = []

        self.root.configure(bg=self.bg_color)
        self.create_layout()
        self.load_all_items()

    def center_window(self, width, height):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def db_connection(self):
        return sqlite3.connect("pharmacare.db")

    def create_layout(self):
        header = tk.Frame(self.root, bg=self.primary_color, height=70)
        header.pack(fill="x")
        tk.Label(header,
                 text="Purchases - PharmaCare",
                 font=("Arial", 20, "bold"),
                 bg=self.primary_color,
                 fg=self.white).pack(side="left", padx=20)

        back_btn = tk.Button(header,
                             text="Back",
                             font=("Arial", 12, "bold"),
                             bg=self.accent_color,
                             fg=self.white,
                             relief="flat",
                             cursor="hand2",
                             command=self.go_back)
        back_btn.pack(side="right", padx=20, pady=15, ipadx=10, ipady=5)

        # Top: Search and selected item info
        top_frame = tk.Frame(self.root, bg=self.bg_color)
        top_frame.pack(fill="x", padx=20, pady=(12, 0))

        tk.Label(top_frame, text="Search Item (ID or name):", font=("Arial", 12), bg=self.bg_color).pack(side="left")
        self.search_entry = tk.Entry(top_frame, font=("Arial", 12), width=40)
        self.search_entry.pack(side="left", padx=8)
        self.search_entry.bind("<Return>", lambda e: self.search_items())

        tk.Button(top_frame, text="Search", bg=self.secondary_color, fg=self.white, font=("Arial", 12, "bold"),
                  relief="flat", cursor="hand2", command=self.search_items).pack(side="left", padx=6)

        tk.Button(top_frame, text="Show All", bg=self.secondary_color, fg=self.white, font=("Arial", 12, "bold"),
                  relief="flat", cursor="hand2", command=self.load_all_items).pack(side="left", padx=6)

        # Middle: left -> item results, right -> cart
        middle_frame = tk.Frame(self.root, bg=self.bg_color)
        middle_frame.pack(fill="both", expand=True, padx=20, pady=12)

        # Left: item list and add controls
        left_frame = tk.Frame(middle_frame, bg=self.white)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0,10))

        tk.Label(left_frame, text="Available Items", font=("Arial", 14, "bold"), bg=self.white,
                 fg=self.primary_color).pack(anchor="w", padx=10, pady=(10,0))

        self.items_columns = ("item_id", "item_name", "purchase_price", "stock", "expiry_date")
        self.items_tree = ttk.Treeview(left_frame, columns=self.items_columns, show="headings", selectmode="browse", height=10)
        headings = {
            "item_id": "ID",
            "item_name": "Name",
            "purchase_price": "Purchase Price",
            "stock": "Stock",
            "expiry_date": "Expiry"
        }
        for col in self.items_columns:
            self.items_tree.heading(col, text=headings[col])
            if col == "item_name":
                self.items_tree.column(col, width=220)
            else:
                self.items_tree.column(col, width=90)
        self.items_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Item add area
        add_frame = tk.Frame(left_frame, bg=self.white)
        add_frame.pack(fill="x", padx=10, pady=(0,12))

        tk.Label(add_frame, text="Selected Item ID:", bg=self.white).grid(row=0, column=0, sticky="w")
        self.selected_item_var = tk.StringVar()
        tk.Entry(add_frame, textvariable=self.selected_item_var, state="readonly", width=10).grid(row=0, column=1, sticky="w", padx=6)

        tk.Label(add_frame, text="Qty:", bg=self.white).grid(row=0, column=2, sticky="w", padx=(10,0))
        self.qty_var = tk.StringVar(value="1")
        tk.Entry(add_frame, textvariable=self.qty_var, width=6).grid(row=0, column=3, sticky="w", padx=6)

        tk.Label(add_frame, text="Unit Purchase Price:", bg=self.white).grid(row=1, column=0, sticky="w", pady=(6,0))
        self.unit_price_var = tk.StringVar()
        tk.Entry(add_frame, textvariable=self.unit_price_var, width=12).grid(row=1, column=1, sticky="w", padx=6, pady=(6,0))

        tk.Button(add_frame, text="Add to Cart", bg=self.secondary_color, fg=self.white, font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", command=self.add_to_cart).grid(row=1, column=3, sticky="e", padx=6, pady=(6,0))

        # Bind select on items_tree to populate selected fields
        self.items_tree.bind("<<TreeviewSelect>>", self.on_item_select)

        # Right: Cart
        right_frame = tk.Frame(middle_frame, bg=self.white)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10,0))

        tk.Label(right_frame, text="Purchase Cart", font=("Arial", 14, "bold"), bg=self.white, fg=self.primary_color).pack(anchor="w", padx=10, pady=(10,0))

        self.cart_columns = ("item_id", "item_name", "qty", "unit_price", "subtotal")
        self.cart_tree = ttk.Treeview(right_frame, columns=self.cart_columns, show="headings", selectmode="browse", height=10)
        cart_headings = {
            "item_id": "ID",
            "item_name": "Name",
            "qty": "Qty",
            "unit_price": "Unit Price",
            "subtotal": "Subtotal"
        }
        for col in self.cart_columns:
            self.cart_tree.heading(col, text=cart_headings[col])
            if col == "item_name":
                self.cart_tree.column(col, width=200)
            elif col in ("unit_price", "subtotal"):
                self.cart_tree.column(col, width=100, anchor="e")
            else:
                self.cart_tree.column(col, width=60)
        self.cart_tree.pack(fill="both", expand=True, padx=10, pady=10)

        cart_btn_frame = tk.Frame(right_frame, bg=self.white)
        cart_btn_frame.pack(fill="x", padx=10, pady=(0,10))
        tk.Button(cart_btn_frame, text="Remove Selected", bg="#95A5A6", fg=self.white, font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", command=self.remove_selected_cart).pack(side="left", padx=6)
        tk.Button(cart_btn_frame, text="Clear Cart", bg=self.accent_color, fg=self.white, font=("Arial", 11, "bold"),
                  relief="flat", cursor="hand2", command=self.clear_cart).pack(side="left", padx=6)

        # Bottom: supplier, totals, save
        bottom_frame = tk.Frame(self.root, bg=self.bg_color)
        bottom_frame.pack(fill="x", padx=20, pady=(6,20))

        left_bottom = tk.Frame(bottom_frame, bg=self.bg_color)
        left_bottom.pack(side="left", fill="x", expand=True)

        tk.Label(left_bottom, text="Supplier Name:", font=("Arial", 12), bg=self.bg_color).grid(row=0, column=0, sticky="w")
        self.supplier_entry = tk.Entry(left_bottom, font=("Arial", 12), width=30)
        self.supplier_entry.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        right_bottom = tk.Frame(bottom_frame, bg=self.bg_color)
        right_bottom.pack(side="right", fill="x", padx=(0,20))

        tk.Label(right_bottom, text="Total:", font=("Arial", 14, "bold"), bg=self.bg_color).grid(row=0, column=0, sticky="e")
        self.total_var = tk.StringVar(value="0.00")
        tk.Label(right_bottom, textvariable=self.total_var, font=("Arial", 14, "bold"), bg=self.bg_color, fg=self.primary_color).grid(row=0, column=1, sticky="e", padx=(8,0))

        tk.Button(right_bottom, text="Save Purchase", bg=self.secondary_color, fg=self.white, font=("Arial", 12, "bold"),
                  relief="flat", cursor="hand2", command=self.save_purchase).grid(row=1, column=0, columnspan=2, pady=(10,0), ipadx=20, ipady=6)

    # ---------------- DB / utility ----------------
    def load_all_items(self):
        conn = self.db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT item_id, item_name, purchase_price, stock, expiry_date
            FROM medical_items
            ORDER BY item_id DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        self.items_tree.delete(*self.items_tree.get_children())
        for r in rows:
            self.items_tree.insert("", "end", values=(r[0], r[1], r[2], r[3] if r[3] is not None else 0, r[4] if r[4] else ""))

    def search_items(self):
        kw = self.search_entry.get().strip()
        if not kw:
            self.load_all_items()
            return
        conn = self.db_connection()
        cursor = conn.cursor()
        if kw.isdigit():
            cursor.execute("""
                SELECT item_id, item_name, purchase_price, stock, expiry_date
                FROM medical_items WHERE item_id = ?
            """, (int(kw),))
        else:
            cursor.execute("""
                SELECT item_id, item_name, purchase_price, stock, expiry_date
                FROM medical_items WHERE item_name LIKE ?
            """, (f"%{kw}%",))
        rows = cursor.fetchall()
        conn.close()
        self.items_tree.delete(*self.items_tree.get_children())
        for r in rows:
            self.items_tree.insert("", "end", values=(r[0], r[1], r[2], r[3] if r[3] is not None else 0, r[4] if r[4] else ""))

    def on_item_select(self, event=None):
        sel = self.items_tree.selection()
        if not sel:
            return
        vals = self.items_tree.item(sel[0])["values"]
        item_id, name, purchase_price, stock, expiry = vals
        self.selected_item_var.set(str(item_id))
        # ensure numeric formatting
        try:
            price_val = float(purchase_price)
        except Exception:
            price_val = 0.0
        self.unit_price_var.set(f"{price_val:.2f}")
        self.qty_var.set("1")

    # ---------------- Cart operations ----------------
    def add_to_cart(self):
        try:
            item_id = int(self.selected_item_var.get())
        except Exception:
            messagebox.showerror("Error", "Select an item first.")
            return
        try:
            qty = int(self.qty_var.get())
            if qty <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Quantity must be a positive integer.")
            return

        try:
            purchase_price = float(self.unit_price_var.get())
        except Exception:
            messagebox.showerror("Error", "Unit purchase price must be a number.")
            return

        # fetch latest stock from DB
        conn = self.db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, stock FROM medical_items WHERE item_id = ?", (item_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            messagebox.showerror("Error", "Item not found in database.")
            return
        item_name, stock = row
        stock = stock if stock is not None else 0

        subtotal = round(qty * float(purchase_price), 2)

        # if item already in cart, increment qty
        for c in self.cart:
            if c["item_id"] == item_id:
                c["qty"] = c["qty"] + qty
                c["purchase_price"] = float(purchase_price)  # update price to latest entered
                c["subtotal"] = round(c["qty"] * c["purchase_price"], 2)
                self.refresh_cart_view()
                self.calculate_total()
                return

        cart_item = {"item_id": item_id, "item_name": item_name, "qty": qty, "purchase_price": float(purchase_price), "subtotal": subtotal}
        self.cart.append(cart_item)
        self.refresh_cart_view()
        self.calculate_total()

    def refresh_cart_view(self):
        self.cart_tree.delete(*self.cart_tree.get_children())
        for c in self.cart:
            self.cart_tree.insert("", "end", values=(c["item_id"], c["item_name"], c["qty"], f"{c['purchase_price']:.2f}", f"{c['subtotal']:.2f}"))

    def calculate_total(self):
        total = sum(c["subtotal"] for c in self.cart)
        self.total_var.set(f"{total:.2f}")

    def remove_selected_cart(self):
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a cart row to remove.")
            return
        vals = self.cart_tree.item(sel[0])["values"]
        item_id = int(vals[0])
        self.cart = [c for c in self.cart if c["item_id"] != item_id]
        self.refresh_cart_view()
        self.calculate_total()

    def clear_cart(self):
        if not self.cart:
            return
        if not messagebox.askyesno("Confirm", "Clear all items from cart?"):
            return
        self.cart = []
        self.refresh_cart_view()
        self.calculate_total()

    # ---------------- Save purchase ----------------
    def save_purchase(self):
        if not self.cart:
            messagebox.showerror("Error", "Cart is empty.")
            return
        supplier = self.supplier_entry.get().strip() or None
        total = sum(c["subtotal"] for c in self.cart)

        conn = self.db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("BEGIN")
            # Insert into purchases
            purchase_date = datetime.now()
            cursor.execute("""
                INSERT INTO purchases (purchase_date, supplier_name, total_amount)
                VALUES (?, ?, ?)
            """, (purchase_date, supplier, total))
            purchase_id = cursor.lastrowid

            # Insert purchase_details and increase stock
            for c in self.cart:
                subtotal = round(c["qty"] * c["purchase_price"], 2)
                cursor.execute("""
                    INSERT INTO purchase_details (purchase_id, item_id, quantity, purchase_price, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """, (purchase_id, c["item_id"], c["qty"], c["purchase_price"], subtotal))
                # increase stock
                cursor.execute("UPDATE medical_items SET stock = COALESCE(stock,0) + ? WHERE item_id = ?", (c["qty"], c["item_id"]))
                # Optionally, update purchase_price in medical_items if you want the latest purchase price stored:
                # cursor.execute("UPDATE medical_items SET purchase_price = ? WHERE item_id = ?", (c["purchase_price"], c["item_id"]))

            conn.commit()
            messagebox.showinfo("Success", f"Purchase saved successfully (Purchase ID: {purchase_id}).")
            # reset UI
            self.cart = []
            self.refresh_cart_view()
            self.calculate_total()
            self.supplier_entry.delete(0, tk.END)
            self.load_all_items()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Could not save purchase: {e}")
        finally:
            conn.close()

    def go_back(self):
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
    app = ManagePurchase(root)
    root.mainloop()
