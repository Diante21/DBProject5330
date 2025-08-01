from tkinter import Toplevel, Label, Entry, Button, messagebox, StringVar, Radiobutton, IntVar, DISABLED, NORMAL
from tkinter.ttk import Combobox
import mysql.connector
import os

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

def connect_db():
    config = read_db_config()
    return mysql.connector.connect(**config)

def fetch_planets():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT planet_id, name FROM planet")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except:
        return []

def fetch_stations():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.station_id, s.name FROM spacestation s
            LEFT JOIN spaceport p ON s.station_id = p.station_id
            WHERE p.station_id IS NULL
        """)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except:
        return []

def insert_spaceport(name, capacity, fee, planet_id, station_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Check if name already exists on same planet
        if planet_id:
            cursor.execute(
                "SELECT COUNT(*) FROM spaceport WHERE name = %s AND planet_id = %s",
                (name, planet_id)
            )
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Input Error", f"A spaceport named '{name}' already exists on this planet.")
                cursor.close()
                conn.close()
                return

        cursor.execute(
            "INSERT INTO spaceport (name, capacity_limit, fee_per_seat, planet_id, station_id) VALUES (%s, %s, %s, %s, %s)",
            (name, capacity, fee, planet_id, station_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", f"Spaceport '{name}' added successfully.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Insertion failed: {e}")

def show_window():
    win = Toplevel()
    win.title("Add Spaceport")
    win.geometry("420x420")
    win.resizable(False, False)

    planets = fetch_planets()
    stations = fetch_stations()
    planet_map = {f"{name} (ID:{pid})": pid for pid, name in planets}
    station_map = {f"{name} (ID:{sid})": sid for sid, name in stations}

    Label(win, text="Ownership Type:").pack()
    mode = IntVar()
    mode.set(1)

    def on_mode_change():
        if mode.get() == 1:
            entry_name.config(state=NORMAL)
            planet_box.config(state="readonly")
            station_box.set("")
            station_box.config(state=DISABLED)
        else:
            entry_name.delete(0, 'end')
            entry_name.config(state=DISABLED)
            planet_box.set("")
            planet_box.config(state=DISABLED)
            station_box.config(state="readonly")

    Radiobutton(win, text="Planet", variable=mode, value=1, command=on_mode_change).pack()
    Radiobutton(win, text="SpaceStation", variable=mode, value=2, command=on_mode_change).pack()

    Label(win, text="Spaceport Name:").pack(pady=2)
    entry_name = Entry(win, width=35)
    entry_name.pack()

    Label(win, text="Capacity Limit (Integer > 0):").pack(pady=2)
    entry_capacity = Entry(win, width=35)
    entry_capacity.pack()

    Label(win, text="Fee per Seat (Integer ≥ 0):").pack(pady=2)
    entry_fee = Entry(win, width=35)
    entry_fee.pack()

    Label(win, text="Select Planet:").pack(pady=2)
    planet_var = StringVar()
    planet_box = Combobox(win, textvariable=planet_var, values=list(planet_map.keys()), state="readonly", width=32)
    planet_box.pack()

    Label(win, text="Select SpaceStation:").pack(pady=2)
    station_var = StringVar()
    station_box = Combobox(win, textvariable=station_var, values=list(station_map.keys()), state=DISABLED, width=32)
    station_box.pack()

    def on_submit():
        cap = entry_capacity.get().strip()
        fee = entry_fee.get().strip()

        if not cap.isdigit() or int(cap) <= 0:
            messagebox.showerror("Input Error", "Capacity must be a positive integer.")
            return
        if not fee.isdigit() or int(fee) < 0:
            messagebox.showerror("Input Error", "Fee must be a non-negative integer.")
            return

        capacity = int(cap)
        fee = int(fee)

        if mode.get() == 1:
            pname = planet_var.get()
            if not pname:
                messagebox.showerror("Input Error", "Please select a planet.")
                return
            name = entry_name.get().strip()
            if not name:
                messagebox.showerror("Input Error", "Please enter a spaceport name.")
                return
            insert_spaceport(name, capacity, fee, planet_map[pname], None)
        else:
            sname = station_var.get()
            if not sname:
                messagebox.showerror("Input Error", "Please select a space station.")
                return
            sid = station_map[sname]
            name = sname.split(" (ID")[0]
            insert_spaceport(name, capacity, fee, None, sid)

        entry_name.config(state=NORMAL)
        entry_name.delete(0, 'end')
        entry_capacity.delete(0, 'end')
        entry_fee.delete(0, 'end')
        planet_box.set("")
        station_box.set("")
        on_mode_change()

    Button(win, text="Add Spaceport", command=on_submit).pack(pady=12)
    on_mode_change()
