import csv
from datetime import datetime, timedelta
import pandas as pd
def save_customer_data(name):
    current_datetime = datetime.now()
    current_year = current_datetime.year
    current_date = current_datetime.date()
    current_time = current_datetime.time().strftime("%H:%M")

    data = [current_year, current_date, current_time, name]
    header = ["year", "date", "time", "Customer_id"]
    last_entry_time, last_entry_name = get_last_entry(name)
    # print(current_datetime, name, last_entry_time, last_entry_name, "********")
    if (last_entry_time is None) or ((current_datetime - last_entry_time) >= timedelta(hours=1)) or (name != last_entry_name):
        with open('static/customer_data.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if csvfile.tell() == 0:
                writer.writerow(header)
            writer.writerow(data)

def get_last_entry(name):
    last_entry_time = None
    last_entry_name = None

    try:
        df = pd.read_csv("static/customer_data.csv",names = ["year","date","time","Customer_id"])
        n = df[df["Customer_id"]==name]
        # print("#############",n)
        if len(n)>0:
            row_date = datetime.strptime(list(n["date"])[-1], "%Y-%m-%d")
            row_time = datetime.strptime(list(n["time"])[-1], "%H:%M").time()
            row_datetime = datetime.combine(row_date, row_time)
            last_entry_time = row_datetime
            last_entry_name = name
    except (FileNotFoundError, IndexError, ValueError):
        pass

    return last_entry_time, last_entry_name
