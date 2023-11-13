import cv2
from pyzbar.pyzbar import decode
import jwt
import json
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
from threading import *
import pandas as pd
import csv


signature = "paneerbutterchickenmasala"


with open('Book1.csv', mode='r') as infile:
    reader = csv.reader(infile)
    mydict = dict((rows[0],rows[2]) for rows in reader)
    


try:
    with open("jwt_tokens.json", "r") as json_file:
        json_data = json.load(json_file)
        jwt_tokens = json_data.get("tokens", [])
        
        
except FileNotFoundError:
    jwt_tokens = []

# Initialize scanned_jwts dictionary or create it if not present
try:
    with open("scanned_jwts.json", "r") as file:
        try:
            scanned_jwts = json.load(file)
        except json.decoder.JSONDecodeError:
            scanned_jwts = {}
            
            
except FileNotFoundError:
    f = open('scanned_jwts.json', 'a')
    scanned_jwts = {}

cap = cv2.VideoCapture(0)

# Initialize the message and overlay color
message = ""
overlay_color = '#ffffff'  # White

def update_text_box(message):
    text_box.delete(1.0, tk.END)
    text_box.insert(tk.END, message)


def close_window():
    show_result_window.result_window_open = False
# Function to show a result window
def show_result_window(result, color):
    if not getattr(show_result_window, 'result_window_open', False):
        show_result_window.result_window_open = True
        top = Toplevel()
        top.geometry("400x200")
        top.title("Scan Result")
        label = Label(top, text=result,bg=color, fg='#FFFFFF', font=("Helvetica", 16))
        label.pack()
        top.after(2000, top.destroy)  # Close the window after 4 seconds
        t = Timer(2,close_window)
        t.start()

def scan():
    global message, overlay_color
    while True:
        _, frame = cap.read()

        # Decode barcodes in the frame
        decoded_objects = decode(frame)

        for obj in decoded_objects:
            if obj.type == 'QRCODE':
                jwt_string = obj.data.decode('utf-8')
                # print("JWT String:", jwt_string)

                # Verify the JWT signature
                

                try:
                    
                    decoded_jwt = jwt.decode(jwt_string, key=signature, algorithms=['HS256'])
                    decoded_jwt_string = decoded_jwt['id']
                    print(decoded_jwt_string)
                    
                except jwt.InvalidSignatureError:
                    decoded_jwt = None
                    
                except jwt.exceptions.DecodeError:
                    decoded_jwt = None
                    
                    # add a fake jwt with data saying fake pass

                if decoded_jwt:
                    try:
                    # Check if the JWT has already been scanned
                        if jwt_string in scanned_jwts:
                            if scanned_jwts[jwt_string] == 'valid':
                                message = mydict[decoded_jwt_string]
                                overlay_color = '#FFFF00'  # Yellow (already scanned valid pass)
                                show_result_window(message, "#FFFF00")  # Show valid pass window
                            else:
                                message = mydict[decoded_jwt_string]
                                overlay_color = '#00FF00'  # Green (valid pass)
                                scanned_jwts[jwt_string] = 'valid'
                                show_result_window(message, "#00FF00")  # Show valid pass window
                        else:
                            # JWT is being scanned for the first time
                            if jwt_string in jwt_tokens:
                                scanned_jwts[jwt_string] = 'valid'
                                message = mydict[decoded_jwt_string]
                                overlay_color = '#00FF00'  # Green (valid pass)
                                show_result_window(message, "#00FF00")  # Show valid pass window
                            else:
                                scanned_jwts[jwt_string] = 'invalid'
                                message = mydict[decoded_jwt_string]
                                overlay_color = '#FF0000'  # Red (invalid pass)
                                show_result_window(message, "#FF0000")  # Show invalid pass window
                    except:
                        # print("wrong pass")
                        # message="wrong pass"
                        # show_result_window(message, "#00FFFF")
                        pass
                        
                    update_text_box(jwt_string)
                    with open("scanned_jwts.json", "w") as file:
                        json.dump(scanned_jwts, file)
                    # print("succesfully scanned pass of", message + "pass verfication status:", scanned_jwts[jwt_string])

        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        img = ImageTk.PhotoImage(image=img)

        video_label.img = img
        video_label.config(image=img)
        video_label.update()

        if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit the loop
            break

    cap.release()
    cv2.destroyAllWindows()
    show_result_window.result_window_open = False

# Create the main GUI window
root = tk.Tk()
root.title("Pass Scanning App")

# Create a frame for the video capture window
video_frame = tk.Frame(root)
video_frame.pack(side=tk.RIGHT)

# Create a label for displaying the video feed
video_label = tk.Label(video_frame)
video_label.pack()

# Create a colored background frame for the left half
background_frame = tk.Frame(root, width=320, height=480, bg=overlay_color)
background_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a text widget for displaying QR code data
text_box = tk.Text(background_frame, wrap=tk.WORD, width=40, height=5)
text_box.pack(pady=20)

# Run the GUI
root.after(10, scan)  # Delay the scan function slightly to ensure the GUI is initialized first
root.mainloop()
