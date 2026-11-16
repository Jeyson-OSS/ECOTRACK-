import os
import customtkinter as ctk
from tkinter import messagebox

from database import conectar
from estadisticas import total_reciclado, total_puntos, total_usuarios
from reciclaje import registrar_reciclaje
from usuarios import obtener_usuarios, registrar_usuario
from reportes import obtener_historial, residuos_por_material
from exportar_pdf import generar_reporte_pdf

from recompensas import (
    RECOMPENSAS,
    obtener_puntos_disponibles,
    canjear_recompensa,
    obtener_historial_canjes
)

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


class EcoTrackApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("ECOTRACK - Gestión Inteligente de Residuos")
        self.geometry("1150x700")
        self.minsize(950, 600)
        self.configure(fg_color="#F2F7F3")

        self.usuario_actual = None
        self.mostrar_login()

    # =====================================
    # UTILIDADES
    # =====================================

    def limpiar_ventana(self):
        for widget in self.winfo_children():
            widget.destroy()

    def limpiar_contenido(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()

    def titulo_pagina(self, titulo, descripcion):

        ctk.CTkLabel(
            self.contenido,
            text=titulo,
            font=("Arial", 30, "bold"),
            text_color="#14532D"
        ).pack(anchor="w", pady=(10, 5))

        ctk.CTkLabel(
            self.contenido,
            text=descripcion,
            font=("Arial", 14),
            text_color="#64748B"
        ).pack(anchor="w", pady=(0, 25))

    # =====================================
    # INICIO DE SESIÓN
    # =====================================

    def mostrar_login(self):

        self.limpiar_ventana()
        self.geometry("500x550")

        formulario = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=20
        )
        formulario.pack(
            expand=True,
            padx=50,
            pady=40,
            fill="both"
        )

        ctk.CTkLabel(
            formulario,
            text="♻ ECOTRACK",
            font=("Arial", 32, "bold"),
            text_color="#14532D"
        ).pack(pady=(45, 10))

        ctk.CTkLabel(
            formulario,
            text="Sistema inteligente de reciclaje",
            font=("Arial", 14),
            text_color="#64748B"
        ).pack(pady=(0, 35))

        self.login_usuario = ctk.CTkEntry(
            formulario,
            placeholder_text="Nombre de usuario",
            width=300,
            height=45
        )
        self.login_usuario.pack(pady=10)

        self.login_contrasena = ctk.CTkEntry(
            formulario,
            placeholder_text="Contraseña",
            show="*",
            width=300,
            height=45
        )
        self.login_contrasena.pack(pady=10)

        self.login_contrasena.bind(
            "<Return>",
            lambda event: self.validar_login()
        )

        ctk.CTkButton(
            formulario,
            text="INICIAR SESIÓN",
            width=300,
            height=45,
            command=self.validar_login
        ).pack(pady=25)

        ctk.CTkLabel(
            formulario,
            text="ECOTRACK © 2026",
            text_color="#94A3B8"
        ).pack(pady=10)

    def validar_login(self):

        usuario = self.login_usuario.get().strip()
        contrasena = self.login_contrasena.get()

        if not usuario or not contrasena:
            messagebox.showwarning(
                "Datos incompletos",
                "Ingresá tu usuario y contraseña."
            )
            return

        conexion = conectar()

        try:
            cursor = conexion.cursor()

            cursor.execute(
                """
                SELECT id, nombre, usuario, contraseña, rol
                FROM usuarios
                WHERE usuario = ? AND contraseña = ?
                """,
                (usuario, contrasena)
            )

            resultado = cursor.fetchone()

        finally:
            conexion.close()

        if resultado:

            self.usuario_actual = {
                "id": resultado[0],
                "nombre": resultado[1],
                "usuario": resultado[2],
                "rol": resultado[4]
            }

            self.mostrar_sistema()

        else:

            messagebox.showerror(
                "Acceso denegado",
                "Usuario o contraseña incorrectos."
            )

    # =====================================
    # SISTEMA PRINCIPAL
    # =====================================

    def mostrar_sistema(self):

        self.limpiar_ventana()
        self.geometry("1150x700")

        self.crear_menu()
        self.crear_contenido()
        self.mostrar_inicio()

    def crear_menu(self):

        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color="#14532D"
        )

        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="♻ ECOTRACK",
            font=("Arial", 27, "bold"),
            text_color="white"
        ).pack(pady=(25, 10))

        ctk.CTkLabel(
            self.sidebar,
            text=self.usuario_actual["nombre"],
            font=("Arial", 15, "bold"),
            text_color="#BBF7D0"
        ).pack(pady=5)

        ctk.CTkLabel(
            self.sidebar,
            text=self.usuario_actual["rol"].upper(),
            font=("Arial", 12),
            text_color="white"
        ).pack(pady=(0, 18))

        opciones = [
            ("🏠  Inicio", self.mostrar_inicio),
            ("♻  Registrar reciclaje", self.mostrar_registro),
            ("📋  Historial", self.mostrar_historial),
            ("📊  Estadísticas", self.mostrar_estadisticas),
            ("📈  Gráficas", self.mostrar_graficas),
            ("🎁  Recompensas", self.mostrar_recompensas)
        ]

        if self.usuario_actual["rol"] == "admin":

            opciones.extend([
                ("👥  Usuarios", self.mostrar_usuarios),
                ("➕  Nuevo usuario", self.mostrar_nuevo_usuario),
                ("📄  Exportar PDF", self.exportar_pdf)
            ])

        for texto, funcion in opciones:

            ctk.CTkButton(
                self.sidebar,
                text=texto,
                height=40,
                anchor="w",
                fg_color="transparent",
                hover_color="#166534",
                text_color="white",
                font=("Arial", 13),
                command=funcion
            ).pack(fill="x", padx=12, pady=4)

        ctk.CTkButton(
            self.sidebar,
            text="🚪  Cerrar sesión",
            height=42,
            fg_color="#991B1B",
            hover_color="#7F1D1D",
            text_color="white",
            command=self.cerrar_sesion
        ).pack(side="bottom", fill="x", padx=15, pady=20)

    def crear_contenido(self):

        self.contenido = ctk.CTkFrame(
            self,
            fg_color="#F2F7F3",
            corner_radius=0
        )

        self.contenido.pack(
            side="right",
            expand=True,
            fill="both",
            padx=25,
            pady=20
        )

    # =====================================
    # CONSULTAS POR USUARIO
    # =====================================

    def resumen_usuario(self):

        conexion = conectar()

        try:
            cursor = conexion.cursor()

            cursor.execute(
                """
                SELECT COALESCE(SUM(cantidad), 0),
                       COALESCE(SUM(puntos), 0)
                FROM reciclaje
                WHERE usuario_id = ?
                """,
                (self.usuario_actual["id"],)
            )

            return cursor.fetchone()

        finally:
            conexion.close()

    def obtener_materiales_usuario(self):

        conexion = conectar()

        try:
            cursor = conexion.cursor()

            cursor.execute(
                """
                SELECT material, SUM(cantidad)
                FROM reciclaje
                WHERE usuario_id = ?
                GROUP BY material
                """,
                (self.usuario_actual["id"],)
            )

            return cursor.fetchall()

        finally:
            conexion.close()

    # =====================================
    # PANEL PRINCIPAL
    # =====================================

    def mostrar_inicio(self):

        self.limpiar_contenido()

        self.titulo_pagina(
            "Panel principal",
            f"Bienvenido, {self.usuario_actual['nombre']}."
        )

        if self.usuario_actual["rol"] == "admin":

            datos = [
                ("♻ Residuos reciclados",
                 f"{total_reciclado():.2f} kg"),

                ("⭐ Puntos acumulados",
                 str(total_puntos())),

                ("👥 Usuarios registrados",
                 str(total_usuarios()))
            ]

        else:

            cantidad, puntos = self.resumen_usuario()

            disponibles = obtener_puntos_disponibles(
                self.usuario_actual["id"]
            )

            datos = [
                ("♻ Mis residuos reciclados",
                 f"{cantidad:.2f} kg"),

                ("⭐ Mis puntos disponibles",
                 str(disponibles))
            ]

        tarjetas = ctk.CTkFrame(
            self.contenido,
            fg_color="transparent"
        )
        tarjetas.pack(fill="x")

        for titulo, valor in datos:

            tarjeta = ctk.CTkFrame(
                tarjetas,
                fg_color="white",
                corner_radius=15
            )

            tarjeta.pack(
                side="left",
                expand=True,
                fill="both",
                padx=8
            )

            ctk.CTkLabel(
                tarjeta,
                text=titulo,
                font=("Arial", 14),
                text_color="#64748B"
            ).pack(pady=(25, 10))

            ctk.CTkLabel(
                tarjeta,
                text=valor,
                font=("Arial", 26, "bold"),
                text_color="#15803D"
            ).pack(pady=(0, 25))

        mensaje = ctk.CTkFrame(
            self.contenido,
            fg_color="#DCFCE7",
            corner_radius=15
        )

        mensaje.pack(fill="x", pady=35)

        ctk.CTkLabel(
            mensaje,
            text="¡Cada acción cuenta!",
            font=("Arial", 22, "bold"),
            text_color="#166534"
        ).pack(pady=(25, 8))

        ctk.CTkLabel(
            mensaje,
            text="Reciclar hoy es construir un mejor mañana.",
            font=("Arial", 15),
            text_color="#166534"
        ).pack(pady=(0, 25))

    # =====================================
    # REGISTRAR RECICLAJE
    # =====================================

    def mostrar_registro(self):

        self.limpiar_contenido()

        self.titulo_pagina(
            "Registrar reciclaje",
            "Ingresá los datos del material reciclado."
        )

        formulario = ctk.CTkFrame(
            self.contenido,
            fg_color="white",
            corner_radius=15
        )

        formulario.pack(fill="x", padx=10, pady=10)

        self.lista_usuarios = {}

        if self.usuario_actual["rol"] == "admin":

            usuarios = obtener_usuarios()

            self.lista_usuarios = {
                usuario[1]: usuario[0]
                for usuario in usuarios
            }

            ctk.CTkLabel(
                formulario,
                text="Seleccionar usuario",
                font=("Arial", 15, "bold"),
                text_color="#14532D"
            ).pack(anchor="w", padx=30, pady=(25, 5))

            nombres = list(self.lista_usuarios.keys())

            if not nombres:
                messagebox.showwarning(
                    "Sin usuarios",
                    "No hay usuarios registrados."
                )
                return

            self.usuario_seleccionado = ctk.CTkOptionMenu(
                formulario,
                values=nombres,
                width=350
            )

            self.usuario_seleccionado.pack(anchor="w", padx=30)

        else:

            self.lista_usuarios = {
                self.usuario_actual["usuario"]:
                self.usuario_actual["id"]
            }

        ctk.CTkLabel(
            formulario,
            text="Tipo de material",
            font=("Arial", 15, "bold"),
            text_color="#14532D"
        ).pack(anchor="w", padx=30, pady=(20, 5))

        self.material_seleccionado = ctk.CTkOptionMenu(
            formulario,
            values=["Plástico", "Papel", "Cartón", "Vidrio", "Metal"],
            width=350
        )

        self.material_seleccionado.pack(anchor="w", padx=30)

        ctk.CTkLabel(
            formulario,
            text="Cantidad en kilogramos",
            font=("Arial", 15, "bold"),
            text_color="#14532D"
        ).pack(anchor="w", padx=30, pady=(20, 5))

        self.cantidad = ctk.CTkEntry(
            formulario,
            placeholder_text="Ejemplo: 2.5",
            width=350
        )

        self.cantidad.pack(anchor="w", padx=30)

        ctk.CTkButton(
            formulario,
            text="♻ GUARDAR RECICLAJE",
            width=350,
            height=45,
            command=self.guardar_reciclaje
        ).pack(anchor="w", padx=30, pady=30)

    def guardar_reciclaje(self):

        try:

            if self.usuario_actual["rol"] == "admin":

                nombre = self.usuario_seleccionado.get()
                usuario_id = self.lista_usuarios[nombre]

            else:

                usuario_id = self.usuario_actual["id"]

            material = self.material_seleccionado.get()

            cantidad = float(
                self.cantidad.get().replace(",", ".")
            )

            if cantidad <= 0:
                raise ValueError

            puntos = registrar_reciclaje(
                usuario_id,
                material,
                cantidad
            )

            messagebox.showinfo(
                "Registro exitoso",
                f"Material: {material}\n"
                f"Cantidad: {cantidad:.2f} kg\n"
                f"Puntos obtenidos: {puntos}"
            )

            self.mostrar_inicio()

        except ValueError:

            messagebox.showerror(
                "Cantidad inválida",
                "Ingresá una cantidad numérica mayor que cero."
            )

        except Exception as error:

            messagebox.showerror(
                "Error",
                f"No se pudo guardar el registro:\n{error}"
            )

    # =====================================
    # HISTORIAL
    # =====================================

    def mostrar_historial(self):

        self.limpiar_contenido()

        self.titulo_pagina(
            "Historial de reciclaje",
            "Consulta de registros realizados."
        )

        registros = obtener_historial()

        if self.usuario_actual["rol"] != "admin":

            registros = [
                registro for registro in registros
                if self.es_registro_del_usuario(registro)
            ]

        tabla = ctk.CTkScrollableFrame(
            self.contenido,
            fg_color="white"
        )

        tabla.pack(fill="both", expand=True)

        encabezados = [
            "Usuario", "Material", "Cantidad", "Puntos", "Fecha"
        ]

        for columna, texto in enumerate(encabezados):

            ctk.CTkLabel(
                tabla,
                text=texto,
                font=("Arial", 13, "bold"),
                text_color="#14532D"
            ).grid(row=0, column=columna, padx=12, pady=15)

        for fila, registro in enumerate(registros, start=1):

            for columna, dato in enumerate(registro):

                ctk.CTkLabel(
                    tabla,
                    text=str(dato),
                    text_color="#334155"
                ).grid(
                    row=fila,
                    column=columna,
                    padx=12,
                    pady=12
                )

        if not registros:

            ctk.CTkLabel(
                tabla,
                text="No hay registros disponibles."
            ).grid(
                row=1,
                column=0,
                columnspan=5,
                pady=30
            )

    def es_registro_del_usuario(self, registro):

        conexion = conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute(
                "SELECT id FROM usuarios WHERE nombre = ?",
                (registro[0],)
            )

            resultado = cursor.fetchone()

            return (
                resultado is not None
                and resultado[0] == self.usuario_actual["id"]
            )

        finally:
            conexion.close()

    # =====================================
    # ESTADÍSTICAS
    # =====================================

    def mostrar_estadisticas(self):

        self.limpiar_contenido()

        self.titulo_pagina(
            "Estadísticas",
            "Resumen de materiales reciclados."
        )

        if self.usuario_actual["rol"] == "admin":

            datos = [
                ("Total reciclado",
                 f"{total_reciclado():.2f} kg"),

                ("Total de puntos",
                 str(total_puntos())),

                ("Usuarios registrados",
                 str(total_usuarios()))
            ]

            materiales = residuos_por_material()

        else:

            cantidad, puntos = self.resumen_usuario()

            datos = [
                ("Mis residuos reciclados",
                 f"{cantidad:.2f} kg"),

                ("Mis puntos disponibles",
                 str(obtener_puntos_disponibles(
                     self.usuario_actual["id"]
                 )))
            ]

            materiales = self.obtener_materiales_usuario()

        for titulo, valor in datos:

            tarjeta = ctk.CTkFrame(
                self.contenido,
                fg_color="white",
                corner_radius=12
            )

            tarjeta.pack(fill="x", pady=8)

            ctk.CTkLabel(
                tarjeta,
                text=titulo,
                text_color="#64748B"
            ).pack(anchor="w", padx=25, pady=(15, 5))

            ctk.CTkLabel(
                tarjeta,
                text=valor,
                font=("Arial", 25, "bold"),
                text_color="#15803D"
            ).pack(anchor="w", padx=25, pady=(0, 15))

        ctk.CTkLabel(
            self.contenido,
            text="Materiales reciclados",
            font=("Arial", 20, "bold"),
            text_color="#14532D"
        ).pack(anchor="w", pady=15)

        for material, cantidad in materiales:

            ctk.CTkLabel(
                self.contenido,
                text=f"{material}: {cantidad:.2f} kg",
                text_color="#334155"
            ).pack(anchor="w", pady=4)

    # =====================================
    # GRÁFICAS
    # =====================================

    def mostrar_graficas(self):

        self.limpiar_contenido()

        self.titulo_pagina(
            "Gráficas de reciclaje",
            "Visualización de los materiales reciclados."
        )

        if self.usuario_actual["rol"] == "admin":
            materiales = residuos_por_material()
        else:
            materiales = self.obtener_materiales_usuario()

        materiales = [
            (nombre, cantidad)
            for nombre, cantidad in materiales
            if cantidad is not None and cantidad > 0
        ]

        if not materiales:

            ctk.CTkLabel(
                self.contenido,
                text="Todavía no hay datos para generar gráficas.",
                font=("Arial", 17),
                text_color="#64748B"
            ).pack(pady=60)

            return

        nombres = [dato[0] for dato in materiales]
        cantidades = [float(dato[1]) for dato in materiales]

        figura = Figure(figsize=(9, 5), dpi=100)
        figura.patch.set_facecolor("#F2F7F3")

        barras = figura.add_subplot(121)

        barras.bar(
            nombres,
            cantidades,
            color="#15803D"
        )

        barras.set_title("Reciclaje por material")
        barras.set_ylabel("Kilogramos")
        barras.tick_params(axis="x", rotation=35)
        barras.grid(axis="y", alpha=0.2)

        circular = figura.add_subplot(122)

        circular.pie(
            cantidades,
            labels=nombres,
            autopct="%1.1f%%",
            startangle=90
        )

        circular.set_title("Porcentaje por material")

        figura.tight_layout(pad=3)

        contenedor = ctk.CTkFrame(
            self.contenido,
            fg_color="white",
            corner_radius=15
        )

        contenedor.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        lienzo = FigureCanvasTkAgg(
            figura,
            master=contenedor
        )

        lienzo.draw()

        lienzo.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # =====================================
    # RECOMPENSAS
    # =====================================

    def mostrar_recompensas(self):

        self.limpiar_contenido()

        self.titulo_pagina(
            "Recompensas ecológicas",
            "Canjeá tus puntos por beneficios."
        )

        usuario_id = self.usuario_actual["id"]

        puntos = obtener_puntos_disponibles(usuario_id)

        tarjeta_puntos = ctk.CTkFrame(
            self.contenido,
            fg_color="#DCFCE7",
            corner_radius=15
        )

        tarjeta_puntos.pack(fill="x", pady=10)

        ctk.CTkLabel(
            tarjeta_puntos,
            text="⭐ TUS PUNTOS DISPONIBLES",
            font=("Arial", 17, "bold"),
            text_color="#166534"
        ).pack(pady=(18, 5))

        ctk.CTkLabel(
            tarjeta_puntos,
            text=str(puntos),
            font=("Arial", 32, "bold"),
            text_color="#15803D"
        ).pack(pady=(0, 18))

        contenedor = ctk.CTkScrollableFrame(
            self.contenido,
            fg_color="transparent"
        )

        contenedor.pack(
            fill="both",
            expand=True,
            pady=10
        )

        for recompensa in RECOMPENSAS:

            disponible = puntos >= recompensa["puntos"]

            tarjeta = ctk.CTkFrame(
                contenedor,
                fg_color="white",
                corner_radius=12
            )

            tarjeta.pack(fill="x", padx=5, pady=7)

            ctk.CTkLabel(
                tarjeta,
                text=f"🎁 {recompensa['nombre']}",
                font=("Arial", 17, "bold"),
                text_color="#14532D"
            ).pack(anchor="w", padx=20, pady=(15, 5))

            ctk.CTkLabel(
                tarjeta,
                text=recompensa["descripcion"],
                text_color="#64748B"
            ).pack(anchor="w", padx=20, pady=3)

            ctk.CTkLabel(
                tarjeta,
                text=f"⭐ {recompensa['puntos']} puntos",
                font=("Arial", 14, "bold"),
                text_color="#15803D"
            ).pack(anchor="w", padx=20, pady=5)

            ctk.CTkButton(
                tarjeta,
                text="CANJEAR" if disponible else "PUNTOS INSUFICIENTES",
                state="normal" if disponible else "disabled",
                fg_color="#15803D",
                hover_color="#166534",
                command=lambda r=recompensa: self.confirmar_canje(r)
            ).pack(anchor="e", padx=20, pady=(5, 15))

        ctk.CTkButton(
            self.contenido,
            text="📋 VER HISTORIAL DE CANJES",
            height=40,
            command=self.mostrar_historial_canjes
        ).pack(fill="x", pady=8)

    def confirmar_canje(self, recompensa):

        respuesta = messagebox.askyesno(
            "Confirmar canje",
            f"¿Deseás canjear {recompensa['nombre']} "
            f"por {recompensa['puntos']} puntos?"
        )

        if not respuesta:
            return

        exito, mensaje = canjear_recompensa(
            self.usuario_actual["id"],
            recompensa
        )

        if exito:

            messagebox.showinfo(
                "Canje exitoso",
                mensaje
            )

        else:

            messagebox.showwarning(
                "No se pudo canjear",
                mensaje
            )

        self.mostrar_recompensas()

    def mostrar_historial_canjes(self):

        self.limpiar_contenido()

        self.titulo_pagina(
            "Historial de recompensas",
            "Consulta de los canjes realizados."
        )

        if self.usuario_actual["rol"] == "admin":

            registros = obtener_historial_canjes()

        else:

            registros = obtener_historial_canjes(
                self.usuario_actual["id"]
            )

        tabla = ctk.CTkScrollableFrame(
            self.contenido,
            fg_color="white"
        )

        tabla.pack(fill="both", expand=True)

        encabezados = [
            "Usuario", "Recompensa", "Puntos", "Fecha"
        ]

        for columna, texto in enumerate(encabezados):

            ctk.CTkLabel(
                tabla,
                text=texto,
                font=("Arial", 13, "bold"),
                text_color="#14532D"
            ).grid(row=0, column=columna, padx=15, pady=15)

        if not registros:

            ctk.CTkLabel(
                tabla,
                text="Todavía no hay recompensas canjeadas."
            ).grid(
                row=1,
                column=0,
                columnspan=4,
                pady=30
            )

        for fila, registro in enumerate(registros, start=1):

            for columna, dato in enumerate(registro):

                ctk.CTkLabel(
                    tabla,
                    text=str(dato),
                    text_color="#334155"
                ).grid(
                    row=fila,
                    column=columna,
                    padx=15,
                    pady=12
                )

        ctk.CTkButton(
            self.contenido,
            text="VOLVER A RECOMPENSAS",
            command=self.mostrar_recompensas
        ).pack(fill="x", pady=8)

    # =====================================
    # USUARIOS
    # =====================================

    def mostrar_usuarios(self):

        if self.usuario_actual["rol"] != "admin":
            return

        self.limpiar_contenido()

        self.titulo_pagina(
            "Usuarios registrados",
            "Personas que forman parte de ECOTRACK."
        )

        usuarios = obtener_usuarios()

        tabla = ctk.CTkScrollableFrame(
            self.contenido,
            fg_color="white"
        )

        tabla.pack(fill="both", expand=True)

        encabezados = ["ID", "Nombre", "Usuario", "Rol"]

        for columna, texto in enumerate(encabezados):

            ctk.CTkLabel(
                tabla,
                text=texto,
                font=("Arial", 14, "bold"),
                text_color="#14532D"
            ).grid(row=0, column=columna, padx=25, pady=15)

        for fila, usuario in enumerate(usuarios, start=1):

            datos = [
                usuario[0],
                usuario[1],
                usuario[2],
                usuario[4]
            ]

            for columna, dato in enumerate(datos):

                ctk.CTkLabel(
                    tabla,
                    text=str(dato),
                    text_color="#334155"
                ).grid(
                    row=fila,
                    column=columna,
                    padx=25,
                    pady=12
                )

    # =====================================
    # NUEVO USUARIO
    # =====================================

    def mostrar_nuevo_usuario(self):

        if self.usuario_actual["rol"] != "admin":
            return

        self.limpiar_contenido()

        self.titulo_pagina(
            "Registrar nuevo usuario",
            "Completá los datos para agregar una persona."
        )

        formulario = ctk.CTkFrame(
            self.contenido,
            fg_color="white",
            corner_radius=15
        )

        formulario.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            formulario,
            text="Nombre completo",
            text_color="#14532D"
        ).pack(anchor="w", padx=30, pady=(25, 5))

        self.nuevo_nombre = ctk.CTkEntry(
            formulario,
            placeholder_text="Nombre completo",
            width=380
        )

        self.nuevo_nombre.pack(anchor="w", padx=30)

        ctk.CTkLabel(
            formulario,
            text="Nombre de usuario",
            text_color="#14532D"
        ).pack(anchor="w", padx=30, pady=(18, 5))

        self.nuevo_usuario = ctk.CTkEntry(
            formulario,
            placeholder_text="Nombre de usuario",
            width=380
        )

        self.nuevo_usuario.pack(anchor="w", padx=30)

        ctk.CTkLabel(
            formulario,
            text="Contraseña",
            text_color="#14532D"
        ).pack(anchor="w", padx=30, pady=(18, 5))

        self.nueva_contrasena = ctk.CTkEntry(
            formulario,
            placeholder_text="Contraseña",
            show="*",
            width=380
        )

        self.nueva_contrasena.pack(anchor="w", padx=30)

        ctk.CTkLabel(
            formulario,
            text="Tipo de usuario",
            text_color="#14532D"
        ).pack(anchor="w", padx=30, pady=(18, 5))

        self.nuevo_rol = ctk.CTkOptionMenu(
            formulario,
            values=["usuario", "admin"],
            width=380
        )

        self.nuevo_rol.pack(anchor="w", padx=30)

        ctk.CTkButton(
            formulario,
            text="➕ REGISTRAR USUARIO",
            width=380,
            height=45,
            command=self.guardar_usuario
        ).pack(anchor="w", padx=30, pady=30)

    def guardar_usuario(self):

        nombre = self.nuevo_nombre.get().strip()
        usuario = self.nuevo_usuario.get().strip()
        contrasena = self.nueva_contrasena.get()
        rol = self.nuevo_rol.get()

        if not nombre or not usuario or not contrasena:

            messagebox.showwarning(
                "Campos incompletos",
                "Completá todos los campos."
            )

            return

        if len(contrasena) < 4:

            messagebox.showwarning(
                "Contraseña inválida",
                "La contraseña debe tener al menos 4 caracteres."
            )

            return

        resultado = registrar_usuario(
            nombre,
            usuario,
            contrasena,
            rol
        )

        if resultado:

            messagebox.showinfo(
                "Registro exitoso",
                f"El usuario {usuario} fue registrado."
            )

            self.mostrar_usuarios()

        else:

            messagebox.showerror(
                "Error",
                "No se pudo registrar el usuario. "
                "Verificá si el nombre ya existe."
            )

    # =====================================
    # EXPORTAR PDF
    # =====================================

    def exportar_pdf(self):

        if self.usuario_actual["rol"] != "admin":

            messagebox.showerror(
                "Acceso denegado",
                "Solo el administrador puede exportar reportes."
            )

            return

        try:

            archivo = generar_reporte_pdf()

            messagebox.showinfo(
                "Reporte generado",
                "El reporte PDF se creó correctamente.\n\n"
                f"Archivo: {os.path.basename(archivo)}"
            )

            os.startfile(archivo)

        except Exception as error:

            messagebox.showerror(
                "Error al generar PDF",
                f"No se pudo generar el reporte:\n{error}"
            )

    # =====================================
    # CERRAR SESIÓN
    # =====================================

    def cerrar_sesion(self):

        respuesta = messagebox.askyesno(
            "Cerrar sesión",
            "¿Deseás cerrar tu sesión?"
        )

        if respuesta:

            self.usuario_actual = None
            self.mostrar_login()


# =====================================
# EJECUTAR ECOTRACK
# =====================================

if __name__ == "__main__":

    app = EcoTrackApp()
    app.mainloop()