from tkinter import Toplevel, Label, Entry, Button, messagebox
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

# Connect to database
def connect_db():
    config = read_db_config()
    return mysql.connector.connect(**config)

# Insert planet with basic constraints
def insert_planet(name, size, population):
    if not name:
        messagebox.showerror("Input Error", "Planet name cannot be empty.")
        return
    if not size.isdigit() or not population.isdigit():
        messagebox.showerror("Input Error", "Size and population must be integers.")
        return

    size = int(size)
    population = int(population)

    if size <= 0:
        messagebox.showerror("Input Error", "Size must be greater than 0.")
        return
    if population < 0:
        messagebox.showerror("Input Error", "Population cannot be negative.")
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO planet (name, size, population) VALUES (%s, %s, %s)",
            (name, size, population)
        )
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", f"Planet '{name}' added successfully.")
    except mysql.connector.IntegrityError as e:
        messagebox.showerror("Database Error", f"Planet name must be unique.\n{e}")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Insertion failed: {e}")

# Show GUI window
def show_window():
    win = Toplevel()
    win.title("Add Planet")
    win.geometry("300x220")
    win.resizable(False, False)

    Label(win, text="Planet Name:").pack(pady=3)
    entry_name = Entry(win, width=30)
    entry_name.pack()

    Label(win, text="Size (Integer > 0):").pack(pady=3)
    entry_size = Entry(win, width=30)
    entry_size.pack()

    Label(win, text="Population (Integer ≥ 0):").pack(pady=3)
    entry_population = Entry(win, width=30)
    entry_population.pack()

    def on_submit():
        insert_planet(entry_name.get().strip(), entry_size.get().strip(), entry_population.get().strip())
        entry_name.delete(0, 'end')
        entry_size.delete(0, 'end')
        entry_population.delete(0, 'end')

    Button(win, text="Add Planet", command=on_submit).pack(pady=10)
