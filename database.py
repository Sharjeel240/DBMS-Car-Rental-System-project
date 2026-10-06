import mysql.connector
from mysql.connector import Error

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',        # Replace with your MySQL username
    'password': '12345678',# Replace with your MySQL password
    'database': 'car_rental_db'
}

def get_connection():
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def execute_query(query, params=()):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def fetch_all(query, params=()):
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_raw_query(query):
    """Executes arbitrary SQL queries for the live database inspector inside the app."""
    conn = get_connection()
    if not conn:
        return [], []
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [col[0] for col in cursor.description] if cursor.description else []
    rows = cursor.fetchall() if cursor.description else []
    conn.close()
    return columns, rows