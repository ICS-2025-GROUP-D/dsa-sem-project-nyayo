from tkinter import Tk
from ui.appointment import AppointmentWindow
from ui.display import DisplayWindow
from ui.management import ManagementWindow
from db.database import init_db


def main():
    init_db()

    # Create main windows
    root1 = Tk()
    app1 = AppointmentWindow(root1)

    root2 = Tk()
    app2 = DisplayWindow(root2)

    root3 = Tk()
    app3 = ManagementWindow(root3)

    root1.mainloop()
    root2.mainloop()
    root3.mainloop()


if __name__ == "__main__":
    main()