import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os
import face_recognition
from employees import employees  # Importing employee data

frame_width = 640
frame_height = 480

# Load employee face encodings
employee_encodings = {}
for name, photo_paths in employees.items():
    employee_encodings[name] = []
    for photo_path in photo_paths:
        if os.path.exists(photo_path):  # Check if the file exists
            image = face_recognition.load_image_file(photo_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                encoding = encodings[0]
                employee_encodings[name].append(encoding)
            else:
                print(f"No face found in {photo_path}")
        else:
            print(f"File not found: {photo_path}")

def show_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (frame_width, frame_height))

        # Draw an oval
        center_coordinates = (frame_width // 2, frame_height // 2)
        axes_length = (100, 160)  # Width and height of the oval
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
    button1.config(state=tk.DISABLED)
    show_frame()

def take_photo():
    ret, frame = cap.read()
    if ret:
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (frame_width, frame_height))
        if not os.path.exists('photos'):
            os.makedirs('photos')
        photo_path = 'photos/photo.jpg'
        cv2.imwrite(photo_path, frame)

        # Perform face recognition
        identify_employee(photo_path)

def identify_employee(photo_path):
    unknown_image = face_recognition.load_image_file(photo_path)
    unknown_encodings = face_recognition.face_encodings(unknown_image)

    if unknown_encodings:
        unknown_encoding = unknown_encodings[0]

        for name, encodings in employee_encodings.items():
            for encoding in encodings:
                results = face_recognition.compare_faces([encoding], unknown_encoding)
                if True in results:
                    print(f"Employee identified: {name}")
                    return
        print("Employee not identified")
    else:
        print("No face found in the taken photo")


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

button2 = tk.Button(button_container, text="Take Photo", command=take_photo)
button2.pack(side=tk.LEFT)

button3 = tk.Button(button_container, text="Admin")
button3.pack(side=tk.LEFT)

button4 = tk.Button(button_container, text="TBC 1")
button4.pack(side=tk.LEFT)

button5 = tk.Button(button_container, text="TBC 2")
button5.pack(side=tk.LEFT)

root.mainloop()

if 'cap' in globals():
    cap.release()
    cv2.destroyAllWindows()
