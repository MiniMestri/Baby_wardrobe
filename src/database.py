import sqlite3

def create_connection():
    connection = sqlite3.connect("C:/Users/fonsi/Desktop/ESTUDIO/IMF 2/TFG/Baby_wardrobe/bbdd/login.sqlite3")
    return connection

def create_table():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS login (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL)''')
    connection.commit()
    connection.close()

def add_user(username, password):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO login (username, password) VALUES (?, ?)", (username, password))
    connection.commit()
    connection.close()

def validate_user(username, password):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM login WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    connection.close()
    return user

create_table()