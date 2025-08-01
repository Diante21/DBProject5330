from tkinter import Tk, Button, Label

def open_add_planet():
    import add_planet_gui
    add_planet_gui.show_window()

def open_add_station():
    import add_station_gui
    add_station_gui.show_window()

def open_add_route():
    import add_route_gui
    add_route_gui.show_window()

def open_add_spaceport():
    import add_spaceport_gui
    add_spaceport_gui.show_window()

def open_add_spacecraft():
    import add_spacecraft_gui
    add_spacecraft_gui.show_window()

def open_add_flight():
    import add_flight_gui
    add_flight_gui.show_window()

def open_add_schedule():
    import add_schedule_gui
    add_schedule_gui.show_window()

def open_spaceport_query():
    import query_spaceport
    query_spaceport.show_window()

def open_route_query():
    import query_route
    query_route.show_window()

def open_flight_finder():
    import flight_finder
    flight_finder.show_window()

def open_new_flight_creator():
    import new_flight_creator
    new_flight_creator.show_window()
# Main GUI window
root = Tk()
root.title("Intergalactic Database System - Main Menu")
root.geometry("400x585")
root.resizable(False, False)

Label(root, text="Select a Function Module", font=("Arial", 14)).pack(pady=10)

Button(root, text="Add Planet", width=30, command=open_add_planet).pack(pady=5)
Button(root, text="Add SpaceStation", width=30, command=open_add_station).pack(pady=5)
Button(root, text="Add Spaceport", width=30, command=open_add_spaceport).pack(pady=5)
Button(root, text="Add route", width=30, command=open_add_route).pack(pady=5)
Button(root, text="Add Spacecraft", width=30, command=open_add_spacecraft).pack(pady=5)
Button(root, text="Add Flight", width=30, command=open_add_flight).pack(pady=5)
Button(root, text="Add FlightSchedule", width=30, command=open_add_schedule).pack(pady=5)
Button(root, text="extra Flight Creator", width=30, command=open_new_flight_creator).pack(pady=5)

Label(root, text="--- Query Functions ---", font=("Arial", 12)).pack(pady=10)
Button(root, text="Spaceport Query", width=30, command=open_spaceport_query).pack(pady=5)
Button(root, text="Route Query", width=30, command=open_route_query).pack(pady=5)
Button(root, text="Flight Finder", width=30, command=open_flight_finder).pack(pady=5)

Button(root, text="Exit", width=30, command=root.destroy).pack(pady=20)

root.mainloop()

