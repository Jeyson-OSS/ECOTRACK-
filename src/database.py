import sqlite3
import os

RUTA_DB = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "database",
    "ecotrack.db"
)

def conectar():
    return sqlite3.connect(RUTA_DB)


def crear_tablas():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            contraseña TEXT NOT NULL,
            rol TEXT DEFAULT 'usuario'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reciclaje (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            material TEXT NOT NULL,
            cantidad REAL NOT NULL,
            puntos INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    conexion.commit()
    conexion.close()


if __name__ == "__main__":
    crear_tablas()
    print("Base de datos ECOTRACK creada correctamente.")