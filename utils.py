import csv
from datetime import datetime, timedelta

def save_customer_data(name):
    current_datetime = datetime.now()
    current_year = current_datetime.year
    current_date = current_datetime.date()
    current_time = current_datetime.time().strftime("%H:%M")

    data = [current_year, current_date, current_time, name]

    last_entry_time, last_entry_name = get_last_entry()
    print(current_datetime, name, last_entry_time, last_entry_name, "********")
    if (last_entry_time is None) or ((current_datetime - last_entry_time) >= timedelta(hours=1)) or (name != last_entry_name):
        with open('customer_data.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)

def get_last_entry():
    last_entry_time = None
    last_entry_name = None

    try:
        with open('customer_data.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 4:
                    row_date = datetime.strptime(row[1], "%Y-%m-%d")
                    row_time = datetime.strptime(row[2], "%H:%M").time()
                    row_datetime = datetime.combine(row_date, row_time)
                    if last_entry_time is None or row_datetime > last_entry_time:
                        last_entry_time = row_datetime
                        last_entry_name = row[3]
    except (FileNotFoundError, IndexError, ValueError):
        pass

    return last_entry_time, last_entry_name
