from flask import Flask, render_template, Response,jsonify, request,redirect, url_for
from camera import Video
import cv2
import os
import face_recognition
import mediapipe as mp
import random
import string
import dlib
from utils import save_customer_data,putText,get_customer_data

app = Flask(__name__)
mp_face_detection = mp.solutions.face_detection.FaceDetection()
camera_enabled = False  
known_face_encodings = []
known_face_names = []
thresh_least = 12

for name in os.listdir("Known-Faces"):
    
    for i in os.listdir(os.path.join("Known-Faces",name)):
        try:
            known_image = face_recognition.load_image_file(os.path.join("Known-Faces",name , i))

            known_face_encoding = face_recognition.face_encodings(known_image)[0]
            known_face_encodings.append(known_face_encoding)
            known_face_names.append(name)
        except:
            continue
        
video1 = Video(known_face_encodings,known_face_names,mp_face_detection)
g1 = False
g2 = False
ready_to_save = False
g_face_name = ""
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log', methods=['POST'])
def log():
    log_message = request.data.decode('utf-8')
    print(f"Log message from client: {log_message}")

    global camera_enabled,g1,g2,g_face_name,video1,ready_to_save
    if log_message == "Camera enabled":
        camera_enabled = True
        
        g_face_name = ""
        print("Camera enabled")


    elif log_message == "Camera disabled":
        camera_enabled = False
        
        g1 = False
        g2 = False
        ready_to_save = False
        # del video1 #if del so sample image is also not shown on video frame
        print("Camera disabled")

    return "Log received"

def gen(camera):
    unknown_faces = {}
    known_faces = {}
    frame_count = 0
    image_saved = False
    
    while True:
        
        if camera_enabled:
            color = (0, 0, 255)
            global g1,g2,ready_to_save
         
            frame, faces_names, rects = camera.get_frame()
            try:
               
                if len(faces_names)>1:
                    print(faces_names,"faces  names")
                for i, face_name in enumerate(faces_names):
                    if not face_name:
                        continue
                   
                    if face_name == "Unknown":
                        if i not in unknown_faces:
                            tracker = dlib.correlation_tracker()
                            tracker.start_track(frame, dlib.rectangle(*rects[i]))
                            unknown_faces[i] = {'tracker': tracker, 'frames': [frame[rects[i][1]:rects[i][3],rects[i][0]:rects[i][2]]], 'count': 1}
                            print("New tracker")
                        else:
                            print("Update tracker")
                            unknown_faces[i]['tracker'].update(frame)
                            unknown_faces[i]['frames'].append(frame[rects[i][1]:rects[i][3],rects[i][0]:rects[i][2]])
                            unknown_faces[i]['count'] += 1
                            
                            if unknown_faces[i]['count'] >= thresh_least:
                                
                                name_fol = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                                face_folder = os.path.join("Known-Faces", name_fol)
                                k = 0

                                os.makedirs(face_folder, exist_ok=True)
                                thresh_current_run = 4
                                print("running after folder created")
                                for j, saved_frame in enumerate(unknown_faces[i]['frames']):
                                    print(f"len of frames of {i} : {len(unknown_faces[i]['frames'])}\n j: {j}")
                                    if k <thresh_current_run:
                                        try:
                                            known_face_encoding = face_recognition.face_encodings(saved_frame)[0]
                                            if len(known_face_encoding) > 0:

                                                known_face_names.append(name_fol)
                                                known_face_encodings.append(known_face_encoding)
                                                k +=1
                                            else:
                                                unknown_faces[i]['count'] -= 1
                                                unknown_faces[i]['frames'].pop(j)
                                                continue
                                        except:
                                            unknown_faces[i]['count'] -= 1
                                            unknown_faces[i]['frames'].pop(j)

                                            continue
                                    
                                    print("image save start")
                                    cv2.imwrite(os.path.join(face_folder, f"{j}.jpg"), saved_frame)
                                    print("Iamge Saved")
                                    if j>=thresh_least-1:
                                        ready_to_save = True
                                    if j>=len(unknown_faces[i]['frames'])-1:
                                        print(j,"yes")
                                        
                                        g1 = True  
                                    if j>=len(unknown_faces[i]['frames'])-(int(len(unknown_faces[i]['frames'])//2)):
                                        frame = putText(frame,f"New Customer detected{name_fol}")
                                        color = (0, 255, 0)
                              
                                unknown_faces.pop(i)

                    else:
                       
                        if face_name:
                            print("face name condtion",face_name)
                            
                            global g_face_name
                            g_face_name = face_name
                            color = (0, 255, 0)
                            if i not in known_faces:
                                tracker1 = dlib.correlation_tracker()
                                tracker1.start_track(frame, dlib.rectangle(*rects[i]))
                                known_faces[i] = {'tracker': tracker1, 'frames': [frame[rects[i][1]:rects[i][3],rects[i][0]:rects[i][2]]], 'count': 1}
                            else:
                                print(known_faces[i]['count'],ready_to_save)
                                print("Update tracker of known face",rects)
                                known_faces[i]['tracker'].update(frame)
                                known_faces[i]['frames'].append(frame[rects[i][1]:rects[i][3],rects[i][0]:rects[i][2]])
                                known_faces[i]['count'] += 1
                                print(known_faces[i]['count'])
                                print("tracker updated")
                                if (known_faces[i]['count'] >= thresh_least) or ready_to_save:
                                    
                                    g2 = True  
                                    print("known face count 10")
                                    known_faces.pop(i)

                        
                    x,y,x1,y1 = rects[i]
                
                    
                    # cv2.rectangle(frame, (x, y), (x1, y1), (0, 0, 255), 1)
                    cv2.line(frame, (x, y), (x + 30, y), color, 6)  # TL
                    cv2.line(frame, (x, y), (x, y + 30), color, 6)

                    cv2.line(frame, (x1, y), (x1 - 30, y), color, 6)  # TR
                    cv2.line(frame, (x1, y), (x1, y + 30), color, 6)

                    cv2.line(frame, (x, y1), (x + 30, y1), color, 6)  # BL
                    cv2.line(frame, (x, y1), (x, y1 - 30), color, 6)

                    cv2.line(frame, (x1, y1), (x1 - 30, y1), color, 6)  # BR
                    cv2.line(frame, (x1, y1), (x1, y1 - 30), color, 6)

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
        
@app.route('/check_face_saved')
def check_face_saved():
   
    image_saved = False
    known_redirect = False
    print("inside function yes")
    if g1:
        print("inside g1")
    
        image_saved = True
        

    if g2 and  not g1:
        print("inside g2")
        known_redirect = True
    return jsonify({'image_saved': image_saved,"known_redirect":known_redirect,"faceid":g_face_name})


@app.route('/submit', methods=['POST'])
def submit_form():
    name = request.form.get('name')
    address = request.form.get('address')
    phone = request.form.get('phone')
    email = request.form.get('email')

    fruits = request.form.getlist('fruits[]')
    quantities = {}

    for fruit in fruits:
        quantity = request.form.get(f'quantity_{fruit}')
        quantities[fruit] = quantity


    global g_face_name
    print("Customer ID",g_face_name)
    print('Name:', name)
    print('Address:', address)
    print('Phone:', phone)
    print('Email:', email)
    print('Fruits:', fruits)
    print('Quantities:', quantities)
    save_customer_data(g_face_name,name,address,phone,email,quantities)

    return render_template("index.html")
@app.route('/submit2', methods=['POST'])
def submit_form2():
    global g_face_name
    row_date, row_time, person_name, person_email, person_phone, person_address = get_customer_data(g_face_name)

    fruits = request.form.getlist('fruits[]')
    quantities = {}

    for fruit in fruits:
        quantity = request.form.get(f'quantity_{fruit}')
        quantities[fruit] = quantity

    print("Customer ID",g_face_name)
    print('Name:', person_name)
    print('Address:', person_address)
    print('Phone:', person_phone)
    print('Email:', person_email)
    print('Fruits:', fruits)
    print('Quantities:', quantities)
    save_customer_data(g_face_name,person_name,person_address,person_phone,person_email,quantities)

    return render_template("index.html")
@app.route('/video')
def video():
  
    res = gen(video1)
    print(res)
    
    return Response(res, mimetype='multipart/x-mixed-replace; boundary=frame')
    
@app.route('/graphs')
def second_page():
    return render_template('graphs.html')

@app.route('/test1')
def third_page():
    return render_template('test1.html')

@app.route('/known')
def fourth_page():
    return render_template('known.html')

if __name__ == '__main__':
    app.run(debug=True)
