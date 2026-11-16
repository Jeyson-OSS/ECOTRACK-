from database import conectar
from datetime import datetime


PUNTOS_POR_KILO = {
    "Plástico": 10,
    "Papel": 5,
    "Cartón": 5,
    "Vidrio": 8,
    "Metal": 15
}


def registrar_reciclaje(usuario_id, material, cantidad):

    conexion = conectar()
    cursor = conexion.cursor()

    puntos = int(cantidad * PUNTOS_POR_KILO[material])
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO reciclaje
        (usuario_id, material, cantidad, puntos, fecha)
        VALUES (?, ?, ?, ?, ?)
    """, (usuario_id, material, cantidad, puntos, fecha))

    conexion.commit()
    conexion.close()

    return puntos