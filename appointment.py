from tkinter import *
import sqlite3
import tkinter.messagebox
from collections import deque
import heapq


# Data Structures
class PatientQueue:
    def __init__(self):
        self.regular_queue = deque()  # Standard queue for regular patients
        self.priority_queue = []  # Priority queue for emergency cases
        self.patient_counter = 0  # To track patient IDs

    def add_patient(self, name, is_emergency=False):
        self.patient_counter += 1
        patient = {'id': self.patient_counter, 'name': name}
        if is_emergency:
            heapq.heappush(self.priority_queue, (-self.patient_counter, patient))  # Negative for max heap
        else:
            self.regular_queue.append(patient)
        return patient

    def get_next_patient(self):
        if self.priority_queue:
            return heapq.heappop(self.priority_queue)[1]
        elif self.regular_queue:
            return self.regular_queue.popleft()
        return None


# Initialize patient queue
patient_queue = PatientQueue()

# connection to database
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Create table if not exists with proper schema
try:
    c.execute('''CREATE TABLE IF NOT EXISTS appointments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT, age INTEGER, gender TEXT, 
                  location TEXT, scheduled_time TEXT, 
                  phone TEXT, is_emergency INTEGER DEFAULT 0)''')
    conn.commit()
except sqlite3.Error as e:
    print(f"Database error: {e}")
    # Try to alter table if it exists but missing column
    try:
        c.execute("ALTER TABLE appointments ADD COLUMN is_emergency INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Failed to alter table: {e}")


# tkinter window
class Application:
    def __init__(self, master):
        self.master = master
        self.create_widgets()
        self.update_logs()

    def create_widgets(self):
        # Window settings
        self.master.title("Hospital Appointment System")
        self.master.geometry("1200x720")
        self.master.resizable(True, True)

        # Frames with proper padding
        self.left = Frame(self.master, width=800, height=720, bg='lightgreen', padx=20, pady=20)
        self.left.pack(side=LEFT, fill=BOTH, expand=True)

        self.right = Frame(self.master, width=400, height=720, bg='steelblue', padx=20, pady=20)
        self.right.pack(side=RIGHT, fill=BOTH, expand=True)

        # Labels and entries with proper spacing
        self.create_form_fields()

        # Buttons with better spacing
        button_frame = Frame(self.left, bg='lightgreen')
        button_frame.place(x=200, y=340, width=400, height=60)

        self.submit = Button(button_frame, text="Add Appointment", width=20, height=2,
                             bg='steelblue', command=self.add_appointment)
        self.submit.pack(side=LEFT, padx=10)

        self.emergency_btn = Button(button_frame, text="Emergency Case", width=20, height=2,
                                    bg='red', fg='white', command=lambda: self.add_appointment(True))
        self.emergency_btn.pack(side=LEFT, padx=10)

        # Logs display with better formatting
        self.logs = Label(self.right, text="Queue Status", font=('arial 20 bold'),
                          fg='white', bg='steelblue')
        self.logs.pack(pady=10)

        self.box = Text(self.right, width=50, height=30, font=('arial 12'))
        scrollbar = Scrollbar(self.right, command=self.box.yview)
        self.box.config(yscrollcommand=scrollbar.set)

        self.box.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

    def create_form_fields(self):
        fields = [
            ("Patient's Name", 100),
            ("Age", 140),
            ("Gender", 180),
            ("Location", 220),
            ("Appointment Time", 260),
            ("Phone Number", 300)
        ]

        self.entries = []
        for i, (text, y_pos) in enumerate(fields):
            label = Label(self.left, text=text, font=('arial 14 bold'),
                          fg='black', bg='lightgreen')
            label.place(x=50, y=y_pos)

            entry = Entry(self.left, width=30, font=('arial 14'))
            entry.place(x=250, y=y_pos)
            self.entries.append(entry)

        self.heading = Label(self.left, text="ABC Hospital Appointments",
                             font=('arial 24 bold'), fg='black', bg='lightgreen')
        self.heading.place(x=50, y=20)

    def add_appointment(self, is_emergency=False):
        values = [entry.get() for entry in self.entries]
        if any(val == '' for val in values):
            tkinter.messagebox.showinfo("Warning", "Please Fill Up All Boxes")
            return

        name, age, gender, location, time, phone = values

        # Validate age is numeric
        try:
            int(age)
        except ValueError:
            tkinter.messagebox.showinfo("Error", "Age must be a number")
            return

        # Add to queue
        patient = patient_queue.add_patient(name, is_emergency)

        # Add to database with error handling
        try:
            sql = """INSERT INTO appointments 
                     (name, age, gender, location, scheduled_time, phone, is_emergency) 
                     VALUES(?, ?, ?, ?, ?, ?, ?)"""
            c.execute(sql, (name, age, gender, location, time, phone, int(is_emergency)))
            conn.commit()

            # Show success message
            msg = f"Appointment for {name} has been created"
            if is_emergency:
                msg += " (EMERGENCY CASE)"
            tkinter.messagebox.showinfo("Success", msg)

            # Update logs
            self.update_logs()
            self.clear_entries()
        except sqlite3.Error as e:
            tkinter.messagebox.showerror("Database Error", f"Failed to save appointment: {e}")

    def clear_entries(self):
        for entry in self.entries:
            entry.delete(0, END)

    def update_logs(self):
        self.box.delete(1.0, END)

        # Get all appointments from DB
        try:
            c.execute("SELECT COUNT(*) FROM appointments")
            total = c.fetchone()[0]
            self.box.insert(END, f"Total Appointments: {total}\n\n")

            # Show queue status
            self.box.insert(END, "Current Queue Status:\n")
            self.box.insert(END, "=" * 30 + "\n\n")

            # Show emergency cases first
            self.box.insert(END, "Emergency Cases:\n")
            self.box.insert(END, "-" * 30 + "\n")
            for priority, patient in patient_queue.priority_queue:
                self.box.insert(END, f"ID: {patient['id']} - {patient['name']}\n")

            # Show regular cases
            self.box.insert(END, "\nRegular Cases:\n")
            self.box.insert(END, "-" * 30 + "\n")
            for patient in patient_queue.regular_queue:
                self.box.insert(END, f"ID: {patient['id']} - {patient['name']}\n")
        except sqlite3.Error as e:
            self.box.insert(END, f"Error loading appointments: {e}")


root = Tk()
b = Application(root)
root.mainloop()