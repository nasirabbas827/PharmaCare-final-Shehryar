import sqlite3
from datetime import datetime

def create_database():
    """Create PharmaCare Management System Database with updated schema"""
    
    # Connect to SQLite database (creates file if it doesn't exist)
    conn = sqlite3.connect('pharmacare.db')
    cursor = conn.cursor()
    
    # Enable foreign key support
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # 1. Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Admin', 'User')),
        email TEXT UNIQUE,
        phone TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. Create categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT UNIQUE NOT NULL,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 3. Create medical_items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medical_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        image BLOB,
        item_name TEXT NOT NULL,
        category_id INTEGER,
        description TEXT,
        manufacturer TEXT,
        purchase_price REAL NOT NULL,
        sale_price REAL NOT NULL,
        stock INTEGER,
        expiry_date DATE,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    )
    ''')
    
    # 4. Create purchases table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchases (
        purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
        purchase_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        supplier_name TEXT,
        total_amount REAL NOT NULL
    )
    ''')
    
    # 5. Create purchase_details table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchase_details (
        purchase_detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
        purchase_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        purchase_price REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id),
        FOREIGN KEY (item_id) REFERENCES medical_items(item_id)
    )
    ''')
    
    # 6. Create sales table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        customer_name TEXT,
        total_amount REAL NOT NULL,
        payment_method TEXT
    )
    ''')
    
    # 7. Create sale_details table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sale_details (
        sale_detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        sale_price REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
        FOREIGN KEY (item_id) REFERENCES medical_items(item_id)
    )
    ''')
    
    # Create indexes for faster searches
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_item_name ON medical_items(item_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sale_date ON sales(sale_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_purchase_date ON purchases(purchase_date)')
    
    # Insert default admin user
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password, full_name, role, email, phone)
    VALUES ('admin', 'admin123', 'System Administrator', 'Admin', 'admin@pharmacare.com', '+92-300-1234567')
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("✓ Database 'pharmacare.db' created successfully!")
    print("✓ All tables created")
    print("✓ Default admin user added")
    print("\n" + "="*50)
    print("ADMIN LOGIN CREDENTIALS")
    print("="*50)
    print("Username: admin")
    print("Password: admin123")
    print("="*50)
    print("\nDatabase is ready to use!")

def verify_database():
    """Verify database creation by displaying table information"""
    conn = sqlite3.connect('pharmacare.db')
    cursor = conn.cursor()
    
    # Get list of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\n" + "="*50)
    print("DATABASE VERIFICATION")
    print("="*50)
    print(f"\nTotal Tables Created: {len(tables)}\n")
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  • {table_name:20} - {count} records")
    
    conn.close()

if __name__ == "__main__":
    create_database()
    verify_database()