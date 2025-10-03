import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Reports folder
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

class ReportsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reports - PharmaCare")
        self.root.geometry("1250x600")
        self.root.resizable(False, False)
        self.center_window(1250, 600)

        self.primary_color = "#2C3E50"
        self.secondary_color = "#3498DB"
        self.accent_color = "#E74C3C"
        self.bg_color = "#ECF0F1"
        self.white = "#FFFFFF"

        self.root.configure(bg=self.bg_color)

        self.report_rows = []
        self.report_columns = []
        self.report_title = []

        self.create_layout()

    def center_window(self, width, height):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def db_connection(self):
        return sqlite3.connect("pharmacare.db")

    def create_layout(self):
        header = tk.Frame(self.root, bg=self.primary_color, height=70)
        header.pack(fill="x")
        tk.Label(header,
                 text="Reports - PharmaCare",
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
        back_btn.pack(side="right", padx=20, pady=12, ipadx=8, ipady=4)

        controls = tk.Frame(self.root, bg=self.bg_color)
        controls.pack(fill="x", padx=20, pady=12)

        tk.Label(controls, text="Start Date:", font=("Arial", 12), bg=self.bg_color).pack(side="left")
        self.start_date = DateEntry(controls, date_pattern="yyyy-mm-dd", font=("Arial", 11))
        self.start_date.pack(side="left", padx=(8, 12))

        tk.Label(controls, text="End Date:", font=("Arial", 12), bg=self.bg_color).pack(side="left")
        self.end_date = DateEntry(controls, date_pattern="yyyy-mm-dd", font=("Arial", 11))
        self.end_date.pack(side="left", padx=(8, 12))

        tk.Label(controls, text="Report Type:", font=("Arial", 12), bg=self.bg_color).pack(side="left")
        self.report_cb = ttk.Combobox(
            controls,
            values=["Sales Report", "Purchase Report", "Stock Report", "Profit Report"],
            state="readonly",
            font=("Arial", 11),
            width=20
        )
        self.report_cb.pack(side="left", padx=(8, 12))
        self.report_cb.current(0)

        tk.Button(controls, text="Generate Report", font=("Arial", 11, "bold"),
                  bg=self.secondary_color, fg=self.white, relief="flat",
                  cursor="hand2", command=self.generate_report).pack(side="left", padx=6)
        tk.Button(controls, text="Export to PDF", font=("Arial", 11, "bold"),
                  bg=self.secondary_color, fg=self.white, relief="flat",
                  cursor="hand2", command=self.export_pdf).pack(side="left", padx=6)
        tk.Button(controls, text="Clear", font=("Arial", 11, "bold"),
                  bg="#95A5A6", fg=self.white, relief="flat",
                  cursor="hand2", command=self.clear_table).pack(side="left", padx=6)

        table_frame = tk.Frame(self.root, bg=self.white)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0,12))

        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.pack(fill="both", expand=True, side="left")
        self.tree.bind("<Double-1>", self.show_details)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")

        footer = tk.Frame(self.root, bg=self.bg_color, height=60)
        footer.pack(fill="x", padx=20, pady=(0,12))
        self.summary_var = tk.StringVar(value="")
        tk.Label(footer, textvariable=self.summary_var, font=("Arial", 12), bg=self.bg_color, fg=self.primary_color).pack(anchor="w")

    def clear_table(self):
        for c in self.tree.get_children():
            self.tree.delete(c)
        self.tree["columns"] = []
        self.report_rows = []
        self.report_columns = []
        self.report_title = ""
        self.summary_var.set("")

    def generate_report(self):
        rtype = self.report_cb.get()
        start = self.start_date.get_date().strftime("%Y-%m-%d")
        end = self.end_date.get_date().strftime("%Y-%m-%d")

        if start > end:
            messagebox.showerror("Date Error", "Start date must be before or equal to end date.")
            return

        self.clear_table()

        try:
            if rtype == "Sales Report":
                self._sales_report(start, end)
            elif rtype == "Purchase Report":
                self._purchase_report(start, end)
            elif rtype == "Stock Report":
                self._stock_report()
            elif rtype == "Profit Report":
                self._profit_report(start, end)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")

    def _sales_report(self, start, end):
        conn = self.db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sd.sale_detail_id, s.sale_date, s.customer_name, mi.item_name, sd.quantity, sd.sale_price, sd.subtotal
            FROM sale_details sd
            JOIN sales s ON sd.sale_id = s.sale_id
            LEFT JOIN medical_items mi ON sd.item_id = mi.item_id
            WHERE DATE(s.sale_date) BETWEEN ? AND ?
            ORDER BY s.sale_date
        """, (start, end))
        rows = cursor.fetchall()

        cursor.execute("SELECT COALESCE(SUM(total_amount),0) FROM sales WHERE DATE(sale_date) BETWEEN ? AND ?", (start, end))
        total_sales = cursor.fetchone()[0] or 0.0
        conn.close()

        columns = ["Detail ID","Sale Date","Customer Name","Item Name","Quantity","Unit Price","Subtotal"]
        self.report_columns = columns
        self.report_rows = [[r[0], r[1], r[2] or "", r[3] or "", r[4], r[5], r[6]] for r in rows]
        self.report_title = f"Sales Report ({start} to {end})"

        self._populate_tree(columns, self.report_rows)
        self.summary_var.set(f"Total Sales Amount: {total_sales:.2f}")

    def _purchase_report(self, start, end):
        conn = self.db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pd.purchase_detail_id, p.purchase_date, p.supplier_name, mi.item_name, pd.quantity, pd.purchase_price, pd.subtotal
            FROM purchase_details pd
            JOIN purchases p ON pd.purchase_id = p.purchase_id
            LEFT JOIN medical_items mi ON pd.item_id = mi.item_id
            WHERE DATE(p.purchase_date) BETWEEN ? AND ?
            ORDER BY p.purchase_date
        """, (start, end))
        rows = cursor.fetchall()

        cursor.execute("SELECT COALESCE(SUM(total_amount),0) FROM purchases WHERE DATE(purchase_date) BETWEEN ? AND ?", (start, end))
        total_purchase = cursor.fetchone()[0] or 0.0
        conn.close()

        columns = ["Detail ID","Purchase Date","Supplier Name","Item Name","Quantity","Unit Price","Subtotal"]
        self.report_columns = columns
        self.report_rows = [[r[0], r[1], r[2] or "", r[3] or "", r[4], r[5], r[6]] for r in rows]
        self.report_title = f"Purchase Report ({start} to {end})"

        self._populate_tree(columns, self.report_rows)
        self.summary_var.set(f"Total Purchase Amount: {total_purchase:.2f}")

    def _stock_report(self):
        conn = self.db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT item_id, item_name, COALESCE(stock,0) as stock, COALESCE(expiry_date, '') as expiry
            FROM medical_items
            ORDER BY item_name
        """)
        rows = cursor.fetchall()
        conn.close()

        columns = ["Item ID", "Item Name", "Available Stock", "Expiry Date"]
        self.report_columns = columns
        self.report_rows = [[r[0], r[1] or "", int(r[2]), r[3] or ""] for r in rows]
        self.report_title = "Stock Report (Current)"

        self._populate_tree(columns, self.report_rows)
        zero_count = sum(1 for r in rows if (r[2] or 0) <= 0)
        self.summary_var.set(f"Items with zero stock: {zero_count} | Total items: {len(rows)}")

    def _profit_report(self, start, end):
        conn = self.db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(total_amount),0) FROM sales WHERE DATE(sale_date) BETWEEN ? AND ?", (start, end))
        total_sales = cursor.fetchone()[0] or 0.0
        cursor.execute("SELECT COALESCE(SUM(total_amount),0) FROM purchases WHERE DATE(purchase_date) BETWEEN ? AND ?", (start, end))
        total_purchases = cursor.fetchone()[0] or 0.0
        conn.close()

        profit = total_sales - total_purchases
        self.report_columns = ["Metric","Amount"]
        self.report_rows = [["Total Sales", total_sales], ["Total Purchases", total_purchases], ["Profit", profit]]
        self.report_title = f"Profit Report ({start} to {end})"
        self._populate_tree(self.report_columns, self.report_rows)
        self.summary_var.set(f"Profit: {profit:.2f}")

    def _populate_tree(self, columns, rows):
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col)
            if "Name" in col:
                self.tree.column(col, width=280)
            elif "Amount" in col or "Price" in col or "Profit" in col or "Subtotal" in col:
                self.tree.column(col, width=120, anchor="e")
            else:
                self.tree.column(col, width=100, anchor="center")

        for r in rows:
            display = [str(v) if not isinstance(v, float) else f"{v:.2f}" for v in r]
            self.tree.insert("", "end", values=display)

    def show_details(self, event):
        # Show selected item details in a messagebox
        sel = self.tree.focus()
        if not sel:
            return
        values = self.tree.item(sel, "values")
        detail_text = "\n".join(f"{col}: {val}" for col, val in zip(self.report_columns, values))
        messagebox.showinfo("Detail Info", detail_text)

    def export_pdf(self):
        if not self.report_columns or not self.report_rows:
            messagebox.showwarning("No Data", "Generate a report before exporting to PDF.")
            return

        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{self.report_title.replace(' ', '_')}_{ts}.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)

        try:
            doc = SimpleDocTemplate(filepath, pagesize=landscape(A4), rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
            styles = getSampleStyleSheet()
            elements = []

            elements.append(Paragraph(self.report_title, styles["Title"]))
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
            elements.append(Spacer(1, 12))

            table_data = [self.report_columns]
            for row in self.report_rows:
                formatted = []
                for val in row:
                    if isinstance(val, float):
                        formatted.append(f"{val:.2f}")
                    else:
                        formatted.append(str(val))
                table_data.append(formatted)

            tbl = Table(table_data, repeatRows=1)
            tbl_style = TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor(self.primary_color)),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("ALIGN", (0,0), (-1,-1), "CENTER"),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ])
            tbl.setStyle(tbl_style)
            ncols = len(self.report_columns)
            col_width = (landscape(A4)[0] - (36*mm)) / ncols
            tbl._argW = [col_width]*ncols

            elements.append(tbl)
            elements.append(Spacer(1,12))
            elements.append(Paragraph(self.summary_var.get(), styles["Normal"]))

            doc.build(elements)
            messagebox.showinfo("PDF Exported", f"Report exported to: {filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export PDF: {e}")

    def go_back(self):
        try:
            import admin_dashboard
            self.root.destroy()
            root = tk.Tk()
            admin_dashboard.AdminDashboard(root, None, None)
            root.mainloop()
        except Exception:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReportsApp(root)
    root.mainloop()
