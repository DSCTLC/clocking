import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os

frame_width = 640
frame_height = 480

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
        cv2.imwrite('photos/photo.jpg', frame)

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
