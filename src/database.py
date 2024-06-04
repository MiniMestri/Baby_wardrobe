import sqlite3
import sys
import os
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from datetime import datetime, timedelta


if getattr(sys, 'frozen', False):
    base_dir = os.path.join(sys._MEIPASS, 'bbdd')
else:
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bbdd')

if not os.path.exists(base_dir):
    os.makedirs(base_dir)

ruta_bbdd = os.path.join(base_dir, 'login.sqlite3')


print("eta es una bbdd"+ruta_bbdd)

def create_connection():
    try:
        return sqlite3.connect(ruta_bbdd)
    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None


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
        nombre_usuario TEXT NOT NULL,
        nombre TEXT NOT NULL,
        altura REAL,
        circunferencia_pecho REAL,
        circunferencia_cintura REAL,
        largo_torso REAL,
        largo_pierna REAL,
        fecha_medicion DATE,
        FOREIGN KEY(nombre_usuario) REFERENCES login(username)
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medidas_prenda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        prenda TEXT NOT NULL,
        nombre_personalizado TEXT,
        imagen TEXT,
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


def save_measurements(username, name, height, chest_circumference, waist_circumference, torso_length, leg_length):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM medidas_bebe WHERE nombre_usuario = ? AND nombre = ?", (username, name))
    if cursor.fetchone():
        cursor.execute('''UPDATE medidas_bebe SET altura = ?, circunferencia_pecho = ?, circunferencia_cintura = ?, largo_torso = ?, largo_pierna = ?, fecha_medicion = ?
                          WHERE nombre_usuario = ? AND nombre = ?''',
                       (height, chest_circumference, waist_circumference, torso_length, leg_length, datetime.now(), username, name))
    else:
        cursor.execute('''INSERT INTO medidas_bebe (nombre_usuario, nombre, altura, circunferencia_pecho, circunferencia_cintura, largo_torso, largo_pierna, fecha_medicion)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (username, name, height, chest_circumference, waist_circumference, torso_length, leg_length, datetime.now()))
    connection.commit()
    connection.close()

def save_measurements_clothing(username, clothing_type, wardrobe_name, custom_name, image, height, chest_circumference, waist_circumference, torso_length, leg_length):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO medidas_prenda (nombre, prenda, nombre_armario, nombre_personalizado, imagen, altura_prenda, circunferencia_pecho_prenda, circunferencia_cintura_prenda, largo_torso_prenda, largo_pierna_prenda)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (username, clothing_type, wardrobe_name, custom_name, image, height, chest_circumference, waist_circumference, torso_length, leg_length))
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
    WHERE nombre_usuario = ?
    ORDER BY id DESC
    LIMIT 1
    ''', (username,))
    measurements = cursor.fetchone()
    connection.close()
    return measurements

def get_clothes_in_wardrobe(username, wardrobe_name):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, prenda FROM medidas_prenda WHERE nombre = ? AND nombre_armario = ?", (username, wardrobe_name))
    clothes = [(row[0], row[1]) for row in cursor.fetchall()]
    connection.close()
    return clothes


def get_clothing_info(clothing_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''
    SELECT prenda, nombre_personalizado, imagen, altura_prenda, circunferencia_pecho_prenda, circunferencia_cintura_prenda, largo_torso_prenda, largo_pierna_prenda
    FROM medidas_prenda
    WHERE id = ?
    ''', (clothing_id,))
    row = cursor.fetchone()
    connection.close()
    if row:
        return {
            'type': row[0],
            'custom_name': row[1],
            'image': row[2],
            'height': row[3],
            'chest_circumference': row[4],
            'waist_circumference': row[5],
            'torso_length': row[6],
            'leg_length': row[7]
        }
    return None


def delete_clothing_from_wardrobe(clothing_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM medidas_prenda WHERE id = ?", (clothing_id,))
    connection.commit()
    connection.close()

def get_clothes_by_category(username, category):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, prenda FROM medidas_prenda WHERE nombre = ? AND prenda = ?", (username, category))
    clothes = [(row[0], row[1]) for row in cursor.fetchall()]
    connection.close()
    return clothes

def update_clothing_details(clothing_id, type, custom_name, image, height, chest_circumference, waist_circumference, torso_length, leg_length):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''
    UPDATE medidas_prenda
    SET prenda = ?, nombre_personalizado = ?, imagen = ?, altura_prenda = ?, circunferencia_pecho_prenda = ?, circunferencia_cintura_prenda = ?, largo_torso_prenda = ?, largo_pierna_prenda = ?
    WHERE id = ?
    ''', (type, custom_name, image, height, chest_circumference, waist_circumference, torso_length, leg_length, clothing_id))
    connection.commit()
    connection.close()

def get_all_clothes(username):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM medidas_prenda WHERE nombre = ?", (username,))
    clothes = cursor.fetchall()
    connection.close()
    return clothes

def get_existing_names(username):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT nombre FROM medidas_bebe WHERE nombre_usuario = ?", (username,))
    names = [row[0] for row in cursor.fetchall()]
    connection.close()
    return names


def get_baby_measurements(username, baby_name):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''
    SELECT nombre, altura, circunferencia_pecho, circunferencia_cintura, largo_torso, largo_pierna
    FROM medidas_bebe
    WHERE nombre_usuario = ? AND nombre = ?
    ORDER BY id DESC
    LIMIT 1
    ''', (username, baby_name))
    measurements = cursor.fetchone()
    connection.close()
    return measurements

def check_for_reminders(username):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''
    SELECT nombre, fecha_medicion
    FROM medidas_bebe
    WHERE nombre_usuario = ?
    ''', (username,))
    records = cursor.fetchall()
    connection.close()

    reminders = []
    for record in records:
        baby_name, last_measurement_date = record
        if last_measurement_date:
            last_measurement_date = datetime.strptime(last_measurement_date, "%Y-%m-%d %H:%M:%S")
            if datetime.now() - last_measurement_date > timedelta(days=1):
                reminders.append(baby_name)

    if reminders:
        reminder_text = "Es momento de actualizar las medidas de: " + ", ".join(reminders)
        popup = Popup(title='Recordatorio de Crecimiento',
                      content=Label(text=reminder_text),
                      size_hint=(None, None), size=(400, 400))
        popup.open()



create_tables()