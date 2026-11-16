import os
from datetime import datetime

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure

from database import conectar
from estadisticas import total_reciclado, total_puntos, total_usuarios
from reportes import obtener_historial, residuos_por_material


def generar_reporte_pdf():

    # Ubicación del archivo PDF
    carpeta_proyecto = os.path.dirname(os.path.dirname(__file__))

    nombre_archivo = os.path.join(
        carpeta_proyecto,
        "Reporte_ECOTRACK.pdf"
    )

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Consultar información
    reciclado = total_reciclado()
    puntos = total_puntos()
    usuarios = total_usuarios()

    materiales = residuos_por_material()
    historial = obtener_historial()

    with PdfPages(nombre_archivo) as pdf:

        # =================================
        # PÁGINA 1: RESUMEN GENERAL
        # =================================

        figura = Figure(figsize=(8.27, 11.69))
        figura.patch.set_facecolor("white")

        ax = figura.add_subplot(111)
        ax.axis("off")

        ax.text(
            0.5, 0.94,
            "ECOTRACK",
            fontsize=30,
            fontweight="bold",
            color="#14532D",
            ha="center"
        )

        ax.text(
            0.5, 0.90,
            "Sistema Inteligente de Gestión de Residuos",
            fontsize=13,
            color="#64748B",
            ha="center"
        )

        ax.text(
            0.08, 0.82,
            "REPORTE GENERAL DE RECICLAJE",
            fontsize=17,
            fontweight="bold",
            color="#14532D"
        )

        ax.text(
            0.08, 0.77,
            f"Fecha de generación: {fecha}",
            fontsize=11
        )

        # Indicadores
        indicadores = [
            ("Residuos reciclados", f"{reciclado:.2f} kg"),
            ("Puntos acumulados", str(puntos)),
            ("Usuarios registrados", str(usuarios))
        ]

        posiciones = [0.68, 0.58, 0.48]

        for (titulo, valor), posicion in zip(
            indicadores, posiciones
        ):

            ax.text(
                0.10, posicion,
                titulo,
                fontsize=13,
                color="#64748B"
            )

            ax.text(
                0.75, posicion,
                valor,
                fontsize=16,
                fontweight="bold",
                color="#15803D",
                ha="center"
            )

        ax.text(
            0.08, 0.36,
            "RESUMEN POR MATERIAL",
            fontsize=16,
            fontweight="bold",
            color="#14532D"
        )

        ax.text(
            0.10, 0.31,
            "Material",
            fontsize=12,
            fontweight="bold"
        )

        ax.text(
            0.75, 0.31,
            "Cantidad (kg)",
            fontsize=12,
            fontweight="bold",
            ha="center"
        )

        posicion = 0.26

        for material, cantidad in materiales:

            ax.text(
                0.10, posicion,
                str(material),
                fontsize=12
            )

            ax.text(
                0.75, posicion,
                f"{cantidad:.2f}",
                fontsize=12,
                ha="center"
            )

            posicion -= 0.055

        ax.text(
            0.5, 0.06,
            "ECOTRACK - Cada acción cuenta por un planeta mejor.",
            fontsize=10,
            color="#64748B",
            ha="center"
        )

        pdf.savefig(figura)
        figura.clear()

        # =================================
        # PÁGINA 2: GRÁFICAS
        # =================================

        figura = Figure(figsize=(8.27, 11.69))
        figura.patch.set_facecolor("white")

        figura.suptitle(
            "ANÁLISIS DE RECICLAJE",
            fontsize=21,
            fontweight="bold",
            color="#14532D",
            y=0.96
        )

        if materiales:

            nombres = [m[0] for m in materiales]
            cantidades = [float(m[1]) for m in materiales]

            # Gráfica de barras
            ax1 = figura.add_subplot(211)

            ax1.bar(
                nombres,
                cantidades,
                color="#15803D"
            )

            ax1.set_title(
                "Cantidad reciclada por material",
                fontsize=14,
                fontweight="bold"
            )

            ax1.set_ylabel("Kilogramos")

            ax1.grid(
                axis="y",
                alpha=0.2
            )

            # Gráfica circular
            ax2 = figura.add_subplot(212)

            ax2.pie(
                cantidades,
                labels=nombres,
                autopct="%1.1f%%",
                startangle=90
            )

            ax2.set_title(
                "Distribución porcentual del reciclaje",
                fontsize=14,
                fontweight="bold"
            )

        else:

            ax = figura.add_subplot(111)
            ax.text(
                0.5, 0.5,
                "Todavía no existen datos de reciclaje.",
                ha="center",
                fontsize=15
            )
            ax.axis("off")

        figura.tight_layout(rect=[0, 0.02, 1, 0.93])

        pdf.savefig(figura)
        figura.clear()

        # =================================
        # PÁGINA 3: HISTORIAL
        # =================================

        figura = Figure(figsize=(11.69, 8.27))
        figura.patch.set_facecolor("white")

        ax = figura.add_subplot(111)
        ax.axis("off")

        ax.set_title(
            "HISTORIAL DE RECICLAJE",
            fontsize=20,
            fontweight="bold",
            color="#14532D",
            pad=25
        )

        encabezados = [
            "Usuario",
            "Material",
            "Cantidad",
            "Puntos",
            "Fecha"
        ]

        filas = [
            [
                str(registro[0]),
                str(registro[1]),
                f"{float(registro[2]):.2f} kg",
                str(registro[3]),
                str(registro[4])
            ]
            for registro in historial
        ]

        if filas:

            tabla = ax.table(
                cellText=filas,
                colLabels=encabezados,
                loc="center",
                cellLoc="center"
            )

            tabla.auto_set_font_size(False)
            tabla.set_fontsize(8)
            tabla.scale(1, 1.5)

        else:

            ax.text(
                0.5, 0.5,
                "No existen registros de reciclaje.",
                ha="center",
                fontsize=14
            )

        pdf.savefig(figura)
        figura.clear()

    print("Reporte generado correctamente.")
    print(f"Ubicación: {nombre_archivo}")

    return nombre_archivo


if __name__ == "__main__":
    generar_reporte_pdf()