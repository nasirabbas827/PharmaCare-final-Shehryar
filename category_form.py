import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class CategoryForm:
    def __init__(self, root, refresh_callback=None, category_data=None):
        self.root = root
        self.refresh_callback = refresh_callback
        self.category_data = category_data

        self.root.title("Category Form")
        self.root.geometry("500x300")
        self.root.configure(bg="#ECF0F1")
        self.center_window(500, 300)

        self.primary_color = "#2C3E50"
        self.secondary_color = "#3498DB"
        self.white = "#FFFFFF"

        self.create_widgets()

    def center_window(self, width, height):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        form_frame = tk.Frame(self.root, bg=self.white, padx=20, pady=20)
        form_frame.pack(expand=True, fill="both", padx=30, pady=30)

        title_text = "Edit Category" if self.category_data else "Add Category"
        tk.Label(
            form_frame,
            text=title_text,
            font=("Arial", 20, "bold"),
            bg=self.white,
            fg=self.primary_color
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        tk.Label(
            form_frame,
            text="Category Name",
            font=("Arial", 12, "bold"),
            bg=self.white,
            fg=self.primary_color
        ).grid(row=1, column=0, sticky="w", pady=5)

        self.category_name_var = tk.StringVar()
        self.category_entry = tk.Entry(
            form_frame,
            textvariable=self.category_name_var,
            font=("Arial", 12),
            bg="#F8F9FA",
            fg=self.primary_color,
            relief="flat"
        )
        self.category_entry.grid(row=1, column=1, pady=5, padx=10, sticky="ew")

        if self.category_data:
            self.category_name_var.set(self.category_data[1])

        btn_text = "Update" if self.category_data else "Save"
        self.save_btn = tk.Button(
            form_frame,
            text=btn_text,
            font=("Arial", 12, "bold"),
            bg=self.secondary_color,
            fg=self.white,
            relief="flat",
            command=self.save_category
        )
        self.save_btn.grid(row=2, column=0, columnspan=2, pady=20, ipadx=10, ipady=5)

        form_frame.columnconfigure(1, weight=1)

    def save_category(self):
        name = self.category_name_var.get().strip()

        if not name:
            messagebox.showerror("Error", "Category name is required!")
            return

        conn = sqlite3.connect('pharmacare.db')
        cursor = conn.cursor()

        try:
            if self.category_data:
                cursor.execute("""
                    UPDATE categories
                    SET category_name = ?
                    WHERE category_id = ?
                """, (name, self.category_data[0]))
                messagebox.showinfo("Success", "Category updated successfully!")
            else:
                cursor.execute("""
                    INSERT INTO categories (category_name)
                    VALUES (?)
                """, (name,))
                messagebox.showinfo("Success", "Category added successfully!")

            conn.commit()
            if self.refresh_callback:
                self.refresh_callback()
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    CategoryForm(root)
    root.mainloop()
