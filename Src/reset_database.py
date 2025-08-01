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

# Execute data clearing and reset auto_increment
def reset_all_data():
    try:
        conn = mysql.connector.connect(**read_db_config())
        cursor = conn.cursor()
        print("🔄 Clearing all data and resetting AUTO_INCREMENT...")

        # Correct order for deletion due to foreign key dependencies
        deletion_order = [
            "flight_schedule",
            "flight",
            "route",
            "spaceport",
            "spacestation",
            "spacecraft_type",
            "planet"
        ]

        for table in deletion_order:
            try:
                cursor.execute(f"DELETE FROM {table}")
                cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
                print(f"✅ Cleared and reset: {table}")
            except mysql.connector.Error as err:
                print(f"❌ Error clearing {table}: {err}")

        conn.commit()
        cursor.close()
        conn.close()
        print("All data has been cleared and ID counters reset.")
    except mysql.connector.Error as err:
        print(f"❌ Database connection error: {err}")

if __name__ == "__main__":
    reset_all_data()
