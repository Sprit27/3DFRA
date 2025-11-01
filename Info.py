import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("info1.db")
cursor = conn.cursor()

# Create the table
def create_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            unique_number INTEGER UNIQUE NOT NULL
        )
    """)
    conn.commit()

# Function to add a name and unique number to the table
def add_entry(name, unique_number):
    try:
        cursor.execute("INSERT INTO people (name, unique_number) VALUES (?, ?)", (name, unique_number))
        conn.commit()
        print(f"Added: {name} with unique number {unique_number}")
    except sqlite3.IntegrityError as e:
        print(f"Error: {e}")

# Main execution
if __name__ == "__main__":
    create_table()  # Ensure the table is created

    # Add some entries
    #add_entry("Alice", 101)
    #dd_entry("Bob", 102)

    # Trying to add duplicate unique numbers
    #add_entry("Charlie", 102)  # This will raise an IntegrityError
    #add_entry("Diana", 103)
