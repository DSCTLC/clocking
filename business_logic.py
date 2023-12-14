# BUS Secion 1
import cv2
import tkinter as tk
import face_recognition
import os
import json

cap = None
show_message_on_video = False  # Flag to control message display
# BUS Secion 2
def start_video(gui):
    global cap
    if cap is None:
        cap = cv2.VideoCapture(0)
        gui.capture_button.config(state=tk.NORMAL)
        gui.back_button.config(state=tk.NORMAL)
        show_frame(gui)
# BUS Secion 3
def capture_frame(gui):
    global cap
    if cap:
        ret, frame = cap.read()
        if ret:
            # Save the captured frame temporarily
            temp_photo_path = "temp_captured_photo.jpg"
            cv2.imwrite(temp_photo_path, frame)

            # Perform facial recognition
            employee_name = recognize_employee(temp_photo_path)
            if employee_name:
                gui.show_message(f"Hello {employee_name}")
            else:
                gui.show_message("No match or unable to read face")
                
# BUS Secion 4

def recognize_employee(captured_photo_path):
    # Load employee data from Filestr.json
    with open('Filestr.json', 'r') as file:
        employees = json.load(file)

    # Load the captured image
    captured_image = face_recognition.load_image_file(captured_photo_path)
    captured_face_encoding = face_recognition.face_encodings(captured_image)

    if captured_face_encoding:
        captured_face_encoding = captured_face_encoding[0]
    else:
        return None  # No face detected in the captured image

    # Iterate through each employee and compare faces
    for employee in employees:
        for photo_path in employee["photos"]:
            # Construct the full path for employee photos
            full_photo_path = os.path.join('current', photo_path)
            for filename in os.listdir(full_photo_path):
                employee_image = face_recognition.load_image_file(os.path.join(full_photo_path, filename))
                employee_face_encoding = face_recognition.face_encodings(employee_image)[0]

                # Compare faces
                results = face_recognition.compare_faces([employee_face_encoding], captured_face_encoding)
                if results[0]:
                    return f"{employee['name']} {employee['surname']}"

    return None  # No match found
# BUS Secion 4
def go_back(gui):
    global cap
    if cap is not None:
        cap.release()
        cap = None

    # Reset the GUI elements
    reset_gui(gui)
# BUS Secion 5

def show_frame(gui):
    global cap, show_message_on_video
    if cap:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (640, 480))

            # If the flag is set, draw the message on the frame
            if show_message_on_video:
                text = "Getting Video Ready"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1
                font_color = (0, 0, 255)  # Red color
                thickness = 2
                text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]

                # Get the text position so it's centered
                text_x = (frame.shape[1] - text_size[0]) // 2
                text_y = (frame.shape[0] + text_size[1]) // 2

                cv2.putText(frame, text, (text_x, text_y), font, font_scale, font_color, thickness)

            gui.update_frame(frame)
        gui.root.after(10, lambda: show_frame(gui))
# BUS Secion 6
def reset_gui(gui):
    # Reset the GUI to its initial state
    gui.start_button.config(state=tk.NORMAL)
    gui.capture_button.config(state=tk.DISABLED)
    gui.back_button.config(state=tk.DISABLED)
    gui.video_label.imgtk = None
    gui.video_label.configure(image='')  # Remove the current image

# BUS Secion 7
def release_resources():
    global cap
    if cap is not None:
        cap.release()
        cv2.destroyAllWindows()
