from tkinter import *
import tkinter.messagebox
from ds.queue import PatientQueue
from db.database import init_db, execute_query
import sqlite3

class AppointmentWindow:
    def __init__(self, master):
        self.master = master
        self.patient_queue = PatientQueue()
        self.create_widgets()
        self.update_logs()
        init_db()

    def create_widgets(self):
        self.master.title("Hospital Appointment System")
        self.master.geometry("1200x720")
        self.master.resizable(True, True)

        self.left = Frame(self.master, width=800, height=720, bg='lightgreen', padx=20, pady=20)
        self.left.pack(side=LEFT, fill=BOTH, expand=True)

        self.right = Frame(self.master, width=400, height=720, bg='steelblue', padx=20, pady=20)
        self.right.pack(side=RIGHT, fill=BOTH, expand=True)

        self.create_form_fields()

        button_frame = Frame(self.left, bg='lightgreen')
        button_frame.place(x=200, y=340, width=400, height=60)

        self.submit = Button(button_frame, text="Add Appointment", width=20, height=2,
                             bg='steelblue', command=self.add_appointment)
        self.submit.pack(side=LEFT, padx=10)

        self.emergency_btn = Button(button_frame, text="Emergency Case", width=20, height=2,
                                    bg='red', fg='white', command=lambda: self.add_appointment(True))
        self.emergency_btn.pack(side=LEFT, padx=10)

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

        try:
            int(age)
        except ValueError:
            tkinter.messagebox.showinfo("Error", "Age must be a number")
            return

        patient = self.patient_queue.add_patient(name, is_emergency)

        try:
            sql = """INSERT INTO appointments 
                     (name, age, gender, location, scheduled_time, phone, is_emergency) 
                     VALUES(?, ?, ?, ?, ?, ?, ?)"""
            execute_query(sql, (name, age, gender, location, time, phone, int(is_emergency)))

            msg = f"Appointment for {name} has been created"
            if is_emergency:
                msg += " (EMERGENCY CASE)"
            tkinter.messagebox.showinfo("Success", msg)

            self.update_logs()
            self.clear_entries()
        except sqlite3.Error as e:
            tkinter.messagebox.showerror("Database Error", f"Failed to save appointment: {e}")

    def clear_entries(self):
        for entry in self.entries:
            entry.delete(0, END)

    def update_logs(self):
        self.box.delete(1.0, END)

        try:
            from db.database import fetch_query
            appointments = fetch_query("SELECT COUNT(*) FROM appointments")
            total = appointments[0][0] if appointments else 0
            self.box.insert(END, f"Total Appointments: {total}\n\n")

            self.box.insert(END, "Current Queue Status:\n")
            self.box.insert(END, "=" * 30 + "\n\n")

            self.box.insert(END, "Emergency Cases:\n")
            self.box.insert(END, "-" * 30 + "\n")
            for priority, patient in self.patient_queue.priority_queue:
                self.box.insert(END, f"ID: {patient['id']} - {patient['name']}\n")

            self.box.insert(END, "\nRegular Cases:\n")
            self.box.insert(END, "-" * 30 + "\n")
            for patient in self.patient_queue.regular_queue:
                self.box.insert(END, f"ID: {patient['id']} - {patient['name']}\n")
        except Exception as e:
            self.box.insert(END, f"Error loading appointments: {e}")