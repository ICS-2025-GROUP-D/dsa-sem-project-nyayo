from collections import deque
import heapq

class PatientQueue:
    def __init__(self):
        self.regular_queue = deque()
        self.priority_queue = []
        self.patient_counter = 0

    def add_patient(self, name, is_emergency=False):
        self.patient_counter += 1
        patient = {'id': self.patient_counter, 'name': name}
        if is_emergency:
            heapq.heappush(self.priority_queue, (-self.patient_counter, patient))
        else:
            self.regular_queue.append(patient)
        return patient

    def get_next_patient(self):
        if self.priority_queue:
            return heapq.heappop(self.priority_queue)[1]
        elif self.regular_queue:
            return self.regular_queue.popleft()
        return None

    def __len__(self):
        return len(self.regular_queue) + len(self.priority_queue)

    def get_queue_status(self):
        status = {
            'regular': list(self.regular_queue),
            'priority': [item[1] for item in self.priority_queue]
        }
        return status