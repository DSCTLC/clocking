import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os
import face_recognition
import json
from tkinter import messagebox

frame_width = 640
frame_height = 480
employee_encodings = {}
cap = None


def capture_photos(employee_name):
    cap = cv2.VideoCapture(0)
    photo_count = 0
    photo_paths = []
    valid_photos = []
    os.makedirs(f"employees/{employee_name}", exist_ok=True)

    while photo_count < 5:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('Capture Photos', frame)
        if cv2.waitKey(1) == ord('c'):
            photo_path = f"employees/{employee_name}/photo_{photo_count}.jpg"
            cv2.imwrite(photo_path, frame)
            photo_paths.append(photo_path)

            image = face_recognition.load_image_file(photo_path)
            if face_recognition.face_encodings(image):
                valid_photos.append(photo_path)
                photo_count += 1
                messagebox.showinfo("Photo Captured", f"Photo {photo_count} captured.")
            else:
                messagebox.showerror("Error", "No face detected in the photo. Please try again.")

    cap.release()
    cv2.destroyAllWindows()
    return photo_paths, valid_photos


def add_employee(name_entry, surname_entry, pin_entry):
    name = name_entry.get()
    surname = surname_entry.get()
    pin = pin_entry.get()
    employee_name = f"{name}_{surname}"
    photo_paths, valid_photos = capture_photos(employee_name)

    if len(valid_photos) == 5:
        new_employee = {
            "name": name,
            "surname": surname,
            "pin": pin,
            "photos": photo_paths
        }
        with open("employees.json", "a") as file:
            json.dump(new_employee, file)
            file.write('\n')
        messagebox.showinfo("Success", f"Employee {name} added successfully.")
    else:
        messagebox.showerror("Error", "Not all photos were suitable for facial recognition. Please try again.")
        for photo in photo_paths:
            if os.path.exists(photo):
                os.remove(photo)


def open_admin_panel():
    admin_root = tk.Tk()
    admin_root.title("Admin Panel")

    tk.Label(admin_root, text="Name").grid(row=0)
    tk.Label(admin_root, text="Surname").grid(row=1)
    tk.Label(admin_root, text="PIN").grid(row=2)

    name_entry = tk.Entry(admin_root)
    surname_entry = tk.Entry(admin_root)
    pin_entry = tk.Entry(admin_root)

    name_entry.grid(row=0, column=1)
    surname_entry.grid(row=1, column=1)
    pin_entry.grid(row=2, column=1)

    add_button = tk.Button(admin_root, text="Add Employee",
                           command=lambda: add_employee(name_entry, surname_entry, pin_entry))
    add_button.grid(row=4, columnspan=2)

    admin_root.mainloop()


def load_employee_data():
    try:
        with open("employees.json", "r") as file:
            employees = [json.loads(line) for line in file.readlines()]
        return employees
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return []


employees = load_employee_data()
for employee in employees:
    name = f'{employee["name"]}_{employee["surname"]}'
    employee_encodings[name] = []
    for photo_path in employee["photos"]:
        if os.path.exists(photo_path):
            image = face_recognition.load_image_file(photo_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                employee_encodings[name].append(encodings[0])


def show_frame():
    global cap
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


def start_video():
    global cap
    cap = cv2.VideoCapture(0)
    show_frame()


# Tkinter GUI setup for clocking system
root = tk.Tk()
root.geometry(f'{frame_width}x{frame_height + 100}')

video_container = tk.Frame(root, width=frame_width, height=frame_height)
video_container.pack_propagate(False)
video_container.pack()

video_label = tk.Label(video_container, bg='grey')
video_label.pack(fill=tk.BOTH, expand=True)

button_container = tk.Frame(root)
button_container.pack()

button1 = tk.Button(button_container, text="Logon", command=start_video)
button1.pack(side=tk.LEFT)

button2 = tk.Button(button_container, text="Admin", command=open_admin_panel)
button2.pack(side=tk.LEFT)

root.mainloop()

# Release resources
if cap:
    cap.release()
cv2.destroyAllWindows()
