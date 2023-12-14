#SECTION 1
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import json
import os
import face_recognition
from tkinter import messagebox
import shutil

frame_width = 640
frame_height = 480
cap = None

current_employee = None
successful_photos = 0
#SECTION 2
def set_button_state(state):
    add_button.config(state=state)
    edit_button.config(state=state)
    delete_button.config(state=state)
    # ready_button.config(state=state)  # Ready button is removed from GUI

def start_video():
    global cap, capture_button, back_button
    if cap is None:
        cap = cv2.VideoCapture(0)
        capture_button.config(state=tk.NORMAL)
        back_button.config(state=tk.NORMAL)
        set_button_state(tk.DISABLED)
        show_frame()
#SECTION 2
def capture_frame():
    global cap, successful_photos, current_employee, add_button, feedback_label, capture_button
    if cap and current_employee:
        ret, frame = cap.read()
        if ret:
            face_locations = face_recognition.face_locations(frame)
            if face_locations:
                photo_path = f"current/{current_employee}/photo_{successful_photos}.jpg"
                cv2.imwrite(photo_path, frame)
                successful_photos += 1
                feedback_label.config(text=f"Photo {successful_photos} captured successfully.")
                if successful_photos >= 5:
                    successful_photos = 0
                    current_employee = None
                    add_button.config(state=tk.NORMAL)
                    capture_button.config(state=tk.DISABLED)
                    feedback_label.config(text="5 photos captured successfully.")
                    if cap:
                        cap.release()
                        cap = None
                    video_label.config(image='')
                    video_label.imgtk = None
            else:
                feedback_label.config(text="No face detected. Try again.")
#SECTION 3
def go_back():
    global cap
    if cap:
        cap.release()
        cap = None
    cv2.destroyAllWindows()
    root.destroy()

def re_enable_buttons():
    set_button_state(tk.NORMAL)
#SECTION 4
def add_employee():
    global current_employee, add_button
    name_var = tk.StringVar()
    surname_var = tk.StringVar()
    pin_var = tk.StringVar()
    role_var = tk.StringVar()
    set_button_state(tk.DISABLED)

    add_window = tk.Toplevel(root)
    add_window.title("Add Employee")

    tk.Label(add_window, text="Name").grid(row=0, column=0)
    tk.Label(add_window, text="Surname").grid(row=1, column=0)
    tk.Label(add_window, text="PIN").grid(row=2, column=0)
    tk.Label(add_window, text="Role").grid(row=3, column=0)

    name_entry = tk.Entry(add_window, textvariable=name_var)
    surname_entry = tk.Entry(add_window, textvariable=surname_var)
    pin_entry = tk.Entry(add_window, textvariable=pin_var)

    name_entry.grid(row=0, column=1)
    surname_entry.grid(row=1, column=1)
    pin_entry.grid(row=2, column=1)

    # Set focus to the Name entry field
    name_entry.focus_set()

    name_entry.grid(row=0, column=1)
    surname_entry.grid(row=1, column=1)
    pin_entry.grid(row=2, column=1)

    try:
        with open("roles.txt", "r") as file:
            roles = file.read().splitlines()
    except FileNotFoundError:
        roles = []

    role_dropdown = tk.OptionMenu(add_window, role_var, *roles)
    role_dropdown.grid(row=3, column=1)

    save_button = tk.Button(add_window, text="Save",
                            command=lambda: save_employee(name_var, surname_var, pin_var, role_var, add_window))
    save_button.grid(row=4, column=0, columnspan=2)
#SECTION 5
def save_employee(name_var, surname_var, pin_var, role_var, add_window):
    global current_employee, add_button
    name = name_var.get()
    surname = surname_var.get()
    pin = pin_var.get()
    role = role_var.get()
    set_button_state(tk.DISABLED)

    if not all([name, surname, pin, role]):
        tk.messagebox.showerror("Error", "All fields are required")
        return

    # Check if employee already exists
    directory = f"current/{name}_{surname}"
    if os.path.exists(directory):
        tk.messagebox.showerror("Error", "Employee already exists")
        return

    if not os.path.exists(directory):
        os.makedirs(directory)

    employee_data = {
        "name": name,
        "surname": surname,
        "pin": pin,
        "role": role,
        "photos": [f"employees/{name}_{surname}/"]
    }
    update_file_structure(employee_data)

    current_employee = f"{name}_{surname}"  # Set the current employee
    add_window.destroy()

    # Start the video as if the Ready button was pressed
    start_video()
    add_button.config(state=tk.NORMAL)  # Re-enable the Add button
#SECTION 7
def update_file_structure(employee_data):
    try:
        with open("Filestr.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    data.append(employee_data)
    with open("Filestr.json", "w") as file:
        json.dump(data, file, indent=4)
#SECTION 8
def edit_employee():
    def start_edit(employee_var, edit_window):
        selected_employee = employee_var.get()
        if selected_employee:
            global current_employee
            current_employee = selected_employee
            edit_window.destroy()
            start_video()
            capture_button.config(state=tk.NORMAL)
            add_button.config(state=tk.DISABLED)
            edit_button.config(state=tk.DISABLED)
            delete_button.config(state=tk.DISABLED)
            set_button_state(tk.DISABLED)

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Employee")

    try:
        with open("Filestr.json", "r") as file:
            employees = json.load(file)
        employee_names = [f"{emp['name']}_{emp['surname']}" for emp in employees]
    except FileNotFoundError:
        employee_names = []

    employee_var = tk.StringVar(edit_window)
    employee_dropdown = tk.OptionMenu(edit_window, employee_var, *employee_names)
    employee_dropdown.pack()

    edit_button = tk.Button(edit_window, text="Edit", command=lambda: start_edit(employee_var, edit_window))
    edit_button.pack()


#SECTION 9
def delete_employee():
    def confirm_delete(employee_var, delete_window):
        selected_employee = employee_var.get()
        if selected_employee:
            response = tk.messagebox.askyesno("Confirm", f"Do you want to delete {selected_employee}?")
            if response:
                delete_employee_data(selected_employee)
                delete_window.destroy()

    def delete_employee_data(employee_name):
        try:
            with open("Filestr.json", "r") as file:
                employees = json.load(file)
            employees = [emp for emp in employees if f"{emp['name']}_{emp['surname']}" != employee_name]
            with open("Filestr.json", "w") as file:
                json.dump(employees, file, indent=4)

            # Delete the employee's directory
            directory = f"current/{employee_name}"
            if os.path.exists(directory):
                shutil.rmtree(directory)

        except Exception as e:
            tk.messagebox.showerror("Error", str(e))

    delete_window = tk.Toplevel(root)
    delete_window.title("Delete Employee")

    try:
        with open("Filestr.json", "r") as file:
            employees = json.load(file)
        employee_names = [f"{emp['name']}_{emp['surname']}" for emp in employees]
    except FileNotFoundError:
        employee_names = []

    employee_var = tk.StringVar(delete_window)
    employee_dropdown = tk.OptionMenu(delete_window, employee_var, *employee_names)
    employee_dropdown.pack()

    delete_button = tk.Button(delete_window, text="Delete", command=lambda: confirm_delete(employee_var, delete_window))
    delete_button.pack()
#SECTION 10

def show_frame():
    global cap, video_label
    if cap:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (frame_width, frame_height))
            center_coordinates = (frame_width // 2, frame_height // 2)
            axes_length = (100, 160)
            cv2.ellipse(frame, center_coordinates, axes_length, 0, 0, 360, (0, 255, 0), 2)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)
        video_label.after(10, show_frame)

# Tkinter GUI setup
# Tkinter GUI setup
root = tk.Tk()
root.geometry(f'{frame_width}x{frame_height + 100}')

video_container = tk.Frame(root, width=frame_width, height=frame_height)
video_container.pack_propagate(False)
video_container.pack()

video_label = tk.Label(video_container, bg='grey')
video_label.pack(fill=tk.BOTH, expand=True)

button_container = tk.Frame(root)
button_container.pack()

# ready_button = tk.Button(button_container, text="Ready", command=start_video)  # Ready button is removed from GUI
capture_button = tk.Button(button_container, text="Capture", state='disabled', command=capture_frame)
back_button = tk.Button(button_container, text="Exit", state='disabled', command=go_back)  # Changed "Back" to "Exit"
add_button = tk.Button(button_container, text="Add", command=add_employee)
edit_button = tk.Button(button_container, text="Retake", command=edit_employee)
delete_button = tk.Button(button_container, text="Delete", command=delete_employee)

# Rearranging the buttons as per your request
add_button.pack(side=tk.LEFT)
delete_button.pack(side=tk.LEFT)
edit_button.pack(side=tk.LEFT)
capture_button.pack(side=tk.LEFT)
back_button.pack(side=tk.LEFT)

# Add a label for feedback
feedback_label = tk.Label(root, text="")
feedback_label.pack()

root.mainloop()

# Release resources
if cap:
    cap.release()
cv2.destroyAllWindows()

