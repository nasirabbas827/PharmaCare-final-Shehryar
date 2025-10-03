import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class PharmaCareLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("PharmaCare Management System - Login")
        self.root.geometry("1250x800")
        self.root.resizable(False, False)
        
        # Center window on screen
        self.center_window()
        
        # Configure colors
        self.primary_color = "#2C3E50"
        self.secondary_color = "#3498DB"
        self.accent_color = "#E74C3C"
        self.bg_color = "#ECF0F1"
        self.white = "#FFFFFF"
        
        self.root.configure(bg=self.bg_color)
        
        self.create_widgets()
    
    def center_window(self):
        self.root.update_idletasks()
        width = 1250
        height = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, fill="both")
        
        # Left side - Decorative panel
        left_panel = tk.Frame(main_frame, bg=self.primary_color, width=400)
        left_panel.pack(side="left", fill="both", expand=True)
        left_panel.pack_propagate(False)
        
        # Logo and welcome text
        welcome_frame = tk.Frame(left_panel, bg=self.primary_color)
        welcome_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(
            welcome_frame,
            text="💊",
            font=("Arial", 80),
            bg=self.primary_color,
            fg=self.white
        ).pack(pady=20)
        
        tk.Label(
            welcome_frame,
            text="PharmaCare",
            font=("Arial", 36, "bold"),
            bg=self.primary_color,
            fg=self.white
        ).pack()
        
        tk.Label(
            welcome_frame,
            text="Management System",
            font=("Arial", 18),
            bg=self.primary_color,
            fg=self.secondary_color
        ).pack(pady=10)
        
        tk.Label(
            welcome_frame,
            text="Your Healthcare Partner",
            font=("Arial", 14, "italic"),
            bg=self.primary_color,
            fg="#95A5A6"
        ).pack(pady=20)
        
        # Right side - Login form
        right_panel = tk.Frame(main_frame, bg=self.white, width=600)
        right_panel.pack(side="right", fill="both", expand=True)
        right_panel.pack_propagate(False)
        
        # Login form container
        login_frame = tk.Frame(right_panel, bg=self.white)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        tk.Label(
            login_frame,
            text="Welcome Back!",
            font=("Arial", 32, "bold"),
            bg=self.white,
            fg=self.primary_color
        ).pack(pady=(0, 10))
        
        tk.Label(
            login_frame,
            text="Please login to your account",
            font=("Arial", 12),
            bg=self.white,
            fg="#7F8C8D"
        ).pack(pady=(0, 40))
        
        # Username field
        tk.Label(
            login_frame,
            text="Username",
            font=("Arial", 12, "bold"),
            bg=self.white,
            fg=self.primary_color,
            anchor="w"
        ).pack(fill="x", padx=40)
        
        username_frame = tk.Frame(login_frame, bg=self.white)
        username_frame.pack(fill="x", padx=40, pady=(5, 20))
        
        tk.Label(
            username_frame,
            text="👤",
            font=("Arial", 16),
            bg=self.white
        ).pack(side="left", padx=(0, 10))
        
        self.username_entry = tk.Entry(
            username_frame,
            font=("Arial", 14),
            bg="#F8F9FA",
            fg=self.primary_color,
            relief="flat",
            bd=0
        )
        self.username_entry.pack(side="left", fill="x", expand=True, ipady=8)
        
        # Add border effect
        username_border = tk.Frame(login_frame, height=2, bg="#BDC3C7")
        username_border.pack(fill="x", padx=40)
        
        # Password field
        tk.Label(
            login_frame,
            text="Password",
            font=("Arial", 12, "bold"),
            bg=self.white,
            fg=self.primary_color,
            anchor="w"
        ).pack(fill="x", padx=40, pady=(20, 0))
        
        password_frame = tk.Frame(login_frame, bg=self.white)
        password_frame.pack(fill="x", padx=40, pady=(5, 20))
        
        tk.Label(
            password_frame,
            text="🔒",
            font=("Arial", 16),
            bg=self.white
        ).pack(side="left", padx=(0, 10))
        
        self.password_entry = tk.Entry(
            password_frame,
            font=("Arial", 14),
            bg="#F8F9FA",
            fg=self.primary_color,
            show="●",
            relief="flat",
            bd=0
        )
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=8)
        
        # Add border effect
        password_border = tk.Frame(login_frame, height=2, bg="#BDC3C7")
        password_border.pack(fill="x", padx=40)
        
        # Login button
        self.login_btn = tk.Button(
            login_frame,
            text="LOGIN",
            font=("Arial", 14, "bold"),
            bg=self.secondary_color,
            fg=self.white,
            activebackground="#2980B9",
            activeforeground=self.white,
            cursor="hand2",
            relief="flat",
            bd=0,
            command=self.login
        )
        self.login_btn.pack(fill="x", padx=40, pady=30, ipady=12)
        
        # Bind hover effects
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg="#2980B9"))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.config(bg=self.secondary_color))
        
        # Bind Enter key to login
        self.root.bind("<Return>", lambda e: self.login())
        
        # Footer
        footer_frame = tk.Frame(right_panel, bg=self.white)
        footer_frame.pack(side="bottom", fill="x", pady=20)
        
        tk.Label(
            footer_frame,
            text="© 2025 PharmaCare Management System. All rights reserved.",
            font=("Arial", 9),
            bg=self.white,
            fg="#95A5A6"
        ).pack()
        
        # Focus on username entry
        self.username_entry.focus()
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password!")
            return
        
        # Connect to database
        try:
            conn = sqlite3.connect('pharmacare.db')
            cursor = conn.cursor()
            
            # Query user
            cursor.execute('''
                SELECT user_id, full_name, role 
                FROM users 
                WHERE username = ? AND password = ?
            ''', (username, password))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                user_id, full_name, role = user
                messagebox.showinfo("Success", f"Welcome, {full_name}!")
                
                # Close login window
                self.root.destroy()
                
                # Open appropriate dashboard
                if role == "Admin":
                    self.open_admin_dashboard(user_id, full_name)
                else:
                    self.open_user_dashboard(user_id, full_name)
            else:
                messagebox.showerror("Error", "Invalid username or password!")
                self.password_entry.delete(0, tk.END)
        
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
    
    def open_admin_dashboard(self, user_id, full_name):
        import admin_dashboard
        root = tk.Tk()
        admin_dashboard.AdminDashboard(root, user_id, full_name)
        root.mainloop()
    
    def open_user_dashboard(self, user_id, full_name):
        import user_dashboard
        root = tk.Tk()
        user_dashboard.UserDashboard(root, user_id, full_name)
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = PharmaCareLogin(root)
    root.mainloop()