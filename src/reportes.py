from database import conectar


def obtener_historial():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT 
            usuarios.nombre,
            reciclaje.material,
            reciclaje.cantidad,
            reciclaje.puntos,
            reciclaje.fecha
        FROM reciclaje
        INNER JOIN usuarios
        ON reciclaje.usuario_id = usuarios.id
        ORDER BY reciclaje.id DESC
    """)

    resultados = cursor.fetchall()
    conexion.close()

    return resultados


def residuos_por_material():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT material, SUM(cantidad)
        FROM reciclaje
        GROUP BY material
    """)

    resultados = cursor.fetchall()
    conexion.close()

    return resultados