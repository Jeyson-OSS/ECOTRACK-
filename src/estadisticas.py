from database import conectar


def total_reciclado():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT SUM(cantidad) FROM reciclaje")
    resultado = cursor.fetchone()[0]

    conexion.close()
    return resultado or 0


def total_puntos():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT SUM(puntos) FROM reciclaje")
    resultado = cursor.fetchone()[0]

    conexion.close()
    return resultado or 0


def total_usuarios():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    resultado = cursor.fetchone()[0]

    conexion.close()
    return resultado