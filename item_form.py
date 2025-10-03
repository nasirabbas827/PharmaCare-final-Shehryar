import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk  # For image preview

IMAGES_DIR = "images"

class ItemForm:
    def __init__(self, root, mode="add", item_data=None, admin_id=None, admin_name="Admin User"):
        self.root = root
        self.mode = mode
        self.item_data = item_data
        self.admin_id = admin_id  # Store admin_id
        self.admin_name = admin_name  # Store admin_name
        self.image_preview_ref = None  # Keep reference to avoid garbage collection

        self.root.title("Item Form - PharmaCare")
        self.root.geometry("1250x600")
        self.root.resizable(False, False)
        self.center_window(1250, 600)

        self.primary_color = "#2C3E50"
        self.secondary_color = "#3498DB"
        self.accent_color = "#E74C3C"
        self.bg_color = "#ECF0F1"
        self.white = "#FFFFFF"

        self.root.configure(bg=self.bg_color)

        os.makedirs(IMAGES_DIR, exist_ok=True)

        self.create_layout()

        if self.mode == "edit" and self.item_data:
            self.load_item()

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
        title = "Add Item" if self.mode == "add" else f"Edit Item (ID: {self.item_data[0] if self.item_data else ''})"
        tk.Label(
            header,
            text=title,
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

        form_frame = tk.Frame(self.root, bg=self.white)
        form_frame.pack(padx=20, pady=12, fill="both", expand=True)

        left_col = tk.Frame(form_frame, bg=self.white)
        left_col.pack(side="left", fill="both", expand=True, padx=(10,5), pady=10)

        right_col = tk.Frame(form_frame, bg=self.white)
        right_col.pack(side="right", fill="both", expand=True, padx=(5,10), pady=10)

        # Image section
        tk.Label(left_col, text="Image", font=("Arial", 12, "bold"), bg=self.white).pack(anchor="w")
        self.image_path_var = tk.StringVar()

        self.image_label = tk.Label(
            left_col,
            text="No image selected",
            bg="#F8F9FA",
            anchor="center",
            relief="groove"
        )
        self.image_label.pack(fill="both", pady=6)

        tk.Button(
            left_col,
            text="Choose Image",
            font=("Arial", 12),
            bg=self.secondary_color,
            fg=self.white,
            relief="flat",
            command=self.choose_image
        ).pack(pady=4)

        lbl_cfg = {"font": ("Arial", 12, "bold"), "bg": self.white, "anchor": "w"}
        entry_cfg = {"font": ("Arial", 12), "bg": "#F8F9FA", "relief": "flat"}

        tk.Label(right_col, text="Item Name", **lbl_cfg).pack(fill="x", pady=(4,0))
        self.item_name_entry = tk.Entry(right_col, **entry_cfg)
        self.item_name_entry.pack(fill="x", pady=4, ipady=6)

        tk.Label(right_col, text="Category", **lbl_cfg).pack(fill="x", pady=(4,0))
        self.category_cb = ttk.Combobox(right_col, state="readonly", font=("Arial", 12))
        self.category_cb.pack(fill="x", pady=4, ipady=6)
        self.load_categories()

        tk.Label(right_col, text="Manufacturer", **lbl_cfg).pack(fill="x", pady=(4,0))
        self.manufacturer_entry = tk.Entry(right_col, **entry_cfg)
        self.manufacturer_entry.pack(fill="x", pady=4, ipady=6)

        tk.Label(right_col, text="Description", **lbl_cfg).pack(fill="x", pady=(4,0))
        self.description_text = tk.Text(right_col, height=4, font=("Arial", 12), bg="#F8F9FA", relief="flat")
        self.description_text.pack(fill="x", pady=4)

        prices_frame = tk.Frame(left_col, bg=self.white)
        prices_frame.pack(fill="x", pady=(10,0))

        tk.Label(prices_frame, text="Purchase Price", **lbl_cfg).grid(row=0, column=0, sticky="w")
        self.purchase_entry = tk.Entry(prices_frame, **entry_cfg)
        self.purchase_entry.grid(row=1, column=0, sticky="we", padx=(0,10), pady=4)

        tk.Label(prices_frame, text="Sale Price", **lbl_cfg).grid(row=0, column=1, sticky="w")
        self.sale_entry = tk.Entry(prices_frame, **entry_cfg)
        self.sale_entry.grid(row=1, column=1, sticky="we", padx=(0,10), pady=4)

        tk.Label(prices_frame, text="Stock", **lbl_cfg).grid(row=2, column=0, sticky="w")
        self.stock_entry = tk.Entry(prices_frame, **entry_cfg)
        self.stock_entry.grid(row=3, column=0, sticky="we", padx=(0,10), pady=4)

        tk.Label(prices_frame, text="Expiry Date", **lbl_cfg).grid(row=2, column=1, sticky="w")
        self.expiry_entry = DateEntry(
            prices_frame,
            font=("Arial", 12),
            background="#F8F9FA",
            borderwidth=0,
            date_pattern="yyyy-mm-dd"
        )
        self.expiry_entry.grid(row=3, column=1, sticky="we", padx=(0,10), pady=4)

        prices_frame.columnconfigure(0, weight=1)
        prices_frame.columnconfigure(1, weight=1)

        action_frame = tk.Frame(self.root, bg=self.bg_color)
        action_frame.pack(fill="x", padx=20, pady=(6,20))

        save_text = "Save Item" if self.mode == "add" else "Update Item"
        tk.Button(
            action_frame,
            text=save_text,
            bg=self.secondary_color,
            fg=self.white,
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.save_item
        ).pack(side="left", padx=6)

    def load_categories(self):
        try:
            conn = self.db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT category_id, category_name FROM categories ORDER BY category_name")
            rows = cursor.fetchall()
            conn.close()
        except sqlite3.Error:
            rows = []

        self.categories = [(r[0], r[1]) for r in rows]
        names = [r[1] for r in rows]
        self.category_cb["values"] = names
        if names:
            self.category_cb.current(0)

    def choose_image(self):
        filetypes = [("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"), ("All files", "*.*")]
        src = filedialog.askopenfilename(title="Choose Image", filetypes=filetypes)
        if not src:
            return

        try:
            basename = os.path.basename(src)
            name, ext = os.path.splitext(basename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            dest_name = f"{name}_{timestamp}{ext}"
            dest_path = os.path.join(IMAGES_DIR, dest_name)
            shutil.copy2(src, dest_path)
            self.image_path_var.set(dest_path)
            self.show_image_preview(dest_path)
        except Exception as e:
            messagebox.showerror("File Error", f"Unable to copy image: {e}")

    def show_image_preview(self, path):
        try:
            img = Image.open(path)
            img.thumbnail((150, 150), Image.Resampling.LANCZOS)  # Ensure image fits within 150x150
            img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=img_tk, text="")
            self.image_preview_ref = img_tk  # Keep reference to avoid garbage collection
        except Exception as e:
            self.image_label.config(image="", text=os.path.basename(path))
            print(f"Error loading image: {e}")  # Log the error for debugging

    def load_item(self):
        (
            _,
            image_path,
            item_name,
            category_id,
            description,
            manufacturer,
            purchase_price,
            sale_price,
            stock,
            expiry
        ) = self.item_data

        if image_path:
            self.image_path_var.set(image_path)
            self.show_image_preview(image_path)

        self.item_name_entry.insert(0, item_name or "")

        cat_ids = [c[0] for c in self.categories]
        try:
            idx = cat_ids.index(category_id) if category_id in cat_ids else 0
        except ValueError:
            idx = 0
        if self.categories:
            self.category_cb.current(idx)

        self.manufacturer_entry.insert(0, manufacturer or "")

        if description:
            self.description_text.insert("1.0", description)

        self.purchase_entry.insert(0, str(purchase_price) if purchase_price is not None else "")
        self.sale_entry.insert(0, str(sale_price) if sale_price is not None else "")
        self.stock_entry.insert(0, str(stock) if stock is not None else "")

        if expiry:
            try:
                dt = datetime.strptime(expiry, "%Y-%m-%d")
                self.expiry_entry.set_date(dt)
            except:
                pass

    def save_item(self):
        item_name = self.item_name_entry.get().strip()
        if not item_name:
            messagebox.showerror("Validation", "Item name is required.")
            return

        cat_index = self.category_cb.current()
        category_id = self.categories[cat_index][0] if (self.categories and cat_index >= 0) else None

        manufacturer = self.manufacturer_entry.get().strip() or None
        description = self.description_text.get("1.0", "end").strip() or None

        try:
            purchase_price = float(self.purchase_entry.get().strip())
        except Exception:
            messagebox.showerror("Validation", "Purchase price must be a valid number.")
            return

        try:
            sale_price = float(self.sale_entry.get().strip())
        except Exception:
            messagebox.showerror("Validation", "Sale price must be a valid number.")
            return

        try:
            stock = int(self.stock_entry.get().strip()) if self.stock_entry.get().strip() else 0
        except Exception:
            messagebox.showerror("Validation", "Stock must be an integer.")
            return

        expiry = self.expiry_entry.get_date().strftime("%Y-%m-%d")

        image_path = self.image_path_var.get() or None

        try:
            conn = self.db_connection()
            cursor = conn.cursor()
            if self.mode == "add":
                cursor.execute("""
                    INSERT INTO medical_items
                    (image, item_name, category_id, description, manufacturer,
                     purchase_price, sale_price, stock, expiry_date, created_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    image_path, item_name, category_id, description, manufacturer,
                    purchase_price, sale_price, stock, expiry, datetime.now()
                ))
                conn.commit()
                messagebox.showinfo("Success", "Item saved successfully.")
            else:
                item_id = self.item_data[0]
                cursor.execute("""
                    UPDATE medical_items
                    SET image = ?, item_name = ?, category_id = ?, description = ?, manufacturer = ?,
                        purchase_price = ?, sale_price = ?, stock = ?, expiry_date = ?
                    WHERE item_id = ?
                """, (
                    image_path, item_name, category_id, description, manufacturer,
                    purchase_price, sale_price, stock, expiry, item_id
                ))
                conn.commit()
                messagebox.showinfo("Success", "Item updated successfully.")
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("DB Error", f"An error occurred: {e}")
            return

        if self.root.winfo_exists():
            self.root.destroy()
        import manage_items
        root = tk.Tk()
        manage_items.ManageItems(root, admin_id=self.admin_id, admin_name=self.admin_name)
        root.mainloop()

    def go_back(self):
        try:
            import admin_dashboard
            if self.root.winfo_exists():
                self.root.destroy()
            root = tk.Tk()
            admin_dashboard.AdminDashboard(root, self.admin_id, self.admin_name)
            root.mainloop()
        except Exception as e:
            print(f"Error navigating to AdminDashboard: {e}")
            if self.root.winfo_exists():
                self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    ItemForm(root)
    root.mainloop()