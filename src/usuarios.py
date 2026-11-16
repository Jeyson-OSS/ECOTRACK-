from database import conectar


def registrar_usuario(nombre, usuario, contraseña, rol="usuario"):
    conexion = conectar()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            INSERT INTO usuarios (nombre, usuario, contraseña, rol)
            VALUES (?, ?, ?, ?)
        """, (nombre, usuario, contraseña, rol))

        conexion.commit()
        return True

    except Exception as error:
        print("Error:", error)
        return False

    finally:
        conexion.close()


def obtener_usuarios():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    conexion.close()
    return usuarios