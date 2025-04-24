import sqlite3

DB_NAME = "patients.db"

# 🔄 Create the table if not exists
def create_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            lastname TEXT,
            age INTEGER,
            city TEXT,
            state TEXT,
            pincode TEXT,
            xray_date TEXT,
            mobile TEXT,
            email TEXT,
            image_path TEXT,
            result TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ✅ Insert new patient
def insert_patients(name, lastname, age, city, state, pincode, xray_date, mobile, email, image_path, result):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO patients (name, lastname, age, city, state, pincode, xray_date, mobile, email, image_path, result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, lastname, age, city, state, pincode, xray_date, mobile, email, image_path, result))
    conn.commit()
    conn.close()

# ✅ Fetch all patients
def get_all_patients():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM patients")
    data = c.fetchall()
    conn.close()
    return data

# Automatically create table when imported
create_table()
