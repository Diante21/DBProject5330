from tkinter import Toplevel, Label, Entry, Button, messagebox, StringVar, OptionMenu
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

# Establish connection to database
def connect_db():
    config = read_db_config()
    return mysql.connector.connect(**config)

# Get the mapping between spaceports and planets
def get_spaceport_planet_map():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT spaceport_id, planet_id FROM spaceport")
    mapping = dict(cursor.fetchall())
    cursor.close()
    conn.close()
    return mapping

# Launch main flight creation window
def show_window():
    win = Toplevel()
    win.title("New Flight Creator")
    win.geometry("400x600")

    # Fetch all spaceports
    conn1 = connect_db()
    cursor1 = conn1.cursor()
    cursor1.execute("SELECT spaceport_id, name FROM spaceport")
    ports = cursor1.fetchall()
    cursor1.close()
    conn1.close()

    port_map = {f"{name} (ID:{pid})": pid for pid, name in ports}
    origin_var = StringVar()
    dest_var = StringVar()

    Label(win, text="Step 1: Select Origin and Destination").pack(pady=10)
    OptionMenu(win, origin_var, *port_map.keys()).pack()
    OptionMenu(win, dest_var, *port_map.keys()).pack()

    # Step 1: validation and route check
    def step1_continue():
        if not origin_var.get() or not dest_var.get():
            messagebox.showerror("Error", "Please select both origin and destination.")
            return

        oid = port_map[origin_var.get()]
        did = port_map[dest_var.get()]
        if oid == did:
            messagebox.showerror("Error", "Origin and destination cannot be the same.")
            return

        # Check if both ports are on the same planet
        planet_map = get_spaceport_planet_map()
        if planet_map.get(oid) and planet_map.get(oid) == planet_map.get(did):
            messagebox.showerror("Error", "No flights allowed between ports on the same planet.")
            return

        conn2 = connect_db()
        cursor2 = conn2.cursor(buffered=True)
        cursor2.execute("SELECT route_id, distance FROM route WHERE origin_spaceport_id=%s AND destination_spaceport_id=%s", (oid, did))
        route = cursor2.fetchone()

        # If route does not exist, prompt for distance and insert new route
        if not route:
            from tkinter.simpledialog import askinteger
            dist = askinteger("New Route", "Enter distance between ports:")
            if not dist or dist <= 0:
                messagebox.showerror("Error", "Distance must be a positive integer.")
                return
            cursor2.execute("INSERT INTO route (origin_spaceport_id, destination_spaceport_id, distance) VALUES (%s, %s, %s)", (oid, did, dist))
            conn2.commit()
            cursor2.execute("SELECT LAST_INSERT_ID()")
            route_id = cursor2.fetchone()[0]
            distance = dist
        else:
            route_id = route[0]
            distance = route[1]

        cursor2.close()
        conn2.close()
        step2(route_id, distance)

    Button(win, text="Next Step", command=step1_continue).pack(pady=10)

    # Step 2: select valid spacecraft
    def step2(route_id, distance):
        win2 = Toplevel(win)
        win2.title("Step 2: Choose Spacecraft")
        conn3 = connect_db()
        cursor3 = conn3.cursor()
        cursor3.execute("SELECT craft_type_id, type_name, `range` FROM spacecraft_type WHERE `range` >= %s", (distance,))
        options = cursor3.fetchall()
        cursor3.close()
        conn3.close()

        if not options:
            messagebox.showerror("Error", "No spacecraft can cover this distance.")
            win2.destroy()
            return

        craft_map = {f"{name} (ID:{cid}, Range: {r})": cid for cid, name, r in options}
        craft_var = StringVar()
        Label(win2, text="Select spacecraft:").pack(pady=5)
        OptionMenu(win2, craft_var, *craft_map.keys()).pack()

        def confirm():
            if not craft_var.get():
                messagebox.showerror("Error", "Please select a spacecraft.")
                return
            craft_id = craft_map[craft_var.get()]
            win2.destroy()
            step3(route_id, craft_id)

        Button(win2, text="Next Step", command=confirm).pack(pady=10)

    # Step 3: enter and insert flight info
    def step3(route_id, craft_id):
        win3 = Toplevel(win)
        win3.title("Step 3: Create Flight")

        Label(win3, text="Flight Number:").pack()
        entry_num = Entry(win3)
        entry_num.pack()

        Label(win3, text="Departure Time (HH:MM:SS):").pack()
        entry_dep = Entry(win3)
        entry_dep.pack()

        Label(win3, text="Flight Time (decimal hrs):").pack()
        entry_time = Entry(win3)
        entry_time.pack()

        def create_flight():
            try:
                num = entry_num.get().strip()
                dep = entry_dep.get().strip()
                dur = float(entry_time.get().strip())
                if not num or not dep or dur <= 0:
                    messagebox.showerror("Error", "All fields required and duration > 0.")
                    return
                conn4 = connect_db()
                cursor4 = conn4.cursor()
                cursor4.execute(
                    "INSERT INTO flight (flight_number, route_id, craft_type_id, departure_time, flight_time) VALUES (%s, %s, %s, %s, %s)",
                    (num, route_id, craft_id, dep, dur)
                )
                conn4.commit()
                cursor4.close()
                conn4.close()
                messagebox.showinfo("Success", "Flight created successfully.")
                win3.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        Button(win3, text="Create Flight", command=create_flight).pack(pady=10)

    win.protocol("WM_DELETE_WINDOW", win.destroy)

# Entry point
if __name__ == "__main__":
    from tkinter import Tk
    root = Tk()
    root.withdraw()
    show_window()
    root.mainloop()
