from tkinter import Toplevel, Label, Entry, Button, messagebox, StringVar
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

def insert_station(name, location_type, planet_id, orbiting_id):
    if not name or not location_type or not planet_id:
        messagebox.showerror("Input Error", "Name, location type and owner planet are required.")
        return

    if location_type == "orbit" and orbiting_id is None:
        messagebox.showerror("Input Error", "Orbiting planet must be selected for 'orbit' type.")
        return

    if location_type == "space":
        orbiting_id = None

    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO spacestation (name, location_type, planet_id, orbiting_planet_id) VALUES (%s, %s, %s, %s)",
            (name, location_type, int(planet_id), int(orbiting_id) if orbiting_id else None)
        )
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", f"SpaceStation '{name}' added successfully.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Insertion failed: {e}")

def show_window():
    win = Toplevel()
    win.title("Add SpaceStation")
    win.geometry("400x360")
    win.resizable(False, False)

    planets = fetch_planets()
    planet_map = {f"{name} (ID:{pid})": pid for pid, name in planets}
    planet_options = list(planet_map.keys())

    orbit_options = ["--- None ---"] + planet_options
    orbit_map = {"--- None ---": None}
    orbit_map.update(planet_map)

    Label(win, text="Station Name:").pack(pady=3)
    entry_name = Entry(win, width=35)
    entry_name.pack()

    Label(win, text="Location Type:").pack(pady=3)
    location_var = StringVar()
    location_box = Combobox(win, textvariable=location_var, values=["orbit", "space"], state="readonly", width=32)
    location_box.pack()
    location_box.set("orbit")

    Label(win, text="Owner Planet:").pack(pady=3)
    planet_var = StringVar()
    planet_box = Combobox(win, textvariable=planet_var, values=planet_options, state="readonly", width=32)
    planet_box.pack()

    Label(win, text="Orbiting Planet (only for orbit):").pack(pady=3)
    orbit_var = StringVar()
    orbit_box = Combobox(win, textvariable=orbit_var, values=orbit_options, state="readonly", width=32)
    orbit_box.pack()
    orbit_box.set("--- None ---")

    # Automatically disable/enable orbit dropdown based on type
    def on_location_change(event):
        if location_var.get() == "space":
            orbit_box.set("--- None ---")
            orbit_box.config(state="disabled")
        else:
            orbit_box.config(state="readonly")

    location_box.bind("<<ComboboxSelected>>", on_location_change)
    on_location_change(None)  # Initial check

    def on_submit():
        name = entry_name.get().strip()
        location_type = location_var.get().strip().lower()
        owner_id = planet_map.get(planet_var.get())
        orbiting_id = orbit_map.get(orbit_var.get())

        insert_station(name, location_type, owner_id, orbiting_id)

        entry_name.delete(0, 'end')
        location_box.set("orbit")
        orbit_box.set("--- None ---")
        orbit_box.config(state="readonly")

    Button(win, text="Add SpaceStation", command=on_submit).pack(pady=15)
