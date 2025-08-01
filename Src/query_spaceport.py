
from tkinter import Toplevel, Label, Button, Text, Scrollbar, END, ttk, messagebox
import mysql.connector
import os

# Read database configuration from file
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

# Create a database connection
def connect_db():
    return mysql.connector.connect(**read_db_config())

# Execute spaceport query: return related spaceports and flight details
def query_spaceport_info(spaceport_id):
    conn = connect_db()
    cursor = conn.cursor()

    # Get related spaceports from route table
    cursor.execute(
        "SELECT DISTINCT sp.name "
        "FROM route r "
        "JOIN spaceport sp ON "
        "(r.origin_spaceport_id = %s AND r.destination_spaceport_id = sp.spaceport_id) "
        "OR (r.destination_spaceport_id = %s AND r.origin_spaceport_id = sp.spaceport_id)",
        (spaceport_id, spaceport_id)
    )
    related_ports = cursor.fetchall()

    # Get flights (inbound or outbound from this spaceport)
    cursor.execute(
        "SELECT f.flight_number, r.distance, s.type_name, f.departure_time, f.flight_time "
        "FROM flight f "
        "JOIN route r ON f.route_id = r.route_id "
        "JOIN spacecraft_type s ON f.craft_type_id = s.craft_type_id "
        "WHERE r.origin_spaceport_id = %s OR r.destination_spaceport_id = %s",
        (spaceport_id, spaceport_id)
    )
    flights = cursor.fetchall()

    cursor.close()
    conn.close()
    return related_ports, flights

# GUI window
def show_window():
    win = Toplevel()
    win.title("Query Spaceport Info")
    win.geometry("600x500")

    Label(win, text="Select Spaceport:").pack(pady=5)

    port_var = ttk.Combobox(win, state="readonly", width=50)
    port_var.pack(pady=5)

    port_map = {}

    # Load spaceports for dropdown
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT spaceport_id, name FROM spaceport")
        for sid, name in cursor.fetchall():
            label = f"{name} (ID:{sid})"
            port_map[label] = sid
            port_var['values'] = (*port_var['values'], label)
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return

    # Text area for results
    result_area = Text(win, wrap="word", height=20, width=70)
    result_area.pack(pady=10)
    scrollbar = Scrollbar(win, command=result_area.yview)
    scrollbar.pack(side="right", fill="y")
    result_area.config(yscrollcommand=scrollbar.set)

    # Query handler
    def on_query():
        result_area.delete("1.0", "end")
        selected = port_var.get()
        if not selected:
            messagebox.showerror("Input Error", "Please select a spaceport.")
            return
        sid = port_map[selected]
        related_ports, flights = query_spaceport_info(sid)
        result_area.insert("end", "Related Spaceports:\n")
        for (name,) in related_ports:
            result_area.insert("end", f" - {name}\n")
        result_area.insert("end", "\nFlights:\n")
        for flight_number, distance, craft_type, dep_time, duration in flights:
            result_area.insert(
                "end",
                f" - Flight {flight_number} | Distance: {distance} | Spacecraft: {craft_type} | "
                f"Departure: {dep_time} | Duration: {duration} hrs\n"
            )

    # Button to trigger query
    Button(win, text="Run Query", command=on_query).pack(pady=5)
