import os
import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ExpenseDataManager:
    """Handles CSV file operations, Pandas data management, and NumPy calculations."""
    
    def __init__(self, filename="expenses.csv"):
        self.filename = filename
        self.columns = ["Date", "Category", "Amount", "Description"]
        self._initialize_csv()

    def _initialize_csv(self):
        """Creates the CSV file with headers if it does not exist."""
        if not os.path.exists(self.filename):
            with open(self.filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(self.columns)

    def add_expense(self, date_str, category, amount, description):
        """Appends a new expense record to the CSV file."""
        with open(self.filename, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([date_str, category, float(amount), description])

    def load_data(self):
        """Loads expense records into a Pandas DataFrame."""
        try:
            df = pd.read_csv(self.filename)
            if not df.empty:
                df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
            return df
        except Exception:
            return pd.DataFrame(columns=self.columns)

    def delete_expense(self, index):
        """Deletes a specific row by index using Pandas and updates the CSV."""
        df = self.load_data()
        if 0 <= index < len(df):
            df = df.drop(index).reset_index(drop=True)
            df.to_csv(self.filename, index=False)
            return True
        return False

    def get_statistics(self):
        """Calculates summary statistics using NumPy."""
        df = self.load_data()
        if df.empty:
            return {"total": 0.0, "mean": 0.0, "max": 0.0, "min": 0.0, "std": 0.0}

        amounts = df["Amount"].to_numpy()
        return {
            "total": np.sum(amounts),
            "mean": np.mean(amounts),
            "max": np.max(amounts),
            "min": np.min(amounts),
            "std": np.std(amounts)
        }


class ExpenseEaseApp:
    """Main GUI Application class built with Tkinter."""

    def __init__(self, root):
        self.root = root
        self.root.title("ExpenseEase – Personal Expense Tracker")
        self.root.geometry("950x620")
        self.root.configure(bg="#f4f6f9")

        self.data_manager = ExpenseDataManager()

        self._setup_styles()
        self._build_ui()
        self.refresh_ui()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#d9e2ec",
            relief="raised",
            padding=(6, 8)
        )
        style.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=30,
            background="white",
            fieldbackground="white",
            borderwidth=1,
            relief="solid"
        )
        style.map(
            "Treeview",
            background=[("selected", "#cfe2ff")],
            foreground=[("selected", "#111827")]
        )

    def _build_ui(self):
        # --- Header ---
        header = tk.Frame(self.root, bg="#2b4c7e", height=60)
        header.pack(fill=tk.X)
        tk.Label(
            header, text="ExpenseEase – Personal Expense Tracker",
            fg="white", bg="#2b4c7e", font=("Segoe UI", 18, "bold"), pady=12
        ).pack()

        # --- Main Layout Container ---
        main_frame = tk.Frame(self.root, bg="#f4f6f9", padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left Panel: Input Form & Statistics
        left_panel = tk.Frame(main_frame, bg="#ffffff", bd=1, relief=tk.SOLID, padx=15, pady=15)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

        tk.Label(left_panel, text="Add New Expense", font=("Segoe UI", 13, "bold"), bg="#ffffff").pack(anchor="w", pady=(0, 10))

        # Date Input
        tk.Label(left_panel, text="Date (YYYY-MM-DD):", bg="#ffffff", font=("Segoe UI", 10)).pack(anchor="w")
        self.date_entry = ttk.Entry(left_panel, width=28)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(pady=(2, 10))

        # Category Input
        tk.Label(left_panel, text="Category:", bg="#ffffff", font=("Segoe UI", 10)).pack(anchor="w")
        self.category_cb = ttk.Combobox(
            left_panel, width=26, state="readonly",
            values=["Food & Dining", "Transportation", "Utilities", "Entertainment", "Shopping", "Healthcare", "Other"]
        )
        self.category_cb.current(0)
        self.category_cb.pack(pady=(2, 10))

        # Amount Input
        tk.Label(left_panel, text="Amount (₹ / $):", bg="#ffffff", font=("Segoe UI", 10)).pack(anchor="w")
        self.amount_entry = ttk.Entry(left_panel, width=28)
        self.amount_entry.pack(pady=(2, 10))

        # Description Input
        tk.Label(left_panel, text="Description:", bg="#ffffff", font=("Segoe UI", 10)).pack(anchor="w")
        self.desc_entry = ttk.Entry(left_panel, width=28)
        self.desc_entry.pack(pady=(2, 15))

        # Action Buttons
        btn_frame = tk.Frame(left_panel, bg="#ffffff")
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            btn_frame, text="Add Expense", command=self.add_expense,
            bg="#28a745", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, pady=6
        ).pack(fill=tk.X, pady=3)

        tk.Button(
            btn_frame, text="Delete Selected", command=self.delete_selected,
            bg="#dc3545", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, pady=6
        ).pack(fill=tk.X, pady=3)

        tk.Button(
            btn_frame, text="Visualize Expenses", command=self.show_visualizations,
            bg="#007bff", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, pady=6
        ).pack(fill=tk.X, pady=3)

        # NumPy Statistics Display
        tk.Frame(left_panel, height=1, bg="#dcdcdc").pack(fill=tk.X, pady=15)
        tk.Label(left_panel, text="Statistical Summary (NumPy)", font=("Segoe UI", 11, "bold"), bg="#ffffff").pack(anchor="w", pady=(0, 8))

        self.stats_label = tk.Label(left_panel, text="", bg="#ffffff", font=("Consolas", 10), justify=tk.LEFT)
        self.stats_label.pack(anchor="w")

        # Right Panel: Expense Table
        right_panel = tk.Frame(main_frame, bg="#ffffff", bd=1, relief=tk.SOLID, padx=10, pady=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right_panel, text="Expense Records", font=("Segoe UI", 13, "bold"), bg="#ffffff").pack(anchor="w", pady=(0, 10))

        # Use bordered Tkinter cells instead of Treeview. Treeview does not
        # draw vertical borders between data cells on many Windows themes.
        self.selected_row_index = None
        table_container = tk.Frame(right_panel, bg="#ffffff")
        table_container.pack(fill=tk.BOTH, expand=True)

        self.table_canvas = tk.Canvas(
            table_container, bg="#ffffff", highlightthickness=0
        )
        vertical_scrollbar = ttk.Scrollbar(
            table_container, orient=tk.VERTICAL, command=self.table_canvas.yview
        )
        horizontal_scrollbar = ttk.Scrollbar(
            right_panel, orient=tk.HORIZONTAL, command=self.table_canvas.xview
        )
        self.table_canvas.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set
        )

        vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.table_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        horizontal_scrollbar.pack(fill=tk.X)

        self.table_rows_frame = tk.Frame(self.table_canvas, bg="#ffffff")
        self.table_window = self.table_canvas.create_window(
            (0, 0), window=self.table_rows_frame, anchor="nw"
        )
        self.table_rows_frame.bind(
            "<Configure>",
            lambda event: self.table_canvas.configure(
                scrollregion=self.table_canvas.bbox("all")
            )
        )
        self.table_canvas.bind(
            "<Configure>",
            lambda event: self.table_canvas.itemconfigure(
                self.table_window, height=max(event.height, self.table_rows_frame.winfo_reqheight())
            )
        )

        self.table_headers = ["#", "Date", "Category", "Amount (₹)", "Description"]
        self.table_widths = [5, 14, 20, 14, 30]
        for col, (heading, width) in enumerate(zip(self.table_headers, self.table_widths)):
            header_cell = tk.Label(
                self.table_rows_frame,
                text=heading,
                width=width,
                bg="#d9e2ec",
                fg="#172b4d",
                font=("Segoe UI", 10, "bold"),
                relief=tk.SOLID,
                bd=1,
                padx=5,
                pady=8,
                anchor=tk.CENTER
            )
            header_cell.grid(row=0, column=col, sticky="nsew")
            self.table_rows_frame.grid_columnconfigure(col, weight=1)

    def add_expense(self):
        date_str = self.date_entry.get().strip()
        category = self.category_cb.get().strip()
        amount_str = self.amount_entry.get().strip()
        description = self.desc_entry.get().strip()

        # Validate Date
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid date in YYYY-MM-DD format.")
            return

        # Validate Amount
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive number for Amount.")
            return

        if not description:
            description = "-"

        self.data_manager.add_expense(date_str, category, amount, description)
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.refresh_ui()

    def delete_selected(self):
        if self.selected_row_index is None:
            messagebox.showwarning(
                "Selection Required",
                "Please click an expense row in the table before deleting it."
            )
            return

        if self.data_manager.delete_expense(self.selected_row_index):
            self.selected_row_index = None
            self.refresh_ui()

    def select_table_row(self, row_index):
        """Highlight a table row so it can be deleted if needed."""
        self.selected_row_index = row_index
        df = self.data_manager.load_data()
        for widget in self.table_rows_frame.winfo_children():
            grid_row = int(widget.grid_info().get("row", 0))
            if grid_row == 0:
                continue
            bg = "#cfe2ff" if grid_row == row_index + 1 else "#ffffff"
            widget.configure(bg=bg)

    def refresh_ui(self):
        # Rebuild the bordered table cells from the current CSV data.
        for widget in self.table_rows_frame.winfo_children():
            if int(widget.grid_info().get("row", 0)) > 0:
                widget.destroy()
        self.selected_row_index = None

        # Load data via Pandas
        df = self.data_manager.load_data()
        for idx, row in df.iterrows():
            values = (
                str(idx + 1),
                str(row["Date"]),
                str(row["Category"]),
                f"{float(row['Amount']):,.2f}",
                str(row["Description"])
            )
            for col, (value, width) in enumerate(zip(values, self.table_widths)):
                cell = tk.Label(
                    self.table_rows_frame,
                    text=value,
                    width=width,
                    bg="#ffffff",
                    fg="#222222",
                    font=("Segoe UI", 10),
                    relief=tk.SOLID,
                    bd=1,
                    padx=5,
                    pady=7,
                    anchor=tk.CENTER if col in (0, 1, 3) else tk.W
                )
                cell.grid(row=idx + 1, column=col, sticky="nsew")
                cell.bind(
                    "<Button-1>",
                    lambda event, row_index=idx: self.select_table_row(row_index)
                )

        # Update NumPy statistics
        stats = self.data_manager.get_statistics()
        stats_text = (
            f"Total Spent : {stats['total']:.2f}\n"
            f"Average     : {stats['mean']:.2f}\n"
            f"Highest     : {stats['max']:.2f}\n"
            f"Lowest      : {stats['min']:.2f}\n"
            f"Std Dev     : {stats['std']:.2f}"
        )
        self.stats_label.config(text=stats_text)

    def show_visualizations(self):
        df = self.data_manager.load_data()
        if df.empty:
            messagebox.showinfo("No Data", "Add some expenses first to generate visualizations.")
            return

        # Create popup window for Matplotlib graphs
        chart_win = tk.Toplevel(self.root)
        chart_win.title("ExpenseEase – Analytics & Visualizations")
        chart_win.geometry("900x450")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=100)
        fig.patch.set_facecolor("#f4f6f9")

        # 1. Category-wise Pie Chart (Pandas groupby)
        cat_totals = df.groupby("Category")["Amount"].sum()
        ax1.pie(
            cat_totals, labels=cat_totals.index, autopct="%1.1f%%",
            startangle=140, colors=plt.cm.Paired.colors
        )
        ax1.set_title("Expenses by Category", fontsize=12, fontweight="bold")

        # 2. Daily Spending Trend Bar Chart
        daily_totals = df.groupby("Date")["Amount"].sum().tail(10)
        ax2.bar(daily_totals.index, daily_totals.values, color="#2b4c7e", width=0.5)
        ax2.set_title("Recent Daily Spending", fontsize=12, fontweight="bold")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Total Amount")
        ax2.tick_params(axis="x", rotation=45)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseEaseApp(root)
    root.mainloop()