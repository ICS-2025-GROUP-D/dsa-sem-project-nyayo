import sqlite3


def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    try:
        c.execute('''CREATE TABLE IF NOT EXISTS appointments
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT, age INTEGER, gender TEXT, 
                      location TEXT, scheduled_time TEXT, 
                      phone TEXT, is_emergency INTEGER DEFAULT 0)''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        try:
            c.execute("ALTER TABLE appointments ADD COLUMN is_emergency INTEGER DEFAULT 0")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Failed to alter table: {e}")

    conn.close()


def execute_query(query, params=()):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute(query, params)
        conn.commit()
        return c.lastrowid
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()


def fetch_query(query, params=()):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute(query, params)
        return c.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()