import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mysql.connector import Error
from config.db_connection import get_connection
from tabulate import tabulate
from config.setup_db import setup_db
from openpyxl import Workbook
import json

con = get_connection()
cursor = con.cursor()


# CRUD OPERATIONS
def insert_schedule():
    print('Inserting Schedule...')
    emp_no = int(input("Enter Employee Number: "))
    
    cursor.execute("USE facultydb")
    cursor.execute("SELECT emp_num FROM faculty_schedule WHERE emp_num = %s", (emp_no,))
    if cursor.fetchone():
        print(f"Employee #{emp_no} already exists in the database.")
        choice = input("Enter 'B' to go back or any other key to exit: ")
        if choice.upper() == 'B':
            return
        else:
            print("Exiting...")
            sys.exit()
    
    name = input(f'Enter employee name for {emp_no}: ')
    department = int(input(f'''Enter Department for {name}: 
        1: Department of Business Administration\n
        2: Department of Computer Studies\n
        3: Department of Hospitality Management\n
        4: Department of Teacher Education\n
        5: Department of Industrial Technology\n                                        
    '''))
    
    schedule = []
    
    while True:
        days = input("Enter schedule days (e.g., 'M-W' for Monday to Wednesday, 'M, T, W' for individual days) or type 'done' to finish: ")
        if days.lower() == 'done':
            break
        time_block = input(f"Enter time block for {days} (e.g., '1:00 PM - 5:00 PM'): ")
        
        schedule.append({
            "days": days.strip(),
            "time_blocks": time_block.strip()
        })
    
    # Convert the schedule list to a JSON string
    schedule_json = json.dumps(schedule)
    
    query = '''
        INSERT INTO faculty_schedule (emp_num, emp_name, department, schedule)
        VALUES (%s, %s, %s, %s)
    '''
    cursor.execute(query, (emp_no, name, department, schedule_json))
    con.commit()
    
    print("Schedule added successfully!")


def view_schedule():
    print('Viewing Schedule...')
    emp_no = int(input("Enter Employee Number (or 0 for all): "))

    cursor.execute("USE facultydb")

    if emp_no == 0:
        query = '''
            SELECT fs.emp_num, fs.emp_name, fs.department, fs.schedule
            FROM faculty_schedule fs
            ORDER BY fs.emp_num
        '''
        cursor.execute(query)
        rows = cursor.fetchall()
        
        schedule_data = []
        for row in rows:
            emp_num = row[0]
            emp_name = row[1]
            schedule_json = json.loads(row[3])
            
            if isinstance(schedule_json, list):
                schedules = schedule_json
            else:
                schedules = [schedule_json]
                
            for schedule_item in schedules:
                days = schedule_item.get('days', '')
                time_blocks = schedule_item.get('time_blocks', '')
                schedule_data.append([emp_num, emp_name, days, time_blocks])

        headers = ['Emp. Num', 'Name', 'Days', 'Time Block']
        print(tabulate(schedule_data, headers, tablefmt="grid"))
        
    else:
        # Show calendar format for individual employee
        query = '''
            SELECT fs.emp_num, fs.emp_name, fs.department, fs.schedule
            FROM faculty_schedule fs
            WHERE fs.emp_num = %s
        '''
        cursor.execute(query, (emp_no,))
        row = cursor.fetchone()
        
        if not row:
            print("No schedule found for this employee.")
            return
            
        emp_num = row[0]
        emp_name = row[1]
        schedule_json = json.loads(row[3])
        
        # Initialize empty time blocks for each day
        schedule_data = {
            'M': '-',
            'T': '-',
            'W': '-',
            'TH': '-',
            'F': '-'
        }
        
        # Fill in the schedule
        if isinstance(schedule_json, list):
            schedules = schedule_json
        else:
            schedules = [schedule_json]
            
        for schedule_item in schedules:
            days = schedule_item.get('days', '')
            time_block = schedule_item.get('time_blocks', '')
            
            # Split days and remove whitespace
            day_list = [d.strip() for d in days.split(',')]
            
            # Update schedule_data for each day
            for day in day_list:
                if day in schedule_data:
                    schedule_data[day] = time_block
        
        # Create the display data
        display_data = [[
            emp_name,
            schedule_data['M'],
            schedule_data['T'],
            schedule_data['W'],
            schedule_data['TH'],
            schedule_data['F']
        ]]
        
        headers = ['Name', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        print(f"\nSchedule for Employee #{emp_num}:")
        print(tabulate(display_data, headers, tablefmt="grid"))



def update_schedule():
    print('Updating Schedule...')
    emp_num = int(input("Enter employee number to edit schedule: "))

    cursor.execute("SELECT * FROM faculty_schedule WHERE emp_num = %s", (emp_num,))
    row = cursor.fetchone()

    if row:
        
        schedule = json.loads(row[3]) 
        
        
        print("Current Schedule:")
        for schedule_item in schedule:
            print(f"Days: {schedule_item['days']} | Time Blocks: {schedule_item['time_blocks']}")

       
        new_schedule_code = input("Enter new schedule code (e.g., 'MT' for Monday-Tuesday): ").strip()
        new_time_block = input("Enter new time blocks (e.g., '1:00 PM - 5:00 PM, 7:00 AM - 12:00 PM'): ").strip()

        
        updated_schedule = []
        days_list = new_schedule_code.split(",")
        time_blocks_list = new_time_block.split(",")
        
        for i in range(len(days_list)):
            updated_schedule.append({
                "days": days_list[i].strip(),
                "time_blocks": time_blocks_list[i].strip() if i < len(time_blocks_list) else ""
            })

        
        updated_schedule_json = json.dumps(updated_schedule)

        
        query = '''
            UPDATE faculty_schedule
            SET schedule = %s
            WHERE emp_num = %s
        '''
        cursor.execute(query, (updated_schedule_json, emp_num))
        con.commit()

        print(f"{emp_num}'s schedule has been updated.")
    else:
        print("Employee number not found.")

def delete_schedule():
    print('Deleting Schedule or Faculty...')

    emp_num = input("Enter employee number to delete schedule or faculty: ")
    choice = input("Enter '1' to delete the schedule, or '2' to delete the faculty: ")

    con = get_connection()
    cursor = con.cursor()

    cursor.execute("USE facultydb")
    cursor.execute("SELECT * FROM faculty_schedule WHERE emp_num = %s", (emp_num,))
    row = cursor.fetchone()

    if row:
        if choice == '1':
            query = '''
            UPDATE faculty_schedule
            SET schedule = NULL
            WHERE emp_num = %s
            '''
            cursor.execute(query, (emp_num,))
            con.commit()
            print(f"Schedule for employee number {emp_num} has been cleared.")
        
        elif choice == '2':
            query = '''
            DELETE FROM faculty_schedule WHERE emp_num = %s
            '''
            cursor.execute(query, (emp_num,))
            con.commit()
            print(f"Faculty with employee number {emp_num} has been deleted.")

        else:
            print("Invalid choice. Please enter '1' to delete the schedule or '2' to delete the faculty.")
    
    else:
        print("Employee number not found.")

def insert_time_log():
    print('Logging Time-In/Out...')

    emp_num = int(input("Enter employee number: "))
    emp_name = input("Enter employee name: ")
    day_of_week = input("Enter day of the week (e.g., 'M', 'T', 'W', etc.): ")
    date = input("Enter date (YYYY-MM-DD): ")
    time_in = input("Enter time in (24-hour format HH:MM:SS): ")
    time_out = input("Enter time out (24-hour format HH:MM:SS): ")

    cursor.execute("USE facultydb")
    cursor.execute("SELECT * FROM faculty_schedule WHERE emp_num = %s", (emp_num,))
    row = cursor.fetchone()

    if row:
        try:
            schedule_json = json.loads(row[3])  
            
            if not isinstance(schedule_json, list):
                schedule_json = [schedule_json]
            
            day_exists = False
            for schedule_item in schedule_json:
                if isinstance(schedule_item, dict) and 'days' in schedule_item:
                    schedule_days = [d.strip() for d in schedule_item['days'].split(',')]
                    if day_of_week in schedule_days:
                        day_exists = True
                        break

            if day_exists:
                query = '''
                    INSERT INTO input_time_logs (emp_num, emp_name, day_of_week, date, time_in, time_out)
                    VALUES (%s, %s, %s, %s, %s, %s)
                '''
                cursor.execute(query, (emp_num, emp_name, day_of_week, date, time_in, time_out))
                con.commit()

                print("Time log added successfully!")
            else:
                print(f"Error: {day_of_week} is not part of {emp_num}'s schedule.")
        except Error as e:
            print(f"Error processing schedule data: {e}")
    else:
        print("Employee number not found.")
        
def view_time_log():
    print('Viewing Time-In/Out...')
    emp_no = int(input("Enter Employee Number (or 0 for all): "))

    cursor.execute("USE facultydb")

    if emp_no == 0:
        query = '''
            SELECT etl.emp_num, fs.emp_name, etl.schedule_day, etl.date, 
                   etl.time_in,
                   etl.time_out,
                   etl.hrs_rendered
            FROM etl_time_logs etl
            JOIN faculty_schedule fs ON etl.emp_num = fs.emp_num
            ORDER BY etl.date DESC, etl.emp_num
        '''
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            print("No time logs found.")
            return
            
        time_log_data = []
        for row in rows:
            time_log_data.append([
                row[0],  
                row[1],  
                row[2],  
                row[3].strftime('%Y-%m-%d'),  
                row[4],  
                row[5],  
                f"{row[6]:.2f}"  
            ])

        headers = ['Emp. Num', 'Name', 'Day', 'Date', 'Time In', 'Time Out', 'Hours']
        print(tabulate(time_log_data, headers, tablefmt="grid"))
            
    else:
        query = '''
            SELECT etl.emp_num, fs.emp_name, etl.schedule_day, etl.date, 
                   etl.time_in,
                   etl.time_out,
                   etl.hrs_rendered
            FROM etl_time_logs etl
            JOIN faculty_schedule fs ON etl.emp_num = fs.emp_num
            WHERE etl.emp_num = %s
            ORDER BY etl.date DESC
        '''
        cursor.execute(query, (emp_no,))
        rows = cursor.fetchall()
        
        if not rows:
            print(f"No time logs found for employee #{emp_no}")
            return
            
        time_log_data = []
        for row in rows:
            time_log_data.append([
                row[2],  
                row[3].strftime('%Y-%m-%d'),  
                row[4], 
                row[5], 
                f"{row[6]:.2f}"  
            ])

        print(f"\nTime Logs for {rows[0][1]} (#{rows[0][0]}):")
        headers = ['Day', 'Date', 'Time In', 'Time Out', 'Hours']
        print(tabulate(time_log_data, headers, tablefmt="grid"))


def export_time_logs():
    cursor.execute("USE facultydb")
    query = '''
        SELECT itl.emp_num, itl.emp_name, itl.day_of_week, 
               itl.date, itl.time_in, itl.time_out
        FROM input_time_logs itl
        ORDER BY itl.emp_num, itl.date
    '''
    cursor.execute(query)
    rows = cursor.fetchall()

    if not rows:
        print("No time logs found to export.")
        return

    time_logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Time Logs')
    if not os.path.exists(time_logs_dir):
        os.makedirs(time_logs_dir)

    wb = Workbook()
    ws = wb.active
    ws.title = "Input Time Logs"
    
    headers = ['Emp. Num', 'Emp. Name', 'day_of_week', 'Date', 'Time In', 'Time Out']
    ws.append(headers)

    for row in rows:
        ws.append(row)

    file_name = f'time_logs_.xlsx'
    file_path = os.path.join(time_logs_dir, file_name)

    try:
        wb.save(file_path)
        print(f"Time logs exported to Time Logs/{file_name} successfully!")
    except Exception as e:
        print(f"Error saving file: {e}")



def main():
    try:
        setup_db()  
        cursor.execute('USE facultydb')

        while True:
            print("\nFaculty Schedule Management System")
            print("\n")
            print("1. Time-In/Out")
            print("2. Schedules")
            print("3. Export Time Logs")
            print("4. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                while True:
                    print("\nTime-In/Out")
                    print("1. Log Time-In/Out")
                    print("2. View Time-In/Out")
                    print("3. Back to Main Menu")
                    sub_choice = input("Enter your choice: ")

                    if sub_choice == "1":
                        insert_time_log()
                    elif sub_choice == "2":
                        view_time_log()
                    elif sub_choice == "3":
                        break
                    else:
                        print("Invalid choice. Please try again.")
            elif choice == "2":
                while True:  
                    print("\nSchedule Management")
                    print("1. Insert Schedule")
                    print("2. View Schedule")
                    print("3. Update Schedule")
                    print("4. Delete Schedule")
                    print("5. Back to Main Menu")
                    sub_choice = input("Enter your choice: ")

                    if sub_choice == "1":
                        insert_schedule()
                    elif sub_choice == "2":
                        view_schedule()
                    elif sub_choice == "3":
                        update_schedule()
                    elif sub_choice == "4":
                        delete_schedule()
                    elif sub_choice == "5":
                        break
                    else:
                        print("Invalid choice. Please try again.")
            elif choice == "3":
                export_time_logs()
            elif choice == "4":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
    except Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'con' in globals() and con.is_connected():
            cursor.close()
            con.close()
            print("\nDatabase connection closed.")

if __name__ == '__main__':
    main()