from tkinter import *
import sqlite3
import tkinter.messagebox


class PatientBSTNode:
    def __init__(self, patient):
        self.patient = patient
        self.left = None
        self.right = None


class PatientBST:
    def __init__(self):
        self.root = None
        self.load_from_db()

    def load_from_db(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Ensure table has all required columns
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
            patient = {
                'id': row[0],
                'name': row[1],
                'age': row[2],
                'gender': row[3],
                'location': row[4],
                'phone': row[5],
                'time': row[6],
                'is_emergency': bool(row[7]) if len(row) > 7 else False
            }
            self.insert(patient)
        conn.close()

    def insert(self, patient):
        if self.root is None:
            self.root = PatientBSTNode(patient)
        else:
            self._insert(patient, self.root)

    def _insert(self, patient, current_node):
        if patient['id'] < current_node.patient['id']:
            if current_node.left is None:
                current_node.left = PatientBSTNode(patient)
            else:
                self._insert(patient, current_node.left)
        elif patient['id'] > current_node.patient['id']:
            if current_node.right is None:
                current_node.right = PatientBSTNode(patient)
            else:
                self._insert(patient, current_node.right)

    def search(self, patient_id):
        return self._search(patient_id, self.root)

    def _search(self, patient_id, current_node):
        if current_node is None:
            return None
        elif current_node.patient['id'] == patient_id:
            return current_node.patient
        elif patient_id < current_node.patient['id']:
            return self._search(patient_id, current_node.left)
        else:
            return self._search(patient_id, current_node.right)


# Initialize BST
patient_bst = PatientBST()


class Application:
    def __init__(self, master):
        self.master = master

        # Window settings
        self.master.title("Patient Management System")
        self.master.geometry("1200x800")
        self.master.resizable(True, True)

        self.create_widgets()

    def create_widgets(self):
        # Main container with padding
        self.main_frame = Frame(self.master, padx=20, pady=20)
        self.main_frame.pack(fill=BOTH, expand=True)

        # heading label with proper spacing
        self.heading = Label(self.main_frame, text="Update Appointments",
                             fg='steelblue', font=('arial 28 bold'))
        self.heading.pack(pady=20)

        # Search area
        search_frame = Frame(self.main_frame)
        search_frame.pack(fill=X, pady=20)

        Label(search_frame, text="Enter Patient's Name or ID",
              font=('arial 14 bold')).pack(side=LEFT, padx=10)

        self.search_entry = Entry(search_frame, width=30, font=('arial 14'))
        self.search_entry.pack(side=LEFT, padx=10)

        self.search = Button(search_frame, text="Search", width=12, height=1,
                             bg='steelblue', command=self.search_db)
        self.search.pack(side=LEFT, padx=10)

        # Result area with scrollable frame
        result_container = Frame(self.main_frame)
        result_container.pack(fill=BOTH, expand=True)

        self.canvas = Canvas(result_container)
        scrollbar = Scrollbar(result_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def search_db(self):
        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        search_term = self.search_entry.get().strip()
        if not search_term:
            tkinter.messagebox.showinfo("Error", "Please enter a search term")
            return

        # Try searching by ID first
        try:
            patient_id = int(search_term)
            patient = patient_bst.search(patient_id)
            if patient:
                self.show_patient(patient)
                return
        except ValueError:
            pass

        # If not found by ID or search term isn't numeric, search by name
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        sql = "SELECT * FROM appointments WHERE name LIKE ?"
        c.execute(sql, (f"%{search_term}%",))
        patients = c.fetchall()
        conn.close()

        if not patients:
            tkinter.messagebox.showinfo("Not Found", "No matching patients found")
            return

        if len(patients) == 1:
            patient = {
                'id': patients[0][0],
                'name': patients[0][1],
                'age': patients[0][2],
                'gender': patients[0][3],
                'location': patients[0][4],
                'phone': patients[0][5],
                'time': patients[0][6],
                'is_emergency': bool(patients[0][7]) if len(patients[0]) > 7 else False
            }
            self.show_patient(patient)
        else:
            self.show_multiple_results(patients)

    def show_multiple_results(self, patients):
        Label(self.scrollable_frame, text="Multiple matches found. Select one:",
              font=('arial 16 bold')).pack(pady=10)

        for patient in patients:
            frame = Frame(self.scrollable_frame, bd=2, relief=GROOVE)
            frame.pack(fill=X, padx=10, pady=5)

            text = f"ID: {patient[0]} - {patient[1]} (Age: {patient[2]}, {patient[3]})"
            text += f" - Appointment: {patient[6]}"
            if len(patient) > 7 and patient[7]:
                text += " (EMERGENCY)"

            btn = Button(frame, text=text, width=100, anchor='w',
                         command=lambda p=patient: self.show_patient({
                             'id': p[0],
                             'name': p[1],
                             'age': p[2],
                             'gender': p[3],
                             'location': p[4],
                             'phone': p[5],
                             'time': p[6],
                             'is_emergency': bool(p[7]) if len(p) > 7 else False
                         }))
            btn.pack()

    def show_patient(self, patient):
        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Create form fields with better spacing
        fields = [
            ("Patient ID", 'id', False),
            ("Name", 'name', True),
            ("Age", 'age', True),
            ("Gender", 'gender', True),
            ("Location", 'location', True),
            ("Phone", 'phone', True),
            ("Appointment Time", 'time', True),
            ("Emergency Case", 'is_emergency', True)
        ]

        self.entries = {}
        for i, (label, field, editable) in enumerate(fields):
            row = Frame(self.scrollable_frame)
            row.pack(fill=X, padx=10, pady=5)

            Label(row, text=label + ":", width=20, anchor='e',
                  font=('arial 12')).pack(side=LEFT, padx=5)

            if field == 'is_emergency':
                var = IntVar(value=1 if patient.get(field, False) else 0)
                check = Checkbutton(row, variable=var, state='normal' if editable else 'disabled')
                check.pack(side=LEFT)
                self.entries[field] = var
            else:
                entry = Entry(row, font=('arial 12'))
                entry.insert(0, str(patient.get(field, '')))
                if not editable:
                    entry.config(state='readonly')
                entry.pack(side=LEFT, fill=X, expand=True, padx=5)
                self.entries[field] = entry

        # Action buttons with better spacing
        btn_frame = Frame(self.scrollable_frame)
        btn_frame.pack(fill=X, pady=20)

        Button(btn_frame, text="Update", width=15, bg='lightblue',
               command=lambda: self.update_db(patient['id'])).pack(side=LEFT, padx=20)

        Button(btn_frame, text="Delete", width=15, bg='red', fg='white',
               command=lambda: self.delete_db(patient['id'])).pack(side=LEFT, padx=20)

    def update_db(self, patient_id):
        # Get updated values
        updated_values = {
            'name': self.entries['name'].get(),
            'age': self.entries['age'].get(),
            'gender': self.entries['gender'].get(),
            'location': self.entries['location'].get(),
            'phone': self.entries['phone'].get(),
            'time': self.entries['time'].get(),
            'is_emergency': bool(self.entries['is_emergency'].get())
        }

        # Validate
        if not updated_values['name']:
            tkinter.messagebox.showinfo("Error", "Name cannot be empty")
            return

        try:
            int(updated_values['age'])
        except ValueError:
            tkinter.messagebox.showinfo("Error", "Age must be a number")
            return

        # Update database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            query = """UPDATE appointments SET 
                       name=?, age=?, gender=?, location=?, 
                       phone=?, scheduled_time=?, is_emergency=?
                       WHERE id=?"""
            c.execute(query, (
                updated_values['name'],
                updated_values['age'],
                updated_values['gender'],
                updated_values['location'],
                updated_values['phone'],
                updated_values['time'],
                int(updated_values['is_emergency']),
                patient_id
            ))
            conn.commit()

            tkinter.messagebox.showinfo("Updated", "Successfully Updated.")

            # Reinitialize BST to reflect changes
            global patient_bst
            patient_bst = PatientBST()
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Failed to update: {str(e)}")
        finally:
            conn.close()

    def delete_db(self, patient_id):
        if not tkinter.messagebox.askyesno("Confirm", "Delete this patient record?"):
            return

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            # Delete from database
            sql = "DELETE FROM appointments WHERE id=?"
            c.execute(sql, (patient_id,))
            conn.commit()

            tkinter.messagebox.showinfo("Success", "Deleted Successfully")

            # Reinitialize BST to reflect changes
            global patient_bst
            patient_bst = PatientBST()

            # Clear the form
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Failed to delete: {str(e)}")
        finally:
            conn.close()


root = Tk()
b = Application(root)
root.mainloop()