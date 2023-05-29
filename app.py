from flask import Flask, render_template, Response, request
from camera import Video
import cv2
import os
import face_recognition
import mediapipe as mp
import random
import string
import dlib
from utils import save_customer_data
app = Flask(__name__)
mp_face_detection = mp.solutions.face_detection.FaceDetection()
camera_enabled = False  # Variable to track camera state
known_face_encodings = []
known_face_names = []
thresh_least = 10
for name in os.listdir("Known-Faces"):
    for i in os.listdir(os.path.join("Known-Faces",name)):
        known_face_names.append(name)
        known_image = face_recognition.load_image_file(os.path.join("Known-Faces",name , i))
        known_face_encoding = face_recognition.face_encodings(known_image)[0]
        known_face_encodings.append(known_face_encoding)
video1 = Video(known_face_encodings,known_face_names,mp_face_detection)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log', methods=['POST'])
def log():
    log_message = request.data.decode('utf-8')
    print(f"Log message from client: {log_message}")

    global camera_enabled
    if log_message == "Camera enabled":
        camera_enabled = True
        
        print("Camera enabled")
    elif log_message == "Camera disabled":
        camera_enabled = False
        print("Camera disabled")

    return "Log received"

def gen(camera):
    unknown_faces = {}
    frame_count = 0

    while True:
        
        if camera_enabled:
            
            frame, faces_names, rects = camera.get_frame()
            try:
                # Track unknown faces and count frames
                for i, face_name in enumerate(faces_names):
                    if face_name == "Unknown":
                        if i not in unknown_faces:
                            tracker = dlib.correlation_tracker()
                            tracker.start_track(frame, dlib.rectangle(*rects[i]))
                            unknown_faces[i] = {'tracker': tracker, 'frames': [frame[rects[i][1]:rects[i][3],rects[i][0]:rects[i][2]]], 'count': 1}
                        else:
                            unknown_faces[i]['tracker'].update(frame)
                            unknown_faces[i]['frames'].append(frame[rects[i][1]:rects[i][3],rects[i][0]:rects[i][2]])
                            unknown_faces[i]['count'] += 1
                            # print(unknown_faces[i], unknown_faces[i]['count'])
                            if unknown_faces[i]['count'] >= thresh_least:
                                # Save unknown face with random ID
                                name_fol = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                                face_folder = os.path.join("Known-Faces", name_fol)
                                os.makedirs(face_folder, exist_ok=True)
                                k = 0
                                #thresh to save current running program
                                thresh_current_run = 4
                                for j, saved_frame in enumerate(unknown_faces[i]['frames']):
                                    if k <thresh_current_run:
                                        known_face_names.append(name_fol)
                                    
                                        known_face_encoding = face_recognition.face_encodings(saved_frame)[0]
                                        known_face_encodings.append(known_face_encoding)
                                        k +=1
                                    
                                    cv2.imwrite(os.path.join(face_folder, f"{j}.jpg"), saved_frame)
                                    print("Iamge Save")
                                # faces_names[i] = name_fol
                                unknown_faces.pop(i)

                    else:
                        if i in unknown_faces:
                            unknown_faces.pop(i)
                        if face_name:
                            save_customer_data(face_name)
                    x,y,x1,y1 = rects[i]
                    
                    # cv2.rectangle(frame, (x, y), (x1, y1), (0, 0, 255), 1)
                    cv2.line(frame, (x, y), (x + 30, y), (0, 0, 255), 6)  # Top Left
                    cv2.line(frame, (x, y), (x, y + 30), (0, 0, 255), 6)

                    cv2.line(frame, (x1, y), (x1 - 30, y), (0, 0, 255), 6)  # Top Right
                    cv2.line(frame, (x1, y), (x1, y + 30), (0, 0, 255), 6)

                    cv2.line(frame, (x, y1), (x + 30, y1), (0, 0, 255), 6)  # Bottom Left
                    cv2.line(frame, (x, y1), (x, y1 - 30), (0, 0, 255), 6)

                    cv2.line(frame, (x1, y1), (x1 - 30, y1), (0, 0, 255), 6)  # Bottom right
                    cv2.line(frame, (x1, y1), (x1, y1 - 30), (0, 0, 255), 6)

                frame_count += 1

                ret, jpg = cv2.imencode('.jpg', frame)
                frame = jpg.tobytes()
            except:
                ret, jpg = cv2.imencode('.jpg', frame)
                frame = jpg.tobytes()
                yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame +
               b'\r\n\r\n')
        else:
            frame = cv2.imread(r"static\download.jpg")
            ret, jpg = cv2.imencode('.jpg', frame)
            frame = jpg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame +
               b'\r\n\r\n')

       

@app.route('/video')
def video():
    return Response(gen(video1), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/graphs')
def second_page():
    return render_template('graphs.html')

if __name__ == '__main__':
    app.run(debug=True)
