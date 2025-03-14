import flet as ft
from Controlador.controlador import ClienteControlador
import datetime
import math
import threading

class ClienteVista:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.scroll = "always"  # Habilitar scroll vertical
        self.controlador = ClienteControlador(self)
        self.conectado = False
        self.cliente_id = None      # Guardará el id del cliente obtenido
        self.cliente_sueldo = None  # Para calcular cupo_total = 2 * sueldo
        page.window_prevent_close = True
        page.on_window_event = self.on_window_event


        # Control para mostrar mensajes en pantalla (no se limpia al resetear)
        self.lbl_mensaje = ft.Text(value="", color="green")
        
        # CONTROLES EXISTENTES (consulta de tarjeta)
        self.txt_tarjeta = ft.TextField(label="Número de Tarjeta")
        self.fecha_inicio = ft.TextField(label="Fecha Inicio (YYYY-MM-DD)")
        self.fecha_fin = ft.TextField(label="Fecha Fin (YYYY-MM-DD)")
        self.btn_conectar = ft.ElevatedButton("Conectar al Servidor", on_click=self.conectar_al_servidor)
        self.btn_ver_detalles = ft.ElevatedButton("Ver Detalles", on_click=self.ver_detalles)
        self.btn_ver_detalles.disabled = True
        self.btn_compras = ft.ElevatedButton("Compras", on_click=self.mostrar_compras)
        self.btn_compras.disabled = True
        self.detalles_cliente = ft.Text(value="Primero conecte al servidor")

        # CONTROLES PARA REGISTRO (cuando la tarjeta no existe)
        self.aviso_registro = ft.Text(value="", visible=False)
        self.radio_group = ft.RadioGroup(
            content=ft.Column(
                controls=[
                    ft.Radio(label="Cliente ya registrado", value="registrado"),
                    ft.Radio(label="Cliente nuevo", value="nuevo")
                ]
            ),
            visible=False
        )
        self.txt_cedula_existente = ft.TextField(label="Ingrese la cédula del cliente", visible=False)
        self.txt_nuevo_nombre = ft.TextField(label="Nombre del cliente", visible=False)
        self.txt_nueva_cedula = ft.TextField(label="Cédula", visible=False)
        self.txt_nuevo_sueldo = ft.TextField(label="Sueldo", visible=False)
        self.txt_nueva_edad = ft.TextField(label="Edad", visible=False)
        self.btn_siguiente_registro = ft.ElevatedButton("Siguiente", on_click=self.procesar_registro_cliente, visible=False)
        self.btn_atras = ft.ElevatedButton("Atrás", on_click=self.ocultar_registro, visible=False)
        
        # CONTROLES PARA CREAR TARJETA (se muestran tras obtener el cliente)
        self.txt_nombre_banco = ft.TextField(label="Nombre del Banco", visible=False)
        self.txt_cupo_total = ft.TextField(label="Cupo Total (se calcula automáticamente)", visible=False, disabled=True)
        self.btn_crear_tarjeta = ft.ElevatedButton("Crear Tarjeta", on_click=self.registrar_tarjeta, visible=False)
        
        # CONTROLES NUEVOS PARA REGISTRAR COMPRA
        self.btn_registrar_compra = ft.ElevatedButton("Registrar Compra", on_click=self.mostrar_formulario_compra, visible=False)
        self.txt_fecha_compra = ft.TextField(label="Fecha de Compra (YYYY-MM-DD)", visible=False)
        self.txt_monto_compra = ft.TextField(label="Monto", visible=False)
        self.txt_descripcion_compra = ft.TextField(label="Descripción", visible=False)
        self.btn_confirmar_compra = ft.ElevatedButton("Confirmar Compra", on_click=self.registrar_compra, visible=False)
        self.btn_cancelar_compra = ft.ElevatedButton("Cancelar", on_click=self.ocultar_formulario_compra, visible=False)
        
        # CONTROLES NUEVOS PARA REGISTRAR PAGO
        # Dropdown para seleccionar la compra a pagar
        self.dropdown_compras_pago = ft.Dropdown(visible=False)
        self.dropdown_compras_pago.on_change = self.seleccionar_compra  # Actualiza el monto de pago al cambiar selección
        # Controles para el pago
        self.txt_fecha_pago = ft.TextField(label="Fecha de Pago (YYYY-MM-DD)", visible=False)
        self.txt_monto_pago = ft.TextField(label="Monto de Pago", visible=False, disabled=True)
        self.txt_descripcion_pago = ft.TextField(label="Descripción del Pago", visible=False)
        self.btn_generar_pago = ft.ElevatedButton("Generar Pago", on_click=self.mostrar_formulario_pago, visible=False)
        self.btn_confirmar_pago = ft.ElevatedButton("Confirmar Pago", on_click=self.registrar_pago, visible=False)
        self.btn_cancelar_pago = ft.ElevatedButton("Cancelar Pago", on_click=self.ocultar_formulario_pago, visible=False)

        # Envolver todos los controles en un contenedor (Column) con scroll vertical
        scrollable_content = ft.Column(
            controls=[
                self.lbl_mensaje,
                self.btn_conectar,
                self.txt_tarjeta,
                self.fecha_inicio,
                self.fecha_fin,
                self.btn_ver_detalles,
                self.btn_compras,
                self.detalles_cliente,
                self.btn_registrar_compra,
                self.txt_fecha_compra,
                self.txt_monto_compra,
                self.txt_descripcion_compra,
                self.btn_confirmar_compra,
                self.btn_cancelar_compra,
                self.btn_generar_pago,
                self.dropdown_compras_pago,
                self.txt_fecha_pago,
                self.txt_monto_pago,
                self.txt_descripcion_pago,
                self.btn_confirmar_pago,
                self.btn_cancelar_pago,
                self.aviso_registro,
                self.radio_group,
                self.txt_cedula_existente,
                self.txt_nuevo_nombre,
                self.txt_nueva_cedula,
                self.txt_nuevo_sueldo,
                self.txt_nueva_edad,
                self.btn_siguiente_registro,
                self.btn_atras,
                self.txt_nombre_banco,
                self.txt_cupo_total,
                self.btn_crear_tarjeta
            ],
            scroll="always"
        )

        self.page.add(scrollable_content)
        self.radio_group.on_change = self.on_radio_group_change

    def on_window_event(self, e):
        if e.data == "close":
            # Liberar tarjeta antes de cerrar
            if self.controlador.tarjeta_actual:
                self.controlador.liberar_tarjeta(
                    self.controlador.tarjeta_actual
                )
            self.page.window_destroy()
            
    # Método para limpiar lbl_mensaje después de 60 segundos
    def mostrar_mensaje_temporal(self, mensaje):
        self.lbl_mensaje.value = mensaje
        self.page.update()
        # Después de 60 segundos se borra el mensaje
        threading.Timer(2, self.clear_lbl_mensaje).start()

    def clear_lbl_mensaje(self):
        self.lbl_mensaje.value = ""
        self.page.update()

    # Métodos para resetear y limpiar controles
    def resetear_vista(self):
        self.detalles_cliente.value = ""
        self.aviso_registro.value = ""
        self.aviso_registro.visible = False
        self.radio_group.visible = False
        self.txt_cedula_existente.visible = False
        self.txt_nuevo_nombre.visible = False
        self.txt_nueva_cedula.visible = False
        self.txt_nuevo_sueldo.visible = False
        self.txt_nueva_edad.visible = False
        self.btn_siguiente_registro.visible = False
        self.btn_atras.visible = False
        self.txt_nombre_banco.visible = False
        self.txt_cupo_total.visible = False
        self.btn_crear_tarjeta.visible = False
        self.btn_compras.disabled = True
        self.btn_registrar_compra.visible = False
        self.txt_fecha_compra.visible = False
        self.txt_monto_compra.visible = False
        self.txt_descripcion_compra.visible = False
        self.btn_confirmar_compra.visible = False
        self.btn_cancelar_compra.visible = False
        self.btn_generar_pago.visible = False
        self.dropdown_compras_pago.visible = False
        self.txt_fecha_pago.visible = False
        self.txt_monto_pago.visible = False
        self.txt_descripcion_pago.visible = False
        self.btn_confirmar_pago.visible = False
        self.btn_cancelar_pago.visible = False
        self.txt_cedula_existente.value = ""
        self.txt_nuevo_nombre.value = ""
        self.txt_nueva_cedula.value = ""
        self.txt_nuevo_sueldo.value = ""
        self.txt_nueva_edad.value = ""
        self.txt_nombre_banco.value = ""
        self.txt_cupo_total.value = ""
        self.txt_fecha_compra.value = ""
        self.txt_monto_compra.value = ""
        self.txt_descripcion_compra.value = ""
        self.txt_fecha_pago.value = ""
        self.txt_monto_pago.value = ""
        self.txt_descripcion_pago.value = ""
        self.page.update()

    def limpiar_campos_registro_cliente(self):
        self.txt_cedula_existente.value = ""
        self.txt_nuevo_nombre.value = ""
        self.txt_nueva_cedula.value = ""
        self.txt_nuevo_sueldo.value = ""
        self.txt_nueva_edad.value = ""
        self.page.update()

    # Métodos de conexión y consulta
    def conectar_al_servidor(self, e):
        self.conectado = self.controlador.conectar_al_servidor()
        if self.conectado:
            self.detalles_cliente.value = "Cliente conectado"
            self.habilitar_ver_detalles()
        else:
            self.detalles_cliente.value = "Error: No se pudo conectar al servidor"
        self.page.update()

    def habilitar_ver_detalles(self):
        self.btn_ver_detalles.disabled = False
        self.page.update()

    def ver_detalles(self, e):
        if not self.txt_tarjeta.value.strip():
            self.resetear_vista()
            self.mostrar_mensaje_temporal("Debe ingresar un número de tarjeta válido")
            self.page.update()
            return
        num = self.txt_tarjeta.value.strip()
        if self.controlador.tarjeta_actual:
            self.controlador.liberar_tarjeta(self.controlador.tarjeta_actual)
        self.resetear_vista()
        self.txt_tarjeta.value = num
        fecha_inicio = self.fecha_inicio.value.strip() or None
        fecha_fin = self.fecha_fin.value.strip() or None
        self.controlador.buscar_cliente_por_tarjeta(num, fecha_inicio, fecha_fin)
        self.page.update()

    def ocultar_registro(self, e):
        if self.controlador.tarjeta_actual:
            self.controlador.liberar_tarjeta(self.controlador.tarjeta_actual)
        self.resetear_vista()
        self.page.update()

    def mostrar_detalle(self, detalle):
        if "error" in detalle:
            self.mostrar_registro_tarjeta()
            self.mostrar_mensaje_temporal(detalle["error"])
        else:
            texto = f"Titular: {detalle['nombre']}\n"
            card = None
            for t in detalle['tarjetas']:
                if t['numero_tarjeta'] == self.txt_tarjeta.value.strip():
                    card = t
                    break
            if card:
                texto += f"Banco: {card['nombre_banco']}\n"
                texto += f"Cupo Total: {self.formatear_pesos(card['cupo_total'])}\n"
                texto += f"Cupo Disponible: {self.formatear_pesos(card['cupo_disponible'])}\n"
            texto += f"Número de compras: {detalle['num_compras']}\n"
            self.detalles_cliente.value = texto
            self.btn_compras.disabled = False if detalle['compras'] else True
            self.btn_registrar_compra.visible = True
            self.btn_generar_pago.visible = True
        self.page.update()

    def mostrar_compras(self, e):
        if self.controlador.ultimo_detalle is None:
            self.mostrar_mensaje_temporal("Primero vea los detalles de la tarjeta")
            self.page.update()
            return
        compras = self.controlador.ultimo_detalle.get("compras", [])
        if not compras:
            self.mostrar_mensaje_temporal("No hay compras para mostrar")
            self.page.update()
            return
        texto = "Compras:\n"
        for compra in compras:
            texto += (
                f"Tarjeta ({compra['nombre_banco']}): "
                f"Monto: {self.formatear_pesos(compra['monto'])}, "
                f"Descripción: {compra['descripcion']}\n"
            )
        self.detalles_cliente.value = texto
        self.page.update()

    # --- Sección de registro de compra ---
    def mostrar_formulario_compra(self, e):
        self.txt_fecha_compra.visible = True
        self.txt_monto_compra.visible = True
        self.txt_descripcion_compra.visible = True
        self.btn_confirmar_compra.visible = True
        self.btn_cancelar_compra.visible = True
        self.txt_fecha_compra.value = ""
        self.txt_monto_compra.value = ""
        self.txt_descripcion_compra.value = ""
        self.page.update()

    def ocultar_formulario_compra(self, e):
        self.txt_fecha_compra.visible = False
        self.txt_monto_compra.visible = False
        self.txt_descripcion_compra.visible = False
        self.btn_confirmar_compra.visible = False
        self.btn_cancelar_compra.visible = False
        self.txt_fecha_compra.value = ""
        self.txt_monto_compra.value = ""
        self.txt_descripcion_compra.value = ""
        self.page.update()

    def registrar_compra(self, e):
        fecha = self.txt_fecha_compra.value.strip()
        monto = self.txt_monto_compra.value.strip()
        descripcion = self.txt_descripcion_compra.value.strip()
        numero_tarjeta = self.txt_tarjeta.value.strip()
        if not (fecha and monto and descripcion):
            self.mostrar_mensaje_temporal("Complete todos los datos de la compra")
            self.page.update()
            return
        try:
            monto = float(monto)
        except ValueError:
            self.mostrar_mensaje_temporal("El monto debe ser numérico")
            self.page.update()
            return
        datos = {
            "accion": "registrar_compra",
            "numero_tarjeta": numero_tarjeta,
            "fecha": fecha,
            "monto": monto,
            "descripcion": descripcion
        }
        respuesta = self.controlador.registrar_compra(datos)
        if respuesta is None:
            self.mostrar_mensaje_temporal("Error de conexión: No se recibió respuesta del servidor")
        elif "mensaje" in respuesta:
            self.mostrar_mensaje_temporal(respuesta["mensaje"])
        else:
            self.mostrar_mensaje_temporal(respuesta.get("error", "No se pudo registrar la compra"))
        self.controlador.buscar_cliente_por_tarjeta(numero_tarjeta)
        self.resetear_vista()
        self.page.update()

    # --- Sección de registro de tarjeta y cliente ---
    def mostrar_registro_tarjeta(self):
        self.resetear_vista()
        self.aviso_registro.value = ("El número de la tarjeta no se encuentra registrado. "
                                    "Registre el cliente para crear una tarjeta.")
        self.aviso_registro.visible = True
        self.radio_group.visible = True
        self.btn_siguiente_registro.visible = True
        self.btn_atras.visible = True
        self.page.update()

    def on_radio_group_change(self, e):
        if self.radio_group.value == "registrado":
            self.txt_cedula_existente.visible = True
            self.txt_nuevo_nombre.visible = False
            self.txt_nueva_cedula.visible = False
            self.txt_nuevo_sueldo.visible = False
            self.txt_nueva_edad.visible = False
        elif self.radio_group.value == "nuevo":
            self.txt_cedula_existente.visible = False
            self.txt_nuevo_nombre.visible = True
            self.txt_nueva_cedula.visible = True
            self.txt_nuevo_sueldo.visible = True
            self.txt_nueva_edad.visible = True
        self.page.update()

    def procesar_registro_cliente(self, e):
        if self.radio_group.value == "registrado":
            cedula = self.txt_cedula_existente.value.strip()
            if not cedula:
                self.mostrar_mensaje_temporal("Ingrese la cédula del cliente")
                self.page.update()
                return
            respuesta = self.controlador.buscar_cliente_por_cedula(cedula)
            if "error" in respuesta:
                self.mostrar_mensaje_temporal(f"Cliente con cédula {cedula} no ha sido encontrado")
                self.page.update()
                return
            else:
                self.cliente_id = respuesta.get("id_cliente")
                self.cliente_sueldo = respuesta.get("sueldo")
                self.detalles_cliente.value = f"Cliente encontrado: {respuesta.get('nombre')}, Sueldo: {self.formatear_pesos(self.cliente_sueldo)}"
                self.limpiar_campos_registro_cliente()
                self.mostrar_campos_tarjeta()
        elif self.radio_group.value == "nuevo":
            nombre = self.txt_nuevo_nombre.value.strip()
            cedula = self.txt_nueva_cedula.value.strip()
            sueldo = self.txt_nuevo_sueldo.value.strip()
            edad = self.txt_nueva_edad.value.strip()
            if not (nombre and cedula and sueldo and edad):
                self.mostrar_mensaje_temporal("Complete todos los datos del nuevo cliente")
                self.page.update()
                return
            try:
                sueldo = float(sueldo)
                edad = int(edad)
            except:
                self.mostrar_mensaje_temporal("Sueldo debe ser numérico y edad entera")
                self.page.update()
                return
            respuesta = self.controlador.registrar_cliente_nuevo(nombre, cedula, sueldo, edad)
            if "error" in respuesta:
                self.mostrar_mensaje_temporal(respuesta["error"])
                self.page.update()
                return
            else:
                self.cliente_id = respuesta.get("id_cliente")
                self.cliente_sueldo = float(sueldo)
                self.detalles_cliente.value = f"Cliente creado: {nombre}, Sueldo: {self.formatear_pesos(self.cliente_sueldo)}"
                self.limpiar_campos_registro_cliente()
                self.mostrar_campos_tarjeta()
        self.page.update()

    def limpiar_campos_registro_cliente(self):
        self.txt_cedula_existente.value = ""
        self.txt_nuevo_nombre.value = ""
        self.txt_nueva_cedula.value = ""
        self.txt_nuevo_sueldo.value = ""
        self.txt_nueva_edad.value = ""
        self.page.update()

    def mostrar_campos_tarjeta(self):
        self.aviso_registro.visible = False
        self.radio_group.visible = False
        self.txt_cedula_existente.visible = False
        self.txt_nuevo_nombre.visible = False
        self.txt_nueva_cedula.visible = False
        self.txt_nuevo_sueldo.visible = False
        self.txt_nueva_edad.visible = False
        self.btn_siguiente_registro.visible = False
        self.btn_atras.visible = False
        self.txt_nombre_banco.visible = True
        self.txt_cupo_total.visible = True
        self.btn_crear_tarjeta.visible = True
        if self.cliente_sueldo is not None:
            computed_cupo = 2 * self.cliente_sueldo
            self.txt_cupo_total.value = str(computed_cupo)
        self.page.update()

    def ocultar_registro(self, e):
        self.resetear_vista()
        self.page.update()

    def registrar_tarjeta(self, e):
        if not self.cliente_id:
            self.mostrar_mensaje_temporal("No se ha obtenido el cliente. Registre el cliente primero.")
            self.page.update()
            return
        nombre_banco = self.txt_nombre_banco.value.strip()
        cupo_total = self.txt_cupo_total.value.strip()
        numero_tarjeta = self.txt_tarjeta.value.strip()
        if not (nombre_banco and cupo_total and numero_tarjeta):
            self.mostrar_mensaje_temporal("Complete todos los datos de la tarjeta")
            self.page.update()
            return
        try:
            cupo_total = float(cupo_total)
        except ValueError:
            self.mostrar_mensaje_temporal("El cupo total debe ser un número")
            self.page.update()
            return
        datos = {
            "accion": "registrar_tarjeta",
            "tipo_cliente": "registrado",
            "id_cliente": self.cliente_id,
            "nombre_banco": nombre_banco,
            "numero_tarjeta": numero_tarjeta,
            "cupo_total": cupo_total
        }
        respuesta = self.controlador.registrar_tarjeta(datos)
        if "mensaje" in respuesta:
            self.mostrar_mensaje_temporal(f"Tarjeta de crédito del banco {nombre_banco} creada correctamente")
        else:
            self.mostrar_mensaje_temporal(respuesta.get("error", "No se ha podido crear la tarjeta"))
        self.controlador.buscar_cliente_por_tarjeta(numero_tarjeta)
        self.resetear_vista()
        self.page.update()

    @staticmethod
    def formatear_pesos(valor):
        return f"${valor:,.0f}"

    def mostrar_mensaje_temporal(self, mensaje):
        self.lbl_mensaje.value = mensaje
        self.page.update()
        threading.Timer(60, self.clear_lbl_mensaje).start()

    def clear_lbl_mensaje(self):
        self.lbl_mensaje.value = ""
        self.page.update()

    # --- Sección de registro de PAGO ---
    #def llenar_dropdown_pago(self, compras):
    #    """Llena el dropdown con las compras pendientes.
    #    Cada opción tendrá el formato: "id_compra|descripcion|monto"
    #    """
    #    opciones = []
    #    for compra in compras:
    #        # Se asume que cada compra es un diccionario con claves "id", "descripcion" y "monto"
    #        opcion_texto = f"{compra['id']}|{compra['descripcion']}|{self.formatear_pesos(compra['monto'])}"
    #        opciones.append(ft.dropdown.Option(text=opcion_texto))
    #    self.dropdown_compras_pago.options = opciones
    #    if opciones:
    #        self.dropdown_compras_pago.value = opciones[0].text
    #    else:
    #        self.dropdown_compras_pago.value = ""
    #    self.page.update()
    
    def llenar_dropdown_pago(self, compras):
        opciones = []
        for compra in compras:
            # Texto formateado para mostrar
            texto_formateado = f"{compra['descripcion']} - {self.formatear_pesos(compra['monto'])}"
            # Clave con los datos originales (incluyendo el float)
            clave = f"{compra['id']}|{compra['descripcion']}|{compra['monto']}"
            opciones.append(
                ft.dropdown.Option(
                    text=texto_formateado,  # Muestra el formato bonito
                    key=clave  # Guarda los datos originales como string
                )
            )
        
        self.dropdown_compras_pago.options = opciones
        if opciones:
            self.dropdown_compras_pago.value = opciones[0].key  # Usa la clave, no el texto
        else:
            self.dropdown_compras_pago.value = ""
        self.page.update()

    def seleccionar_compra(self, e):
        """Actualiza el campo 'Monto de Pago' según la compra seleccionada en el dropdown."""
        if self.dropdown_compras_pago.value:
            parts = self.dropdown_compras_pago.value.split("|")
            if len(parts) == 3:
                self.txt_monto_pago.value = parts[2]
                self.page.update()

    def mostrar_formulario_pago(self, e):
        if self.controlador.ultimo_detalle is None or not self.controlador.ultimo_detalle.get("compras"):
            self.mostrar_mensaje_temporal("No hay compras pendientes para pagar")
            self.page.update()
            return
        self.llenar_dropdown_pago(self.controlador.ultimo_detalle["compras"])
        self.dropdown_compras_pago.visible = True
        self.txt_fecha_pago.visible = True
        self.txt_monto_pago.visible = True
        self.txt_descripcion_pago.visible = True
        self.btn_confirmar_pago.visible = True
        self.btn_cancelar_pago.visible = True
        # Precargar el monto desde la primera opción del dropdown
        parts = self.dropdown_compras_pago.value.split("|")
        if len(parts) == 3:
            self.txt_monto_pago.value = parts[2]
            self.txt_monto_pago.disabled = True
        self.page.update()

    def ocultar_formulario_pago(self, e):
        self.dropdown_compras_pago.visible = False
        self.txt_fecha_pago.visible = False
        self.txt_monto_pago.visible = False
        self.txt_descripcion_pago.visible = False
        self.btn_confirmar_pago.visible = False
        self.btn_cancelar_pago.visible = False
        # Limpiar los valores del formulario de pago
        self.dropdown_compras_pago.value = ""
        self.txt_fecha_pago.value = ""
        self.txt_monto_pago.value = ""
        self.txt_descripcion_pago.value = ""
        self.txt_monto_pago.disabled = False
        self.page.update()

    def registrar_pago(self, e):
        fecha_pago = self.txt_fecha_pago.value.strip()
        monto_pago_str = self.txt_monto_pago.value.strip()
        descripcion_pago = self.txt_descripcion_pago.value.strip()
        numero_tarjeta = self.txt_tarjeta.value.strip()
        if not (fecha_pago and monto_pago_str):
            self.mostrar_mensaje_temporal("Complete la fecha y el monto del pago")
            self.page.update()
            return
        try:
            monto_pago = float(monto_pago_str)
        except ValueError:
            self.mostrar_mensaje_temporal("El monto de pago debe ser numérico")
            self.page.update()
            return
        if not self.dropdown_compras_pago.value:
            self.mostrar_mensaje_temporal("Seleccione la compra que desea pagar")
            self.page.update()
            return
        parts = self.dropdown_compras_pago.value.split("|")
        if len(parts) != 3:
            self.mostrar_mensaje_temporal("Error al leer la compra seleccionada")
            self.page.update()
            return
        id_compra = parts[0]
        compra_monto = float(parts[2])
        if not math.isclose(monto_pago, compra_monto, rel_tol=1e-5):
            self.mostrar_mensaje_temporal("El monto de pago debe ser igual al monto de la compra")
            self.page.update()
            return
        datos = {
            "accion": "registrar_pago",
            "numero_tarjeta": numero_tarjeta,
            "id_compra": id_compra,  # Enviamos solo el ID (ya extraído)
            "fecha_pago": fecha_pago,
            "monto_pagado": monto_pago,
            "descripcion": descripcion_pago
        }
        respuesta = self.controlador.registrar_pago(datos)
        if respuesta is None:
            self.mostrar_mensaje_temporal("Error de conexión: No se recibió respuesta del servidor")
        elif "mensaje" in respuesta:
            self.mostrar_mensaje_temporal(respuesta["mensaje"])
        else:
            self.mostrar_mensaje_temporal(respuesta.get("error", "No se pudo registrar el pago"))
        self.controlador.buscar_cliente_por_tarjeta(numero_tarjeta)
        self.ocultar_formulario_pago(e)
        self.page.update()

    def mostrar_mensaje(self, mensaje):
        self.lbl_mensaje.value = mensaje
        self.page.update()


    #def cargar_clientes(self, e):
    #    """Solicita la lista de clientes al controlador"""
    #    self.controlador.cargar_clientes()

    #def mostrar_clientes(self, clientes):
    #    #Llena la lista desplegable con los clientes obtenidos
    #    self.lista_clientes.options = [
    #        ft.dropdown.Option(str(cliente["id"]), cliente["nombre"])
    #        for cliente in clientes
    #    ]
    #    self.page.update()

    #def ver_detalle_cliente(self, e):
    #    #Solicita detalles del cliente seleccionado
    #    id_cliente = self.lista_clientes.value
    #    if not id_cliente:
    #        self.mostrar_mensaje("Selecciona un cliente")
    #        return

    #    fecha_inicio = self.fecha_inicio.value or None
    #    fecha_fin = self.fecha_fin.value or None
    #    self.controlador.mostrar_detalle_cliente(int(id_cliente), fecha_inicio, fecha_fin)
    
        
    #def mostrar_detalle(self, detalle):
    #    # Muestra la información del cliente, tarjetas y compras
    #    texto = f"Cliente: {detalle['nombre']}\nNúmero de compras: {detalle['num_compras']}\n\n"
    #    
    #    for tarjeta in detalle['tarjetas']:
    #        texto += f"Tarjeta ({tarjeta['nombre_banco']}): {tarjeta['numero_tarjeta']} - Cupo Total: {self.formatear_pesos(tarjeta['cupo_total'])} - Cupo Disponible: {self.formatear_pesos(tarjeta['cupo_disponible'])}\n"
#
    #    if detalle['compras']:
    #        texto += "\nCompras:\n"
    #        for compra in detalle['compras']:
    #            texto += f" Tarjeta ({compra['nombre_banco']} - {compra['numero_tarjeta']}): Fecha: {compra['fecha']}, Monto: {self.formatear_pesos(compra['monto'])}, Descripción: {compra['descripcion']}\n"

    #    self.detalles_cliente.value = texto
    #    self.page.update()

