import sqlite3

class PatientHashTable:
    def __init__(self):
        self.table = {}
        self.load_from_db()

    def load_from_db(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Check and fix table structure if needed
        c.execute("PRAGMA table_info(appointments)")
        columns = [col[1] for col in c.fetchall()]

        if 'is_emergency' not in columns:
            try:
                c.execute("ALTER TABLE appointments ADD COLUMN is_emergency INTEGER DEFAULT 0")
                conn.commit()
            except sqlite3.Error as e:
                print(f"Couldn't add is_emergency column: {e}")

        c.execute("SELECT * FROM appointments")
        for row in c.fetchall():
            patient_id = row[0]
            self.table[patient_id] = {
                'id': row[0],
                'name': row[1],
                'age': row[2],
                'gender': row[3],
                'location': row[4],
                'phone': row[5],
                'time': row[6],
                'is_emergency': bool(row[7]) if len(row) > 7 else False
            }
        conn.close()

    def get_patient(self, patient_id):
        return self.table.get(patient_id)

    def get_all_patients(self):
        return list(self.table.values())

    def update_patient(self, patient_id, updated_data):
        if patient_id in self.table:
            self.table[patient_id].update(updated_data)
            return True
        return False

    def delete_patient(self, patient_id):
        return self.table.pop(patient_id, None) is not None

    def __len__(self):
        return len(self.table)