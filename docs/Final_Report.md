# Hospital Appointment System - Final Report

## Architecture Diagram
```mermaid
classDiagram
    class PatientQueue{
        +regular_queue: deque
        +priority_queue: heap
        +add_patient()
        +get_next_patient()
    }
    
    class PatientHashTable{
        +table: dict
        +get_patient()
        +get_all_patients()
    }
    
    class PatientBST{
        +root: BSTNode
        +insert()
        +search()
    }
    
    class Database{
        +connection
        +create_tables()
        +add_patient()
    }
    
    class AppUI{
        +create_widgets()
        +handle_events()
    }
    
    PatientQueue --> Database
    PatientHashTable --> Database
    PatientBST --> Database
    AppUI --> PatientQueue
    AppUI --> PatientHashTable
    AppUI --> PatientBST