from tkinter import Toplevel, Label, Entry, Button, messagebox, StringVar, Text
from tkinter.ttk import Combobox
import mysql.connector
import os
from datetime import datetime, timedelta

# Read database configuration
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

# Connect to database
def connect_db():
    config = read_db_config()
    return mysql.connector.connect(**config)

# Fetch all spaceports for dropdowns
def fetch_spaceports():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT spaceport_id, name FROM spaceport")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return {f"{name} (ID:{sid})": sid for sid, name in result}

    except Exception as e:
        print("Fetch spaceports error:", e)
        return {}

# Recursively search for flight paths
def search_paths(current_port, destination_port, day, earliest_time_str, max_stops, max_time, path=[], total_time=0.0, is_first_leg=True):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    itineraries = []
    visited_flights = set(f['flight_number'] for f in path)

    # Parse time for this leg
    try:
        time_obj = datetime.strptime(earliest_time_str, "%H:%M:%S").time()
    except:
        cursor.close()
        conn.close()
        return []

    # First leg: restrict to departures within 3 hours from user time
    latest_first_leg = (datetime.combine(datetime.today(), time_obj) + timedelta(hours=3)).time()

    # Query for eligible flights
    cursor.execute("""
        SELECT f.*, s.type_name, r.origin_spaceport_id, r.destination_spaceport_id
        FROM flight f
        JOIN flight_schedule fs ON f.flight_number = fs.flight_number
        JOIN route r ON f.route_id = r.route_id
        JOIN spacecraft_type s ON f.craft_type_id = s.craft_type_id
        WHERE fs.day_of_week = %s AND r.origin_spaceport_id = %s
    """, (day, current_port))

    for flight in cursor.fetchall():
        if flight['flight_number'] in visited_flights:
            continue

        dep_time = datetime.strptime(str(flight['departure_time']), "%H:%M:%S").time()

        # First leg: restrict departure window (on or after user's earliest, up to +3 hours)
        if is_first_leg:
            if not (time_obj <= dep_time <= latest_first_leg):
                continue
        # Transfers: restrict layover (1hr to 6hr after arrival at stop)
        else:
            prev_flight = path[-1]
            prev_dep = datetime.strptime(str(prev_flight['departure_time']), "%H:%M:%S")
            prev_arrival = prev_dep + timedelta(hours=float(prev_flight['flight_time']))
            earliest_dep = (prev_arrival + timedelta(hours=1)).time()
            latest_dep = (prev_arrival + timedelta(hours=6)).time()
            # Compare time intervals. Handles overnight by requiring next flight same day (for now)
            if not (earliest_dep <= dep_time <= latest_dep):
                continue

        # Calculate total trip time so far
        this_leg_time = float(flight['flight_time'])
        # Add 1 hour per stop (not for first leg)
        if not is_first_leg:
            this_leg_time += 1.0
        new_total_time = total_time + this_leg_time
        if new_total_time > float(max_time):
            continue

        new_path = path + [flight]
        # If destination reached, save the itinerary
        if flight['destination_spaceport_id'] == destination_port:
            itineraries.append(new_path)
        # If more stops allowed, continue searching
        elif max_stops > 0:
            # Next leg can depart no earlier than this arrival + 1hr
            next_earliest_time = (datetime.strptime(str(flight['departure_time']), "%H:%M:%S") + timedelta(hours=float(flight['flight_time']) + 1)).time()
            itineraries.extend(
                search_paths(
                    flight['destination_spaceport_id'],
                    destination_port,
                    day,
                    next_earliest_time.strftime("%H:%M:%S"),
                    max_stops - 1,
                    max_time,
                    new_path,
                    new_total_time,
                    is_first_leg=False
                )
            )

    cursor.close()
    conn.close()
    return itineraries

# Main GUI window
def show_window():
    win = Toplevel()
    win.title("Flight Finder (Path Planning)")
    win.geometry("750x600")
    win.resizable(False, False)

    ports = fetch_spaceports()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    Label(win, text="Origin Spaceport:").pack()
    origin_var = StringVar()
    Combobox(win, textvariable=origin_var, values=list(ports.keys()), width=60, state="readonly").pack()

    Label(win, text="Destination Spaceport:").pack()
    dest_var = StringVar()
    Combobox(win, textvariable=dest_var, values=list(ports.keys()), width=60, state="readonly").pack()

    Label(win, text="Day of Week:").pack()
    day_var = StringVar()
    Combobox(win, textvariable=day_var, values=days, width=30, state="readonly").pack()

    Label(win, text="Earliest Departure Time (HH:MM:SS):").pack()
    entry_time = Entry(win, width=30)
    entry_time.pack()

    Label(win, text="Max Stops (0 for direct only):").pack()
    entry_stops = Entry(win, width=30)
    entry_stops.pack()

    Label(win, text="Max Total Travel Time (hours):").pack()
    entry_max_time = Entry(win, width=30)
    entry_max_time.pack()

    result_area = Text(win, width=85, height=18)
    result_area.pack(pady=10)

    def on_search():
        spaceport_names = fetch_spaceports()
        print(spaceport_names)
        result_area.delete("1.0", "end")
        o = origin_var.get()
        d = dest_var.get()
        if not o or not d or o == d:
            messagebox.showerror("Input Error", "Please select different origin and destination.")
            return
        try:
            earliest = entry_time.get().strip()
            datetime.strptime(earliest, "%H:%M:%S")
            max_stops = int(entry_stops.get().strip())
            max_time = float(entry_max_time.get().strip())
            if max_stops < 0 or max_time < 0:
                raise ValueError("Stops and time must be non-negative.")

            routes = search_paths(ports[o], ports[d], day_var.get(), earliest, max_stops, max_time)
            if not routes:
                result_area.insert("end", "No available routes found.\n")
            else:
                for idx, route in enumerate(routes, 1):
                    total_time = 0.0
                    route_text = []
                    for i, f in enumerate(route):
                        seg_time = float(f['flight_time']) + (1.0 if i > 0 else 0.0)
                        total_time += seg_time
                        origin_name = spaceport_names.get(f['origin_spaceport_id'], f['origin_spaceport_id'])
                        dest_name = spaceport_names.get(f['destination_spaceport_id'], f['destination_spaceport_id'])
                        print(origin_name, dest_name)
                        route_text.append(
                            f"  Leg {i + 1}: Flight {f['flight_number']} from {origin_name} to {dest_name} | "
                            f"Dep: {f['departure_time']} | Duration: {f['flight_time']} hrs | Spacecraft: {f['type_name']}"
                        )

                    result_area.insert("end", f"Itinerary {idx} (Total Legs: {len(route)}; Total Time: {total_time} hrs):\n")
                    for line in route_text:
                        result_area.insert("end", line + "\n")
                    result_area.insert("end", "\n")
        except Exception as e:
            messagebox.showerror("Search Error", str(e))

    Button(win, text="Find Route", command=on_search).pack(pady=5)
