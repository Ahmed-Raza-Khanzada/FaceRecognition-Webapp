import csv
from datetime import datetime, timedelta
import pandas as pd
import cv2
def save_customer_data(id,name,address,phone,email,quantities):
    current_datetime = datetime.now()
    current_year = current_datetime.year
    current_date = current_datetime.date()
    current_time = current_datetime.time().strftime("%H:%M")

    header = ["year", "date", "time", "Customer_id","name","address","phone","email"]
    data = [current_year, current_date, current_time, id,name,address,phone,email]
    for i,v in quantities.items():
        header.append(i)
        data.append(v)
    last_entry_time, last_entry_id = get_last_entry(id)
    # print(current_datetime, id, last_entry_time, last_entry_id, "********")
    if ((last_entry_time is None) or ((current_datetime - last_entry_time) >= timedelta(seconds=60)) or (id != last_entry_id)) and (id !="") and (name !="") :
       
        with open('static/customer_data.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if csvfile.tell() == 0:
                writer.writerow(header)
            writer.writerow(data)

def get_last_entry(id):
    last_entry_time = None
    last_entry_id = None

    try:
        df = pd.read_csv("static/customer_data.csv")
        n = df[df["Customer_id"]==id]
        # print("#############",n)
        if len(n)>0:
            row_date = datetime.strptime(list(n["date"])[-1], "%Y-%m-%d")
            row_time = datetime.strptime(list(n["time"])[-1], "%H:%M").time()
            row_datetime = datetime.combine(row_date, row_time)
            last_entry_time = row_datetime
            last_entry_id = id
    except (FileNotFoundError, IndexError, ValueError):
        pass

    return last_entry_time, last_entry_id
def putText(frame, text ,text_x=5,text_y = 20,font_scale = 1,thickness  = 1,font_color = (0,0,255)):
   
    font = cv2.FONT_HERSHEY_SIMPLEX   

    # Get the size of the text
    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)

    # Calculate the coordinates of the top-left corner for the text and background rectangle

    rect_x = text_x
    rect_y = text_y - text_size[1]  # Place the rectangle above the text

    # Calculate the bottom-right corner of the background rectangle
    rect_width = text_size[0]
    rect_height = text_size[1]

    # Draw the black background rectangle
    cv2.rectangle(frame, (rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height), (0, 0, 0), cv2.FILLED)

    # Draw the text on top of the background
    cv2.putText(frame, text, (text_x, text_y), font, font_scale, font_color, thickness)
    return frame
def get_customer_data(id):
    df = pd.read_csv("static/customer_data.csv")
    n = df[df["Customer_id"]==id]
    if len(n)>0:
        row_date = datetime.strptime(list(n["date"])[-1], "%Y-%m-%d")
        row_time = datetime.strptime(list(n["time"])[-1], "%H:%M").time()
        person_name = list(n["name"])[-1]
        person_email = list(n["email"])[-1]
        person_phone = list(n["phone"])[-1]
        person_address = list(n["address"])[-1]
        return row_date, row_time, person_name, person_email, person_phone, person_address
    else:
        return None, None, None, None, None, None
    
