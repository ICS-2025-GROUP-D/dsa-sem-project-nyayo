from tkinter import *
import sqlite3
import tkinter.messagebox


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


# Initialize hash table
patient_hash = PatientHashTable()


class Application:
    def __init__(self, master):
        self.master = master
        self.current_index = 0
        self.patients = patient_hash.get_all_patients()

        # Window settings
        self.master.title("Patient Display System")
        self.master.geometry("1366x768")
        self.master.resizable(True, True)

        self.create_widgets()
        self.show_patient()

    def create_widgets(self):
        # Main container with padding
        self.main_frame = Frame(self.master, padx=20, pady=20)
        self.main_frame.pack(fill=BOTH, expand=True)

        # heading with proper spacing
        self.heading = Label(self.main_frame, text="Patient Display",
                             font=('arial 36 bold'), fg='green')
        self.heading.pack(pady=20)

        # Patient info display area
        self.info_frame = Frame(self.main_frame)
        self.info_frame.pack(fill=BOTH, expand=True, pady=20)

        # Patient details with better spacing
        self.labels = {}
        fields = [
            ('id', "Patient ID", 'arial 24 bold', 50, 50),
            ('name', "Name", 'arial 24 bold', 50, 120),
            ('details', "Details", 'arial 18 bold', 50, 200),
            ('time', "Appointment Time", 'arial 18 bold', 50, 280),
            ('emergency', "Status", 'arial 18 bold', 50, 350)
        ]

        for field, text, font, x, y in fields:
            Label(self.info_frame, text=text + ":", font=font, fg='black').place(x=x, y=y)
            self.labels[field] = Label(self.info_frame, text="", font=font, fg='blue')
            self.labels[field].place(x=x + 300, y=y)

        # Navigation buttons with better layout
        self.button_frame = Frame(self.main_frame)
        self.button_frame.pack(fill=X, pady=30)

        self.prev_btn = Button(self.button_frame, text="Previous Patient", width=20, height=2,
                               bg='steelblue', command=self.prev_patient)
        self.prev_btn.pack(side=LEFT, padx=20)

        self.next_btn = Button(self.button_frame, text="Next Patient", width=20, height=2,
                               bg='steelblue', command=self.next_patient)
        self.next_btn.pack(side=LEFT, padx=20)

        self.search_btn = Button(self.button_frame, text="Search by ID", width=20, height=2,
                                 bg='orange', command=self.search_patient)
        self.search_btn.pack(side=LEFT, padx=20)

    def show_patient(self):
        if not self.patients:
            for label in self.labels.values():
                label.config(text="No patients found")
            return

        if self.current_index >= len(self.patients):
            self.current_index = 0

        patient = self.patients[self.current_index]

        self.labels['id'].config(text=patient.get('id', 'N/A'))
        self.labels['name'].config(text=patient.get('name', 'N/A'))

        details = f"Age: {patient.get('age', 'N/A')} | Gender: {patient.get('gender', 'N/A')}\n"
        details += f"Location: {patient.get('location', 'N/A')} | Phone: {patient.get('phone', 'N/A')}"
        self.labels['details'].config(text=details)

        self.labels['time'].config(text=patient.get('time', 'N/A'))

        status = "EMERGENCY" if patient.get('is_emergency', False) else "Regular"
        color = "red" if patient.get('is_emergency', False) else "green"
        self.labels['emergency'].config(text=status, fg=color)

    def next_patient(self):
        if not self.patients:
            return

        if self.current_index < len(self.patients) - 1:
            self.current_index += 1
        else:
            self.current_index = 0
        self.show_patient()

    def prev_patient(self):
        if not self.patients:
            return

        if self.current_index > 0:
            self.current_index -= 1
        else:
            self.current_index = len(self.patients) - 1
        self.show_patient()

    def search_patient(self):
        search_window = Toplevel(self.master)
        search_window.title("Search Patient")
        search_window.geometry("400x200")

        Label(search_window, text="Enter Patient ID:", font=('arial 14')).pack(pady=20)
        id_entry = Entry(search_window, font=('arial 14'))
        id_entry.pack()

        def search():
            try:
                patient_id = int(id_entry.get())
                patient = patient_hash.get_patient(patient_id)
                if patient:
                    for i, p in enumerate(self.patients):
                        if p.get('id') == patient_id:
                            self.current_index = i
                            self.show_patient()
                            search_window.destroy()
                            return
                tkinter.messagebox.showerror("Error", "Patient ID not found")
            except ValueError:
                tkinter.messagebox.showerror("Error", "Please enter a valid numeric ID")

        Button(search_window, text="Search", command=search).pack(pady=20)


root = Tk()
b = Application(root)
root.mainloop()