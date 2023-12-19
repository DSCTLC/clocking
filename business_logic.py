# BUS Section 1
import cv2
import tkinter as tk
import face_recognition
import os
import json
import shutil
from tkinter import Toplevel, Label, Button
from tkinter import messagebox
from datetime import datetime, timedelta


cap = None
show_message_on_video = False  # Flag to control message display
employee_encodings = {}  # Global variable to store pre-processed face encodings

# BUS Section 2
def start_video(gui):
    global cap
    if cap is None:
        cap = cv2.VideoCapture(0)
        gui.capture_button.config(state=tk.NORMAL)
        gui.start_button.config(state=tk.DISABLED)
        gui.back_button.config(state=tk.NORMAL)# Disable the start button
        show_frame(gui)

def custom_confirm_dialog(employee_name, last_status, formatted_last_action, gui, login_type, current_time):
    dialog = Toplevel(gui.root)
    dialog.title("Confirm Action")

    # Determine the action message based on the last status
    action_msg = f"Your last action: Logged {'out' if last_status == 'out' else 'in'} at {formatted_last_action}"
    question_msg = f"Do you want to log {'out' if last_status == 'in' else 'in'}?"

    # Display the message
    Label(dialog, text=action_msg).pack(pady=(10, 0))
    Label(dialog, text=question_msg, font=("Helvetica", 14, "bold")).pack(pady=(5, 20))

    # Create and pack the "Yes" button
    yes_button = Button(dialog, text="Yes", command=lambda: confirm_action(dialog, employee_name, last_status, gui, login_type, True, current_time))
    yes_button.pack(fill='x', expand=True, padx=20, pady=5)

    # Create and pack the "Correct Previous Non Action" button
    correct_button = Button(dialog, text="Correct Previous Non Action", command=lambda: confirm_action(dialog, employee_name, last_status, gui, login_type, False, current_time))
    correct_button.pack(fill='x', expand=True, padx=20, pady=5)

    # Bind the window close ('X' button) event to the on_dialog_close function
    dialog.protocol("WM_DELETE_WINDOW", lambda: on_dialog_close(gui, dialog))

    dialog.transient(gui.root)  # Set to be on top of the main window
    dialog.grab_set()  # Ensure all input goes to this dialog
    dialog.wait_window()  # Wait here until the dialog is closed

def on_dialog_close(gui, dialog):
    """
    Handle the dialog close event.
    """
    dialog.destroy()
    go_back(gui)

def confirm_action(dialog, employee_name, last_status, gui, login_type, user_response, current_time):
    dialog.destroy()
    if user_response:
        # User agrees to log in/out
        new_status = "in" if last_status == "out" else "out"
        data = read_attendance_data()  # Read the attendance data
        data_record = {
            "employee": employee_name,
            "status": new_status,
            "timestamp": current_time,
            "type": login_type,
            "photo": None  # Replace with actual photo path if available
        }
        data[employee_name] = {"status": new_status, "last_clock": current_time}
        write_attendance_data(data)
        append_to_attendance_log(data_record)
        if login_type == "manual":
            messagebox.showinfo("Manual Login", f"Manual login successful for {employee_name}")

        # Update GUI to 'back' state and stop the video
        go_back(gui)

    else:
        # User chooses to backdate
        data = read_attendance_data()  # Read the attendance data
        last_action = data.get(employee_name, {}).get("last_clock", "No previous record")
        backdate_action(employee_name, last_status, last_action, gui, login_type, current_time)

def capture_frame(gui, attempt=1):
    global cap
    if cap:
        gui.start_button.config(state=tk.DISABLED)  # Disable the start button
        gui.capture_button.config(state=tk.DISABLED)
        gui.back_button.config(state=tk.NORMAL)  # Disable the capture button

        ret, frame = cap.read()
        if ret:
            temp_photo_path = "temp_captured_photo.jpg"
            cv2.imwrite(temp_photo_path, frame)

            employee_name = recognize_employee(temp_photo_path)
            if employee_name:
                # Ask if the recognized employee is correct
                response = messagebox.askyesno("Recognition Result", f"Hello {employee_name}. Is this you?")
                if response:
                    # If the user confirms, process attendance
                    process_attendance(employee_name, gui, "facial")
                else:
                    # If the user says it's not them, offer manual login
                    response = messagebox.askyesno("Manual Login", "Do you want to log in manually?")
                    if response:
                        manual_login(gui, temp_photo_path)
                    else:
                        # Return to the original state
                        go_back(gui)
            else:
                # If no employee is recognized
                response = messagebox.askyesno("Recognition Result", "Not recognized. Do you want to log in manually?")
                if response:
                    manual_login(gui, temp_photo_path)
                else:
                    # Return to the original state
                    go_back(gui)


def read_attendance_data():
    try:
        with open('attendance.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def write_attendance_data(data):
    with open('attendance.json', 'w') as file:
        json.dump(data, file, indent=4)

def append_to_attendance_log(record):
    log_file = 'attendance_log.json'
    try:
        with open(log_file, 'r+') as file:
            log_data = json.load(file)
            log_data.append(record)
            file.seek(0)
            json.dump(log_data, file, indent=4)
    except FileNotFoundError:
        with open(log_file, 'w') as file:
            json.dump([record], file, indent=4)

def process_attendance(employee_name, gui, login_type, photo_path=None):
    data = read_attendance_data()
    current_time = datetime.now().isoformat()

    last_action_info = data.get(employee_name, {"status": "out", "last_clock": "No previous record"})
    last_action = last_action_info.get("last_clock")
    last_status = last_action_info.get("status")

    # Format the last action time for display
    if last_action and last_action != "No previous record":
        try:
            formatted_last_action = datetime.fromisoformat(last_action).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            formatted_last_action = last_action  # In case of formatting error, use original
    else:
        formatted_last_action = last_action

    # Call the custom confirm dialog
    custom_confirm_dialog(employee_name, last_status, formatted_last_action, gui, login_type, current_time)

def backdate_logout(employee_name, last_action, data):
    # Logic to backdate the logout
    backdated_time = last_action  # Modify as needed
    data[employee_name] = {"status": "out", "last_clock": backdated_time, "type": "backdated"}

def backdate_action(employee_name, current_status, last_action, gui, login_type, current_time):
    backdate_window = tk.Toplevel(gui.root)
    backdate_window.title("Backdate Action")

    # Handle the window close event
    backdate_window.protocol("WM_DELETE_WINDOW", lambda: on_popup_close(gui, backdate_window))

    # Instructions
    instruction_label = tk.Label(backdate_window, text=f"Select a time for {employee_name} (after {last_action}):")
    instruction_label.pack()

    # Generate time options
    try:
        last_action_time = datetime.strptime(last_action, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        # Handle invalid format or 'No previous record'
        last_action_time = datetime.now()

    time_options = generate_time_options(employee_name)

    # Check if time options are available
    if not time_options:
        messagebox.showerror("Error", "No valid backdate times available.")
        backdate_window.destroy()
        return

    # Time dropdown
    selected_time = tk.StringVar(backdate_window)
    time_menu = tk.OptionMenu(backdate_window, selected_time, *time_options)
    time_menu.pack()

    # Submit button
    submit_button = tk.Button(backdate_window, text="Submit", command=lambda: submit_backdate(employee_name, current_status, selected_time.get(), backdate_window, gui, login_type))
    submit_button.pack()

def generate_time_options(employee_name):
    # Read the current attendance data
    data = read_attendance_data()
    last_action_info = data.get(employee_name, {"last_clock": "No previous record"})
    last_action_str = last_action_info.get("last_clock")

    # Try parsing the last action time in different formats
    last_action_time = None
    datetime_formats = ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y%m%d @ %H:%M"]
    for fmt in datetime_formats:
        try:
            last_action_time = datetime.strptime(last_action_str, fmt)
            break
        except (ValueError, TypeError):
            continue

    # Use current time if parsing fails
    if not last_action_time:
        print("Invalid last action time format or no previous record. Using current time instead.")
        last_action_time = datetime.now()

    # Generate time options starting from the next 15-minute mark after the last action
    time_options = []
    current_time = datetime.now()
    start_time = last_action_time + timedelta(minutes=15 - (last_action_time.minute % 15))

    # Ensure start_time is not in the future
    if start_time > current_time:
        start_time = current_time - timedelta(minutes=current_time.minute % 15)

    # Generate time options up to the current time
    while start_time <= current_time:
        formatted_time = start_time.strftime("%Y-%m-%d @ %H:%M")
        time_options.append(formatted_time)
        start_time += timedelta(minutes=15)

    return time_options

def submit_backdate(employee_name, current_status, datetime_str, backdate_window, gui, login_type):
    if not datetime_str:
        messagebox.showerror("Backdate Error", "No time selected. Please select a time.")
        return

    # Attempt to convert the selected time to ISO format
    try:
        backdated_time = datetime.strptime(datetime_str, "%Y-%m-%d @ %H:%M").isoformat(timespec='microseconds')
    except ValueError as e:
        messagebox.showerror("Error", f"Invalid time format: {e}")
        print(f"Error parsing time: {datetime_str}. Exception: {e}")
        return

    # Determine the backdated and current statuses
    backdated_status = "out" if current_status == "in" else "in"
    new_current_status = "in" if backdated_status == "out" else "out"

    # Create a record for the backdated action
    backdate_record = {
        "employee": employee_name,
        "status": backdated_status,
        "timestamp": backdated_time,
        "type": "backdated",
        "login_type": login_type
    }

    # Append the backdated record to the attendance log
    append_to_attendance_log(backdate_record)

    # Update the main attendance data with the new current status and timestamp
    current_time = datetime.now().isoformat(timespec='microseconds')
    data = read_attendance_data()
    data[employee_name] = {"status": new_current_status, "last_clock": current_time}
    write_attendance_data(data)

    # Create a record for the current action
    current_record = {
        "employee": employee_name,
        "status": new_current_status,
        "timestamp": current_time,
        "type": "current",
        "login_type": login_type
    }

    # Append the current record to the attendance log
    append_to_attendance_log(current_record)

    messagebox.showinfo("Backdate", f"Backdated {employee_name}'s status to {backdated_status} at {datetime_str}")

    backdate_window.destroy()
    go_back(gui)


def preprocess_and_store_encodings():
    global employee_encodings
    with open('Filestr.json', 'r') as file:
        employees = json.load(file)

    for employee in employees:
        employee_photos = []
        for photo_dir in employee["photos"]:
            photo_dir = photo_dir.strip("/")
            full_photo_path = os.path.join('current', 'employees', photo_dir)

            if os.path.isdir(full_photo_path):
                for filename in os.listdir(full_photo_path):
                    file_path = os.path.join(full_photo_path, filename)
                    image = face_recognition.load_image_file(file_path)
                    encodings = face_recognition.face_encodings(image)

                    if encodings:
                        employee_photos.append(encodings[0])

        employee_encodings[f"{employee['name']} {employee['surname']}"] = employee_photos

# BUS Section 5
def recognize_employee(captured_photo_path):
    global employee_encodings
    captured_image = face_recognition.load_image_file(captured_photo_path)
    captured_face_encoding = face_recognition.face_encodings(captured_image)

    if not captured_face_encoding:
        return None

    captured_face_encoding = captured_face_encoding[0]

    for employee, encodings in employee_encodings.items():
        match_count = sum(face_recognition.compare_faces(encodings, captured_face_encoding))

        if match_count >= 2:
            return employee

    return None

# BUS Section 6
def go_back(gui):
    global cap
    if cap is not None:
        cap.release()
        cap = None
    reset_gui(gui)

# BUS Section 7
def show_frame(gui):
    global cap, show_message_on_video
    if cap:
        ret, frame = cap.read()
        if ret:
            # Flip the frame horizontally and resize if necessary
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (640, 480))

            # Draw an oval on the frame as a guide for face positioning
            center_x, center_y = frame.shape[1] // 2, frame.shape[0] // 2
            axes_length = (100, 150)  # Width and height of the oval
            cv2.ellipse(frame, (center_x, center_y), axes_length, 0, 0, 360, (0, 255, 0), 2)

            # If the flag is set, draw the message on the frame
            if show_message_on_video:
                text = "Getting Video Ready"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1
                font_color = (0, 0, 255)  # Red color
                thickness = 2
                text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]

                # Calculate the text position so it's centered
                text_x = (frame.shape[1] - text_size[0]) // 2
                text_y = (frame.shape[0] + text_size[1]) // 2

                # Draw the text on the frame
                cv2.putText(frame, text, (text_x, text_y), font, font_scale, font_color, thickness)

            # Update the frame in the GUI
            gui.update_frame(frame)

        # Schedule the next frame update
        gui.root.after(10, lambda: show_frame(gui))
# BUS Section 8
def manual_login(gui, photo_path):
    # Create a new window for manual login
    login_window = tk.Toplevel(gui.root)
    login_window.title("Manual Login")

    # Handle the window close event
    login_window.protocol("WM_DELETE_WINDOW", lambda: on_popup_close(gui, login_window))

    # Dropdown for employee selection
    with open('Filestr.json', 'r') as file:
        employees = json.load(file)
    employee_names = [f"{e['name']} {e['surname']}" for e in employees]
    selected_employee = tk.StringVar(login_window)
    employee_menu = tk.OptionMenu(login_window, selected_employee, *employee_names)
    employee_menu.pack()

    # PIN entry
    pin_label = tk.Label(login_window, text="Enter PIN:")
    pin_label.pack()
    pin_entry = tk.Entry(login_window, show="*")
    pin_entry.pack()

    # Submit button
    submit_button = tk.Button(login_window, text="Submit", command=lambda: validate_login(selected_employee.get(), pin_entry.get(), photo_path, gui, login_window))
    submit_button.pack()

def on_popup_close(gui, popup_window):
    """
    Handle the popup window close event.
    """
    popup_window.destroy()
    go_back(gui)
def save_photo_for_manual_login(photo_path, employee_name):
    manual_photo_dir = 'manual_login_photos'
    if not os.path.exists(manual_photo_dir):
        os.makedirs(manual_photo_dir)
    photo_filename = f"{employee_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    shutil.copy(photo_path, os.path.join(manual_photo_dir, photo_filename))
    return os.path.join(manual_photo_dir, photo_filename)


def validate_login(employee_name, pin, photo_path, gui, login_window):
    with open('Filestr.json', 'r') as file:
        employees = json.load(file)

    employee_record = next((e for e in employees if f"{e['name']} {e['surname']}" == employee_name), None)

    if employee_record and employee_record['pin'] == pin:
        photo_for_report = save_photo_for_manual_login(photo_path, employee_name)
        login_window.destroy()  # Close the manual login window immediately after successful login
        process_attendance(employee_name, gui, "manual", photo_for_report)
    else:
        messagebox.showerror("Manual Login", "Incorrect PIN. Please try again.")
        # Optionally, clear the PIN entry field here

def read_attendance_data():
    try:
        with open('attendance.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def write_attendance_data(data):
    with open('attendance.json', 'w') as file:
        json.dump(data, file, indent=4)
def reset_gui(gui):
    gui.start_button.config(state=tk.NORMAL)
    gui.capture_button.config(state=tk.DISABLED)
    gui.back_button.config(state=tk.DISABLED)
    gui.video_label.imgtk = None
    gui.video_label.configure(image='')

# BUS Section 9
def release_resources():
    global cap
    if cap is not None:
        cap.release()
        cv2.destroyAllWindows()

# Initialize the preprocessing at the start of the program
preprocess_and_store_encodings()
