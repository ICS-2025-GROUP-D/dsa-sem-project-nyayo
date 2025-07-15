# Hospital Management System - Project Report

## Data Structures Used
1. **Queue and Priority Queue**
   - Used for managing patient appointments
   - Emergency cases get priority
   - Time Complexity:
     - Enqueue: O(1) for regular, O(log n) for priority
     - Dequeue: O(1) for regular, O(log n) for priority

2. **Hash Table**
   - Used for quick patient lookup by ID
   - Time Complexity: O(1) average case for search

3. **Binary Search Tree**
   - Used for efficient patient searching and management
   - Time Complexity: O(log n) average case for search/insert

## Architecture
The system follows a MVC-like architecture:
- **Model**: Data structures and database
- **View**: Tkinter GUI components
- **Controller**: Application logic in the UI classes