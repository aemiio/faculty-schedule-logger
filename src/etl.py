import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime
import json 
from config.db_connection import get_connection

def extract():
    print("Extracting data... ")
    time_logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Time Logs')
    file_path = os.path.join(time_logs_dir, 'time_logs_.xlsx')
    
    try:
        df = pd.read_excel(file_path)
        print("Data extracted successfully")
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def get_employee_schedule(emp_num, cursor):
    query = 'SELECT schedule FROM faculty_schedule WHERE emp_num = %s'
    cursor.execute(query, (emp_num,))
    result = cursor.fetchone()
    if result and result[0]:
        return pd.json_normalize(json.loads(result[0]))
    return None

def calculate_hours_rendered(time_in, time_out, schedule_time_blocks):
    time_in = datetime.strptime(time_in, '%H:%M:%S')
    time_out = datetime.strptime(time_out, '%H:%M:%S')
    
    schedule_parts = schedule_time_blocks.split(' - ')
    sched_start = datetime.strptime(schedule_parts[0], '%I:%M %p')
    sched_end = datetime.strptime(schedule_parts[1], '%I:%M %p')
    
    scheduled_hours = (sched_end - sched_start).seconds / 3600
    actual_hours = (time_out - time_in).seconds / 3600
    
    return min(actual_hours, scheduled_hours)

def transform(df, cursor):
    print("Transforming data... ")
    transformed_data = []
    
    for i, row in df.iterrows():
        emp_num = row['Emp. Num']
        emp_name = row['Emp. Name']
        day = row['day_of_week'].strip()
        
        if pd.isna(row['Time In']) or pd.isna(row['Time Out']):
            print(f"Skipping row {i}: Missing time values")
            continue
        
        # Convert Timedelta to string time format
        time_in = str(row['Time In']).split()[-1]  # Get HH:MM:SS part
        time_out = str(row['Time Out']).split()[-1]
        
        schedule = get_employee_schedule(emp_num, cursor)
        if schedule is None:
            print(f"No schedule found for employee {emp_num}")
            continue
            
        day_schedule = schedule[schedule['days'].str.contains(day, na=False)]
        if day_schedule.empty:
            print(f"No schedule found for employee {emp_num} on {day}")
            continue
            
        time_blocks = day_schedule.iloc[0]['time_blocks']
        hrs_rendered = calculate_hours_rendered(time_in, time_out, time_blocks)
        
        transformed_data.append({
            'emp_num': emp_num,
            'emp_name': emp_name,
            'schedule_day': day,
            'date': row['Date'],
            'time_in': time_in,
            'time_out': time_out,
            'hrs_rendered': round(hrs_rendered, 2)
        })
        print(f"Processed row {i} successfully")
    
    print(f"\nTransformed {len(transformed_data)} rows")
    return pd.DataFrame(transformed_data)

def load(df, cursor, con):
    print("Loading data... ")
    for _, row in df.iterrows():
        cursor.execute('''
            SELECT COUNT(*) FROM etl_time_logs 
            WHERE emp_num = %s AND date = %s
        ''', (row['emp_num'], row['date']))
        
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO etl_time_logs 
                (emp_num, emp_name, schedule_day, date, time_in, time_out, hrs_rendered)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                row['emp_num'],
                row['emp_name'],
                row['schedule_day'],
                row['date'],
                row['time_in'],
                row['time_out'],
                row['hrs_rendered']
            ))
    
    con.commit()
    print("Data loaded successfully")

def etl():
    con = get_connection()
    cursor = con.cursor()
    cursor.execute('USE facultydb')

    try:
        df = extract()
        if df is None:
            return

        transformed_df = transform(df, cursor)
        if transformed_df.empty:
            print("No data to load after transformation")
            return

        load(transformed_df, cursor, con)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if con.is_connected():
            cursor.close()
            con.close()
            print("Database connection closed")

if __name__ == "__main__":
    etl()
