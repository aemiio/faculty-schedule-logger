import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from mysql.connector import Error
from config.db_connection import get_connection

def init_db():
    con = get_connection()
    cursor = con.cursor()

    try:
        cursor.execute('CREATE DATABASE IF NOT EXISTS facultydb')
        cursor.execute('USE facultydb')

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            dept_id INT PRIMARY KEY,
            dept_name VARCHAR(50)
        )
        """)

        query = '''
            INSERT IGNORE INTO departments (dept_id, dept_name)
            VALUES 
            (1, "Department of Business Administration"),
            (2, "Department of Engineering"),
            (3, "Department of Computer Studies"),
            (4, "Department of Hospitality Management"),
            (5, "Department of Teacher Education"),
            (6, "Department of Industrial Technology")
        '''
        cursor.execute(query)
        con.commit()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty_schedule (
            emp_num INT PRIMARY KEY,
            emp_name VARCHAR(100) NOT NULL,
            department INT,
            schedule JSON,
            FOREIGN KEY (department) REFERENCES departments(dept_id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS input_time_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            emp_num INT NOT NULL,
            emp_name VARCHAR(100),
            day_of_week VARCHAR(10),
            date DATE,
            time_in TIME,
            time_out TIME,
            FOREIGN KEY (emp_num) REFERENCES faculty_schedule(emp_num)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS etl_time_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            emp_num INT NOT NULL,
            emp_name VARCHAR(100),
            schedule_day CHAR(1),
            date DATE,
            time_in TIME,
            time_out TIME,
            hrs_rendered FLOAT,
            FOREIGN KEY (emp_num) REFERENCES faculty_schedule(emp_num)
        )
        """)

    except Error as e:  
        print(f"Error: {e}")

    finally:
        if con.is_connected():
            cursor.close()
            con.close()

def setup_db(data=None):
    init_db()
    
    if data:
        con = get_connection()
        cursor = con.cursor()
        try:
            cursor.execute('USE facultydb')
            # Insert data into faculty_schedule
            query = '''
                INSERT IGNORE INTO faculty_schedule (emp_num, emp_name, department, schedule)
                VALUES (%s, %s, %s, %s)
            '''

            for record in data:
                schedule_data = {
                    "days": record['schedule'][0]['days'],
                    "time_blocks": record['schedule'][0]['time_blocks']
                }

                schedule_json = json.dumps(schedule_data)

                values = (record['emp_num'], record['emp_name'], record['department'], schedule_json)
                cursor.execute(query, values)

            con.commit()
            print(f"{cursor.rowcount} rows were inserted into faculty_schedule.")

        except Error as e:
            print(f"Error: {e}")

        finally:
            if con.is_connected():
                cursor.close()
                con.close()


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_file_path = os.path.join(base_dir, '..', 'data', 'data.json')

    try:
        with open(data_file_path, 'r') as file:
            data = json.load(file)
        setup_db(data)
    except FileNotFoundError:
        print(f"Warning: {data_file_path} not found. Only initializing database structure.")
        setup_db()
