
from tkinter import Toplevel, Label, Button, messagebox, StringVar, Text
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

# Fetch all routes
def fetch_routes():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT r.route_id, sp1.name, sp2.name FROM route r JOIN spaceport sp1 ON r.origin_spaceport_id = sp1.spaceport_id JOIN spaceport sp2 ON r.destination_spaceport_id = sp2.spaceport_id")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return {f"Route {rid}: {src} -> {dst}": rid for rid, src, dst in result}
    except:
        return {}

# Fetch flights on a specific route
def query_flights_by_route(route_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.flight_number, s.type_name, f.departure_time, f.flight_time
            FROM flight f
            JOIN spacecraft_type s ON f.craft_type_id = s.craft_type_id
            WHERE f.route_id = %s
        """, (route_id,))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Query failed: {e}")
        return []

# GUI
def show_window():
    win = Toplevel()
    win.title("Query Route")
    win.geometry("580x400")
    win.resizable(False, False)

    route_map = fetch_routes()

    Label(win, text="Select Route:").pack(pady=3)
    route_var = StringVar()
    route_box = Combobox(win, textvariable=route_var, values=list(route_map.keys()), width=60, state="readonly")
    route_box.pack()

    result_area = Text(win, width=70, height=18)
    result_area.pack(pady=10)

    def on_query():
        result_area.delete("1.0", "end")
        selected = route_var.get()
        if not selected:
            messagebox.showerror("Input Error", "Please select a route.")
            return
        route_id = route_map[selected]
        flights = query_flights_by_route(route_id)
        if not flights:
            result_area.insert("end", "No flights found on this route.")
        else:
            for flight_number, craft_type, dep_time, duration in flights:
                result_area.insert("end", f"- Flight {flight_number} | Spacecraft: {craft_type} | Departure: {dep_time} | Duration: {duration} hrs\n")

    Button(win, text="Run Query", command=on_query).pack(pady=5)
