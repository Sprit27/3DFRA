import cv2
import os
import shutil
import threading
from flask import Flask, render_template, request, jsonify, redirect, url_for,Response
import sqlite3
from datetime import datetime
import pickle
import numpy as np
#from face_recn import store_face, recognize_faces
#from dispy35 import recognize_faces_with_gui, att
import face_recognition
from Info import add_entry
import tkinter as tk
from tkinter import messagebox, Button,Entry
import time
#from clear import rmo
from PIL import Image, ImageTk
import webview

app = Flask(__name__)
window = webview.create_window('3DFRA',app, width=1200, height=800)

ENCODINGS_FILE = "face_encodings.pkl"
# rout for the home page--------------------------------------------------------------------------------------------
@app.route('/')
def home():
    return render_template('home.html')


#@app.route('/detect')
#def detect():
    #return render_template('detect.html')
    



# Route for the HTML form to get the image name and image--------------------------------------------------------------------------------
@app.route('/register')
def index():
    return render_template('register.html')


#data of uno and name--------------------------------------------------------------------------------------------------

DATABASE = "info2.db"
def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

def create_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            unique_number INTEGER UNIQUE NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_entry(name, unique_number):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO people (name, unique_number) VALUES (?, ?)", (name, unique_number))
        conn.commit()
        print(f"Added: {name} with unique number {unique_number}")
    except sqlite3.IntegrityError as e:
        print(f"Error: {e}")
    finally:
        conn.close()

#creat table if not exists
create_table()

# Route for capturing an image and storing info in database---------------------------------------------------------------------------
@app.route('/capture', methods=['POST'])

def capture_image():

    folder = "saves"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    


    # Ask user for the file name
    output = request.form.get('filename')
    uno = request.form.get('uno')
    output_file = output + ".jpg"
    full_path = os.path.join(folder, output_file)
    
    # Initialize the webcam (0 is the default camera)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
       return jsonify({"status": "error", "message": "Could not access the webcam."})

    print("Press 'Space' to capture an image, or 'Esc' to exit.")

    # Create a named window
    cv2.namedWindow("Capture Image", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Capture Image", cv2.WND_PROP_TOPMOST, 1)  # Make window topmost

    while True:
        # Capture a frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Display the frame in a window
        cv2.imshow("Capture Image", frame)

        # Wait for a key press
        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC key to exit
            cap.release()
            time.sleep(1)
            cv2.destroyAllWindows()
            return jsonify({"status": "error", "message": "Exited without saving."})

        elif key == 32:  # Space key to capture
            cv2.imwrite(full_path, frame)
            
            # Call necessary functions
            store_face(full_path, output)  
            add_entry(output, uno)

            cap.release()  # Release webcam after capture
            time.sleep(1)
            cv2.destroyAllWindows()

            return jsonify({"status": "success", "message": f"Image saved as {full_path}"})
    # Ensuring a valid response if the loop somehow exits
    cap.release()
    time.sleep(1)
    cv2.destroyAllWindows()
    return jsonify({"status": "error", "message": "Unexpected exit from capture loop."})

# atendance tables------------------------------------------------------------------------------------------------------


# table for record of all sessions for month
def import_people_to_session():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get the current session table name (YYYY_MM)
    attendance_table = datetime.now().strftime("%Y_%m")

    try:
        # Ensure the session table exists
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS "{attendance_table}" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unique_number INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                Attendance_count INTEGER DEFAULT 0
            )
        """)

        # Fetch all unique_number and name from the people table
        cursor.execute("SELECT unique_number, name FROM people")
        people_data = cursor.fetchall()

        # Insert data into the session table while avoiding duplicates
        for unique_number, name in people_data:
            try:
                cursor.execute(f"""
                    INSERT INTO "{attendance_table}" (unique_number, name)
                    VALUES (?, ?)
                """, (unique_number, name))
            except sqlite3.IntegrityError:
                # Ignore duplicate unique_number entries
                pass

        conn.commit()
        print("People data imported successfully into the session table.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()







#new tables for sessions---------------------------------------------------------------------------------------------
def create_attendance_records():
    conn = get_db()
    cursor = conn.cursor()
    #attendance= datetime.now().strftime("%Y_%m")
    attendance_records= datetime.now().strftime("%Y_%m_%d")
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS "{attendance_records}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_date TEXT NOT NULL,
            unique_number INTEGER NOT NULL,
            present INTEGER DEFAULT 0,
            FOREIGN KEY (unique_number) REFERENCES people(unique_number)
        )
    """)
    conn.commit()
    conn.close()



#mark attendance
def mark_attendance_session(unique_number, present=1):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        attendance_records= datetime.now().strftime("%Y_%m_%d")
        session_date = datetime.now().strftime("%Y_%m_%d %H:%M:%S")  # Current date & time
        cursor.execute(f"""
            SELECT 1 FROM "{attendance_records}" WHERE unique_number = ?
        """, (unique_number,))
        existing_entry = cursor.fetchone()

        if not existing_entry:  # Insert only if no existing entry
            cursor.execute(f"""
                INSERT INTO "{attendance_records}" (session_date, unique_number, present)
                VALUES (?, ?, ?)
            """, (session_date, unique_number, present))
            conn.commit()
            print(f"Marked {unique_number} as {'present' if present else 'absent'} for session on {session_date}")
        else:
            print(f"Skipping {unique_number}, already recorded.")

    except sqlite3.Error as e:
        print(f"Error: {e}")

    finally:
        conn.close()


#modified mark attendance

def mark_attendance(unique_number):
    conn = get_db()
    cursor = conn.cursor()
    
    # Get table names
    attendance_table = datetime.now().strftime("%Y_%m")  # Monthly attendance table
    daily_attendance_table = datetime.now().strftime("%Y_%m_%d")  # Daily attendance table

    try:
        # Check if the unique_number has already been marked present today
        cursor.execute(f"""
            SELECT 1 FROM "{daily_attendance_table}" WHERE unique_number = ?
        """, (unique_number,))
        already_marked = cursor.fetchone()

        if already_marked:
            print(f"Attendance for unique_number {unique_number} has already been marked today.")
        else:
            # Insert record in daily table
            session_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Timestamp
            cursor.execute(f"""
                INSERT INTO "{daily_attendance_table}" (session_date, unique_number, present)
                VALUES (?, ?, ?)
            """, (session_date, unique_number, 1))

            # Update the monthly attendance count
            cursor.execute(f"""
                UPDATE "{attendance_table}"
                SET Attendance_count = Attendance_count + 1
                WHERE unique_number = ?
            """, (unique_number,))

            print(f"Attendance for unique_number {unique_number} has been updated for today.")

        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()







#get unique number by name
def get_unique_number_by_name(name):
    conn = get_db()  # Adjust database name if needed
    cursor = conn.cursor()
    #attendance= datetime.now().strftime("%Y_%m")

    cursor.execute(f"""
        SELECT unique_number FROM people WHERE name = ?
    """, (name,))
    
    result = cursor.fetchone()  # Fetch one matching record
    conn.close()
    
    if result:
        return result[0]  # Return the unique_number
    else:
        print(f"No record found for name: {name}")
        return None


#store faces--------------------------------------------------------------------------------------------------------
def store_face(image_path, name):
# Load image using OpenCV
    image = cv2.imread(image_path)

    if image is None:
        print(f"[ERROR] Could not read image: {image_path}")
        return

    # Convert to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Debugging: print info
    print(f"[DEBUG] dtype: {image_rgb.dtype}, shape: {image_rgb.shape}")

    # Ensure it's 3-channel RGB
    if image_rgb.ndim != 3 or image_rgb.shape[2] != 3:
        print("[ERROR] Image is not a 3-channel RGB image.")
        return

    # Ensure dtype is uint8
    if image_rgb.dtype != np.uint8:
        print("[ERROR] Image dtype is not uint8. Fixing it.")
        image_rgb = image_rgb.astype(np.uint8)

    # Get face encodings
    try:
        encodings = face_recognition.face_encodings(image_rgb)
    except Exception as e:
        print(f"[ERROR] face_recognition failed: {e}")
        return

    if len(encodings) == 0:
        print(f"[WARNING] No face detected in {image_path}. Skipping.")
        return

    # Load existing encodings
    if os.path.exists(ENCODINGS_FILE):
        with open(ENCODINGS_FILE, "rb") as f:
            known_faces = pickle.load(f)
    else:
        known_faces = {"encodings": [], "names": []}

    # Add the new encoding and name
    known_faces["encodings"].append(encodings[0])
    known_faces["names"].append(name)

    # Save updated encodings
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(known_faces, f)

    print(f"[INFO] Stored face encoding for {name}.")

# Call the function to execute the data transfer
import_people_to_session()

#dispy35----------------------------------------------------------------------------------------------------
detected_names = set()

def is_spoof(frame, face_location):
    """ Detects spoofing using multiple techniques """
    (top, right, bottom, left) = face_location
    face_roi = frame[top:bottom, left:right]
    
    # Blurriness Detection
    gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian_var < 30:
        return True  # Likely a spoof (blurry / printed image)
    
    # Color Texture Analysis
    hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
    saturation = np.mean(hsv[:, :, 1])
    if saturation < 30:
        return True  # Low saturation suggests spoofing
    
    # Specular Reflection Detection
    edges = cv2.Canny(gray, 100, 200)
    edge_density = np.sum(edges) / (face_roi.shape[0] * face_roi.shape[1])
    if edge_density < 0.02:
        return True  # Low edge density suggests a spoof
    
    # Eye Blink Detection (using dlib)
    '''detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    dets = detector(gray)
    for det in dets:
        shape = predictor(gray, det)
        
        # Eye aspect ratio (EAR) for blink detection
        dx1 = shape.part(46).x - shape.part(44).x
        dy1 = shape.part(47).y - shape.part(43).y
        
        if dx1 == 0:  # Prevent division by zero
            return True  # Possible spoof
        
        right_eye_ratio = dy1 / dx1
        
        # Set a threshold for real blinks (adjust based on testing)
        if right_eye_ratio < 0.1:  
            return True  # Likely spoof (static image)'''

    return False  # Real face


def recognize_faces_with_gui():
    def update_frame():
        global detected_names

        if not os.path.exists(ENCODINGS_FILE):
            print("No stored face data found. Please add faces first.")
            return

        with open(ENCODINGS_FILE, "rb") as f:
            known_faces = pickle.load(f)

        known_face_encodings = known_faces["encodings"]
        known_face_names = known_faces["names"]

        ret, frame = video_capture.read()
        if not ret:
            print("Error: Unable to read from webcam.")
            return

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

            face_names.append(name)
            detected_names.add(name)

        # Display results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Check for spoofing
            spoofed = is_spoof(frame, (top, right, bottom, left))
            color = (0, 255, 0) if not spoofed else (0, 0, 255)  # Green if real, Red if spoofed

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        canvas.imgtk = imgtk
        canvas.create_image(0, 0, anchor="nw", image=imgtk)

        # Keep window on top even when clicked away
        root.attributes("-topmost", True)

        root.after(10, update_frame)
    
    def add_name():
        name = name_entry.get().strip()
        if name:
            detected_names.add(name)
            name_entry.delete(0, tk.END)

    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("Error: Unable to access the webcam.")
        return

    root = tk.Tk()
    root.title("Face Recognition with Enhanced Anti-Spoofing")
    root.configure(bg="black")
    root.geometry("800x600")

    canvas = tk.Canvas(root, width=700, height=500, bg="black")
    canvas.pack()
    
    frame_controls = tk.Frame(root, bg="black")
    frame_controls.pack()

    name_entry = Entry(frame_controls, width=30)
    name_entry.pack(side=tk.LEFT, padx=5, pady=5)
    submit_button = Button(frame_controls, text="Add Name", command=add_name)
    submit_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    update_frame()

    #close button
    #close_button = tk.Button(root, text="Close", command=root.destroy)
    #close_button.pack()
    def go_home():
      video_capture.release()
      time.sleep(2)
      cv2.destroyAllWindows()
      root.destroy()
    home_button = Button(root, text="Back to Home", command=go_home, bg="gray", fg="white")
    home_button.pack(pady=10)
  




    root.mainloop()

    video_capture.release()
    cv2.destroyAllWindows()

def att():
    return list(detected_names)
 





# Route to handle face recognition---------------------------------------------------------------------------------------

@app.route('/recognise')

def recognise():
    create_attendance_records()
    recognize_faces_with_gui()
    
    names = att()  # Get all detected names

    for name in names:
        if name != "Unknown":  # Ignore unknown faces
            uno = get_unique_number_by_name(name)
            if uno:  # Ensure the unique number exists
                print(f"Marking attendance for: {name} ({uno})")
                
                mark_attendance(uno)
                

    return redirect(url_for('home')) 


#clear-----------------------------------------------------------------------------------------------------------------

@app.route('/clear')
def clear():
    def on_yes():
        file_path = "face_encodings.pkl"
        file2 = "saves"
        
        if os.path.exists(file_path):
            os.remove(file_path)
            messagebox.showinfo("Success", "Facial data cleared successfully!")
        else:
            messagebox.showwarning("Warning", "File not found!")

        if os.path.exists(file2):
            shutil.rmtree(file2)
            messagebox.showinfo("Success", "Facial data cleared successfully!")
        else:
            messagebox.showwarning("Warning", "File not found!")

        root.destroy()

    def on_no():
        root.destroy()

    root = tk.Tk()
    root.title("Confirmation")
    root.geometry("300x150")
    root.configure(bg="black")
    root.attributes('-topmost', True)

    label = tk.Label(root, text="Do you want to clear the facial data?", padx=10, pady=10, bg="black", fg="white")
    label.pack()

    button_yes = tk.Button(root, text="Yes", command=on_yes, width=10, bg="gray", fg="white")
    button_yes.pack(pady=5)

    button_no = tk.Button(root, text="No", command=on_no, width=10, bg="gray", fg="white")
    button_no.pack(pady=5)

    root.mainloop()
    
    return redirect(url_for('home'))    

#Record---------------------------------------------------------------------------------------------------------------

@app.route('/rec')
def rec():
    return render_template('Record.html')

@app.route('/record')
def record():
     conn = get_db()
     conn.row_factory = sqlite3.Row
     cursor = conn.cursor()
     
    
     attendance_table = datetime.now().strftime("%Y_%m")  # Monthly attendance table

     try:
        cursor.execute(f'SELECT * FROM "{attendance_table}"')
        data = cursor.fetchall()
        
        # Convert data to a list of dictionaries
        records = [dict(row) for row in data]

        return jsonify(records)  # Return as JSON

     except sqlite3.Error as e:
        return jsonify({"error": str(e)})

     finally:
        conn.close()

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')
    

@app.route('/about')
def about():
    return render_template('about.html')
    



    

if __name__ == '__main__':
    #app.run(host='127.0.0.1',port=5000)
    #webview.create_window("Smart Face Attendance System", "http://127.0.0.1:5000")
    # Flask thread
    def start_flask():
        app.run(debug=False, use_reloader=False)

    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Wait for Flask to start up
    time.sleep(2)

    # Then create and start the window
    webview.create_window('3DFRA', 'http://127.0.0.1:5000', width=1200, height=800)
    webview.start(gui='edgechromium')
   
