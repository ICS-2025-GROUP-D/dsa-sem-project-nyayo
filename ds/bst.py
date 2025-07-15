import sqlite3

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

    def inorder_traversal(self):
        patients = []
        self._inorder_traversal(self.root, patients)
        return patients

    def _inorder_traversal(self, node, patients):
        if node is not None:
            self._inorder_traversal(node.left, patients)
            patients.append(node.patient)
            self._inorder_traversal(node.right, patients)

    def delete(self, patient_id):
        self.root = self._delete(self.root, patient_id)

    def _delete(self, node, patient_id):
        if node is None:
            return node

        if patient_id < node.patient['id']:
            node.left = self._delete(node.left, patient_id)
        elif patient_id > node.patient['id']:
            node.right = self._delete(node.right, patient_id)
        else:
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            temp = self._min_value_node(node.right)
            node.patient = temp.patient
            node.right = self._delete(node.right, temp.patient['id'])

        return node

    def _min_value_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current