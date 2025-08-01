
from tkinter import Toplevel, Label, Entry, Button, messagebox, StringVar
from tkinter.ttk import Combobox
import mysql.connector
import os

# Read DB config
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

# Connect to DB
def connect_db():
    config = read_db_config()
    return mysql.connector.connect(**config)

# Fetch all flights for dropdown
def fetch_flights():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT flight_number FROM flight")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return [row[0] for row in result]
    except:
        return []

# Insert into flight_schedule table
def insert_schedule(flight_number, day_of_week):
    if not flight_number or not day_of_week:
        messagebox.showerror("Input Error", "Flight and day of week are required.")
        return
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO flight_schedule (flight_number, day_of_week) VALUES (%s, %s)",
            (flight_number, day_of_week)
        )
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", f"Flight schedule for '{flight_number}' on {day_of_week} added.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Insertion failed: {e}")

# GUI window
def show_window():
    win = Toplevel()
    win.title("Add Flight Schedule")
    win.geometry("350x260")
    win.resizable(False, False)

    flight_list = fetch_flights()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    Label(win, text="Select Flight:").pack(pady=3)
    flight_var = StringVar()
    flight_box = Combobox(win, textvariable=flight_var, values=flight_list, width=30, state="readonly")
    flight_box.pack()

    Label(win, text="Select Day of Week:").pack(pady=3)
    day_var = StringVar()
    day_box = Combobox(win, textvariable=day_var, values=days, width=30, state="readonly")
    day_box.pack()

    def on_submit():
        insert_schedule(flight_var.get(), day_var.get())

    Button(win, text="Add Schedule", command=on_submit).pack(pady=10)
