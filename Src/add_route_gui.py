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

# Fetch all spaceports
def fetch_spaceports():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT spaceport_id, name FROM spaceport")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except:
        return []

# Insert route
def insert_route(origin_id, destination_id, distance_str):
    if not origin_id or not destination_id or not distance_str:
        messagebox.showerror("Input Error", "All fields are required.")
        return

    if origin_id == destination_id:
        messagebox.showerror("Input Error", "Origin and destination cannot be the same.")
        return

    if not distance_str.isdigit() or int(distance_str) <= 0:
        messagebox.showerror("Input Error", "Distance must be a positive integer.")
        return

    distance = int(distance_str)

    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Check if both spaceports are on the same planet
        cursor.execute("""
            SELECT p1.planet_id, p2.planet_id
            FROM spaceport p1, spaceport p2
            WHERE p1.spaceport_id = %s AND p2.spaceport_id = %s
        """, (origin_id, destination_id))
        pid1, pid2 = cursor.fetchone()
        if pid1 is not None and pid2 is not None and pid1 == pid2:
            messagebox.showerror("Constraint Error", "Cannot create a route between spaceports on the same planet.")
            conn.close()
            return

        # Insert the route
        cursor.execute(
            "INSERT INTO route (origin_spaceport_id, destination_spaceport_id, distance) VALUES (%s, %s, %s)",
            (origin_id, destination_id, distance)
        )
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", "Route added successfully.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Insertion failed: {e}")

# GUI window
def show_window():
    win = Toplevel()
    win.title("Add Route")
    win.geometry("400x280")
    win.resizable(False, False)

    ports = fetch_spaceports()
    port_map = {f"{name} (ID:{pid})": pid for pid, name in ports}
    options = list(port_map.keys())

    Label(win, text="Select Origin Spaceport:").pack(pady=3)
    origin_var = StringVar()
    origin_box = Combobox(win, textvariable=origin_var, values=options, width=32, state="readonly")
    origin_box.pack()

    Label(win, text="Select Destination Spaceport:").pack(pady=3)
    dest_var = StringVar()
    dest_box = Combobox(win, textvariable=dest_var, values=options, width=32, state="readonly")
    dest_box.pack()

    Label(win, text="Distance (in km):").pack(pady=3)
    entry_distance = Entry(win, width=35)
    entry_distance.pack()

    def on_submit():
        origin_id = port_map.get(origin_var.get())
        destination_id = port_map.get(dest_var.get())
        distance = entry_distance.get().strip()
        insert_route(origin_id, destination_id, distance)
        entry_distance.delete(0, 'end')

    Button(win, text="Add Route", command=on_submit).pack(pady=10)
