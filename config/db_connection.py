import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Add absolute path to .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

def get_connection():
    try:
        con = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        if con.is_connected():
            return con
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None
