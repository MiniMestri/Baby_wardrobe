import sqlite3

def create_connection():
    return sqlite3.connect("C:/Users/fonsi/Desktop/ESTUDIO/IMF 2/TFG/Baby_wardrobe/bbdd/login.sqlite3")


def create_tables():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS login (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medidas_bebe (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        altura REAL,
        circunferencia_pecho REAL,
        circunferencia_cintura REAL,
        largo_torso REAL,
        largo_pierna REAL,
        FOREIGN KEY(nombre) REFERENCES login(username)
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medidas_prenda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        prenda TEXT NOT NULL,
        nombre_armario TEXT NOT NULL,
        altura_prenda REAL,
        circunferencia_pecho_prenda REAL,
        circunferencia_cintura_prenda REAL,
        largo_torso_prenda REAL,
        largo_pierna_prenda REAL,
        FOREIGN KEY(nombre) REFERENCES login(username),
        FOREIGN KEY(nombre_armario) REFERENCES armarios(nombre_armario)
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS armarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        nombre_armario TEXT NOT NULL,
        FOREIGN KEY(username) REFERENCES login(username)
    )''')
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

def change_password(username, old_password, new_password):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM login WHERE username = ? AND password = ?", (username, old_password))
    if cursor.fetchone():
        cursor.execute("UPDATE login SET password = ? WHERE username = ?", (new_password, username))
        connection.commit()
        connection.close()
        return True
    connection.close()
    return False


def save_measurements(username, height, chest_circumference, waist_circumference, torso_length, leg_length):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM medidas_bebe WHERE nombre = ?", (username,))
    if cursor.fetchone():
        cursor.execute('''UPDATE medidas_bebe SET altura = ?, circunferencia_pecho = ?, circunferencia_cintura = ?, largo_torso = ?, largo_pierna = ?
                          WHERE nombre = ?''',
                       (height, chest_circumference, waist_circumference, torso_length, leg_length, username))
    else:
        cursor.execute('''INSERT INTO medidas_bebe (nombre, altura, circunferencia_pecho, circunferencia_cintura, largo_torso, largo_pierna)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (username, height, chest_circumference, waist_circumference, torso_length, leg_length))
    connection.commit()
    connection.close()

def get_existing_names():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT nombre FROM medidas_bebe")
    names = [row[0] for row in cursor.fetchall()]
    connection.close()
    return names

def save_measurements_clothing(username, clothing_type, wardrobe_name, height, chest_circumference, waist_circumference, torso_length, leg_length):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO medidas_prenda (nombre, prenda, nombre_armario, altura_prenda, circunferencia_pecho_prenda, circunferencia_cintura_prenda, largo_torso_prenda, largo_pierna_prenda)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (username, clothing_type, wardrobe_name, height, chest_circumference, waist_circumference, torso_length, leg_length))
        connection.commit()
    except sqlite3.Error as e:
        raise Exception(f"Error al guardar las medidas de la prenda: {e}")
    finally:
        connection.close()

def add_wardrobe(username, wardrobe_name):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO armarios (username, nombre_armario) VALUES (?, ?)", (username, wardrobe_name))
    connection.commit()
    connection.close()

def get_wardrobes(username):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT nombre_armario FROM armarios WHERE username = ?", (username,))
    wardrobes = [row[0] for row in cursor.fetchall()]
    connection.close()
    return wardrobes

def delete_wardrobe(username, wardrobe_name):
    connection = create_connection()
    cursor = connection.cursor()
    # Primero, elimina las prendas asociadas al armario
    cursor.execute("DELETE FROM medidas_prenda WHERE nombre = ? AND nombre_armario = ?", (username, wardrobe_name))
    # Luego, elimina el armario
    cursor.execute("DELETE FROM armarios WHERE username = ? AND nombre_armario = ?", (username, wardrobe_name))
    connection.commit()
    connection.close()

def get_wardrobe_count(username):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM armarios WHERE username = ?", (username,))
    count = cursor.fetchone()[0]
    connection.close()
    return count

def get_clothing_count_per_wardrobe(username):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT nombre_armario, COUNT(*) FROM medidas_prenda WHERE nombre = ? GROUP BY nombre_armario", (username,))
    data = cursor.fetchall()
    connection.close()
    return data

def get_latest_baby_measurements(username):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''
    SELECT nombre, altura, circunferencia_pecho, circunferencia_cintura, largo_torso, largo_pierna
    FROM medidas_bebe
    WHERE nombre = ?
    ORDER BY id DESC
    LIMIT 1
    ''', (username,))
    measurements = cursor.fetchone()
    connection.close()
    return measurements

create_tables()