from database import conectar
from datetime import datetime


RECOMPENSAS = [
    {
        "id": 1,
        "nombre": "Insignia Verde",
        "descripcion": "Reconocimiento por contribuir al reciclaje.",
        "puntos": 50
    },
    {
        "id": 2,
        "nombre": "Reconocimiento Ecológico",
        "descripcion": "Premio por compromiso con el medio ambiente.",
        "puntos": 100
    },
    {
        "id": 3,
        "nombre": "Kit Ecológico",
        "descripcion": "Recompensa especial por reciclar.",
        "puntos": 200
    }
]


def crear_tabla_canjes():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS canjes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            recompensa TEXT NOT NULL,
            puntos INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    conexion.commit()
    conexion.close()


def obtener_puntos_disponibles(usuario_id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(puntos), 0)
        FROM reciclaje
        WHERE usuario_id = ?
    """, (usuario_id,))

    puntos_ganados = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(puntos), 0)
        FROM canjes
        WHERE usuario_id = ?
    """, (usuario_id,))

    puntos_gastados = cursor.fetchone()[0]

    conexion.close()

    return puntos_ganados - puntos_gastados


def canjear_recompensa(usuario_id, recompensa):

    crear_tabla_canjes()

    puntos_disponibles = obtener_puntos_disponibles(usuario_id)

    if puntos_disponibles < recompensa["puntos"]:
        return False, "No tenés suficientes puntos."

    conexion = conectar()
    cursor = conexion.cursor()

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO canjes
        (usuario_id, recompensa, puntos, fecha)
        VALUES (?, ?, ?, ?)
    """, (
        usuario_id,
        recompensa["nombre"],
        recompensa["puntos"],
        fecha
    ))

    conexion.commit()
    conexion.close()

    return True, "¡Recompensa canjeada correctamente!"


def obtener_historial_canjes(usuario_id=None):

    crear_tabla_canjes()

    conexion = conectar()
    cursor = conexion.cursor()

    if usuario_id is None:

        cursor.execute("""
            SELECT usuarios.nombre,
                   canjes.recompensa,
                   canjes.puntos,
                   canjes.fecha
            FROM canjes
            INNER JOIN usuarios
            ON canjes.usuario_id = usuarios.id
            ORDER BY canjes.id DESC
        """)

    else:

        cursor.execute("""
            SELECT usuarios.nombre,
                   canjes.recompensa,
                   canjes.puntos,
                   canjes.fecha
            FROM canjes
            INNER JOIN usuarios
            ON canjes.usuario_id = usuarios.id
            WHERE canjes.usuario_id = ?
            ORDER BY canjes.id DESC
        """, (usuario_id,))

    resultados = cursor.fetchall()
    conexion.close()

    return resultados


crear_tabla_canjes()