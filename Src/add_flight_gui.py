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

# Fetch all route IDs and info
def fetch_routes():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
                    SELECT 
                        r.route_id,
                        origin.name AS origin_name,
                        destination.name AS destination_name,
                        r.distance
                    FROM 
                        route r
                    JOIN 
                        spaceport origin ON r.origin_spaceport_id = origin.spaceport_id
                    JOIN 
                        spaceport destination ON r.destination_spaceport_id = destination.spaceport_id
                """
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except:
        return []

# Fetch all spacecraft types
def fetch_spacecrafts():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT craft_type_id, type_name FROM spacecraft_type")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except:
        return []

# Insert flight into database
def insert_flight(flight_number, route_id, craft_id, departure_time, flight_time, distance):
    if not flight_number or not route_id or not craft_id or not departure_time or not flight_time:
        messagebox.showerror("Input Error", "All fields are required.")
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Get spacecraft range
        cursor.execute("SELECT `range` FROM spacecraft_type WHERE craft_type_id = %s", (craft_id,))
        result = cursor.fetchone()
        if not result:
            raise ValueError("Invalid spacecraft type selected.")
        craft_range = result[0]

        if craft_range < distance:
            messagebox.showerror("Constraint Error", f"The selected spacecraft cannot travel {distance} km (range: {craft_range} km).")
            return

        cursor.execute(
            "INSERT INTO flight (flight_number, route_id, craft_type_id, departure_time, flight_time) VALUES (%s, %s, %s, %s, %s)",
            (flight_number, int(route_id), int(craft_id), departure_time, float(flight_time))
        )
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", f"Flight '{flight_number}' added successfully.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Insertion failed: {e}")
    except ValueError as ve:
        messagebox.showerror("Data Error", str(ve))

# GUI window
def show_window():
    win = Toplevel()
    win.title("Add Flight")
    win.geometry("420x350")
    win.resizable(False, False)

    routes = fetch_routes()
    crafts = fetch_spacecrafts()
    route_map = {f"Route {rid} (From {o} to {d}, {dist}km)": (rid, dist) for rid, o, d, dist in routes}
    craft_map = {f"{name} (ID:{cid})": cid for cid, name in crafts}

    Label(win, text="Flight Number (Unique):").pack(pady=3)
    entry_number = Entry(win, width=35)
    entry_number.pack()

    Label(win, text="Select Route:").pack(pady=3)
    route_var = StringVar()
    route_box = Combobox(win, textvariable=route_var, values=list(route_map.keys()), width=34, state="readonly")
    route_box.pack()

    Label(win, text="Select Spacecraft Type:").pack(pady=3)
    craft_var = StringVar()
    craft_box = Combobox(win, textvariable=craft_var, values=list(craft_map.keys()), width=34, state="readonly")
    craft_box.pack()

    Label(win, text="Departure Time (HH:MM:SS):").pack(pady=3)
    entry_depart = Entry(win, width=35)
    entry_depart.pack()

    Label(win, text="Flight Time (decimal hours):").pack(pady=3)
    entry_time = Entry(win, width=35)
    entry_time.pack()

    def on_submit():
        flight_number = entry_number.get().strip()
        route_info = route_map.get(route_var.get())
        craft_id = craft_map.get(craft_var.get())
        departure_time = entry_depart.get().strip()
        flight_time = entry_time.get().strip()

        if route_info:
            route_id, distance = route_info
        else:
            messagebox.showerror("Selection Error", "Please select a valid route.")
            return

        insert_flight(flight_number, route_id, craft_id, departure_time, flight_time, distance)
        entry_number.delete(0, 'end')
        entry_depart.delete(0, 'end')
        entry_time.delete(0, 'end')

    Button(win, text="Add Flight", command=on_submit).pack(pady=10)
