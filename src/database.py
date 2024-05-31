import sqlite3

def create_connection():
    return sqlite3.connect("C:/Users/fonsi/Desktop/ESTUDIO/IMF 2/TFG/Baby_wardrobe/bbdd/login.sqlite3")

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

def save_measurements_clothing(username, height, chest_circumference, waist_circumference, torso_length, leg_length):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO medidas_prenda (nombre_prenda, altura_prenda, circunferencia_pecho_prenda, circunferencia_cintura_prenda, largo_torso_prenda, largo_pierna_prenda)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (username, height, chest_circumference, waist_circumference, torso_length, leg_length))
    connection.commit()
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

