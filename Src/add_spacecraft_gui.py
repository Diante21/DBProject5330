from tkinter import Toplevel, Label, Entry, Button, messagebox
import mysql.connector
import os

# Read DB config from file
def read_db_config(filename='db_config.txt'):
    base_dir = os.path.dirname(__file__)
    full_path = os.path.join(base_dir, filename)
    config = {}
    with open(full_path, 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                config[key.strip()] = value.strip()
    config['port'] = int(config.get('port', 3306))
    return config

# Connect to MySQL
def connect_db():
    config = read_db_config()
    return mysql.connector.connect(**config)

# Insert a spacecraft type into the database
def insert_spacecraft(type_name, capacity, max_range):
    if not type_name or not capacity or not max_range:
        messagebox.showerror("Input Error", "All fields are required.")
        return

    if not capacity.isdigit() or not max_range.isdigit():
        messagebox.showerror("Input Error", "Capacity and range must be positive integers.")
        return

    capacity = int(capacity)
    max_range = int(max_range)

    if capacity <= 0 or max_range <= 0:
        messagebox.showerror("Input Error", "Capacity and range must be greater than 0.")
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()
        # Check if the type name already exists
        cursor.execute("SELECT COUNT(*) FROM spacecraft_type WHERE type_name = %s", (type_name,))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Input Error", f"Type name '{type_name}' already exists.")
            cursor.close()
            conn.close()
            return

        # INSERT with `range` escaped properly
        cursor.execute(
            "INSERT INTO spacecraft_type (type_name, capacity, `range`) VALUES (%s, %s, %s)",
            (type_name, capacity, max_range)
        )
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", f"Spacecraft Type '{type_name}' added successfully.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Insertion failed: {e}")

# GUI window for adding spacecraft
def show_window():
    win = Toplevel()
    win.title("Add Spacecraft Type")
    win.geometry("380x260")
    win.resizable(False, False)

    Label(win, text="Type Name:").pack(pady=3)
    entry_name = Entry(win, width=35)
    entry_name.pack()

    Label(win, text="Capacity (Integer > 0):").pack(pady=3)
    entry_capacity = Entry(win, width=35)
    entry_capacity.pack()

    Label(win, text="Range (Integer > 0):").pack(pady=3)
    entry_range = Entry(win, width=35)
    entry_range.pack()

    def on_submit():
        type_name = entry_name.get().strip()
        capacity = entry_capacity.get().strip()
        max_range = entry_range.get().strip()
        insert_spacecraft(type_name, capacity, max_range)
        entry_name.delete(0, 'end')
        entry_capacity.delete(0, 'end')
        entry_range.delete(0, 'end')

    Button(win, text="Add Spacecraft", command=on_submit).pack(pady=10)
