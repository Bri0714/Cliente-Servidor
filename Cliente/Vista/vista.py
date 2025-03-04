import flet as ft
from Controlador.controlador import ClienteControlador

class ClienteVista:
    def __init__(self, page: ft.Page):
        self.page = page
        # Habilitar scroll vertical en la página
        self.page.scroll = "always"
        
        self.controlador = ClienteControlador(self)
        self.conectado = False
        self.cliente_id = None      # Guardará el id del cliente obtenido
        self.cliente_sueldo = None  # Para calcular cupo_total = 2 * sueldo

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
                self.btn_registrar_compra,   # Botón para iniciar el registro de compra
                # Formulario de registro de compra (inicialmente oculto)
                self.txt_fecha_compra,
                self.txt_monto_compra,
                self.txt_descripcion_compra,
                self.btn_confirmar_compra,
                self.btn_cancelar_compra,
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

    # Métodos para resetear y limpiar controles
    def resetear_vista(self):
        """Oculta y limpia todos los controles de registro, detalles, compras y formulario de compra (menos lbl_mensaje)."""
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
        # Ocultar formulario de compra
        self.btn_registrar_compra.visible = False
        self.txt_fecha_compra.visible = False
        self.txt_monto_compra.visible = False
        self.txt_descripcion_compra.visible = False
        self.btn_confirmar_compra.visible = False
        self.btn_cancelar_compra.visible = False
        # Limpiar los contenidos de los campos (excepto lbl_mensaje)
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
        self.page.update()

    def limpiar_campos_registro_cliente(self):
        """Limpia únicamente los campos de registro del cliente."""
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
        # Validar que se haya ingresado un número de tarjeta
        if not self.txt_tarjeta.value.strip():
            self.resetear_vista()
            self.lbl_mensaje.value = "Debe ingresar un número de tarjeta válido"
            self.page.update()
            return
        # Conservar el número y reiniciar la vista para iniciar la búsqueda sin datos residuales
        num = self.txt_tarjeta.value.strip()
        self.resetear_vista()
        self.txt_tarjeta.value = num
        fecha_inicio = self.fecha_inicio.value.strip() or None
        fecha_fin = self.fecha_fin.value.strip() or None
        self.controlador.buscar_cliente_por_tarjeta(num, fecha_inicio, fecha_fin)
        self.page.update()

    def mostrar_detalle(self, detalle):
        if "error" in detalle:
            # Si la tarjeta no existe, se muestra la sección de registro
            self.mostrar_registro_tarjeta()
            self.lbl_mensaje.value = detalle["error"]
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
            # Habilitar el botón para registrar compra
            self.btn_registrar_compra.visible = True
        self.page.update()

    def mostrar_compras(self, e):
        if self.controlador.ultimo_detalle is None:
            self.lbl_mensaje.value = "Primero vea los detalles de la tarjeta"
            self.page.update()
            return
        compras = self.controlador.ultimo_detalle.get("compras", [])
        if not compras:
            self.lbl_mensaje.value = "No hay compras para mostrar"
            self.page.update()
            return
        texto = "Compras:\n"
        for compra in compras:
            texto += (
                f"Tarjeta ({compra['nombre_banco']}): "
                f"Fecha: {compra['fecha']}, Monto: {self.formatear_pesos(compra['monto'])}, "
                f"Descripción: {compra['descripcion']}\n"
            )
        self.detalles_cliente.value = texto
        self.page.update()

    # --- Sección de registro de compra ---
    def mostrar_formulario_compra(self, e):
        # Hace visibles los controles para registrar la compra
        self.txt_fecha_compra.visible = True
        self.txt_monto_compra.visible = True
        self.txt_descripcion_compra.visible = True
        self.btn_confirmar_compra.visible = True
        self.btn_cancelar_compra.visible = True
        # Opcional: se pueden asignar valores por defecto, p.ej. la fecha actual
        self.txt_fecha_compra.value = ""
        self.txt_monto_compra.value = ""
        self.txt_descripcion_compra.value = ""
        self.page.update()

    def ocultar_formulario_compra(self, e):
        # Oculta y limpia el formulario de compra
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
        # Método para registrar una compra
        fecha = self.txt_fecha_compra.value.strip()
        monto = self.txt_monto_compra.value.strip()
        descripcion = self.txt_descripcion_compra.value.strip()
        numero_tarjeta = self.txt_tarjeta.value.strip()  # Se utiliza el número ingresado previamente
        if not (fecha and monto and descripcion):
            self.lbl_mensaje.value = "Complete todos los datos de la compra"
            self.page.update()
            return
        try:
            monto = float(monto)
        except ValueError:
            self.lbl_mensaje.value = "El monto debe ser numérico"
            self.page.update()
            return
        datos = {
            "accion": "registrar_compra",
            "numero_tarjeta": numero_tarjeta,
            "fecha": fecha,
            "monto": monto,
            "descripcion": descripcion
        }
        respuesta = self.controlador.modelo.enviar_peticion(datos)
        if respuesta is None:
            self.lbl_mensaje.value = "Error de conexión: No se recibió respuesta del servidor"
        elif "mensaje" in respuesta:
            self.lbl_mensaje.value = respuesta["mensaje"]
        else:
            self.lbl_mensaje.value = respuesta.get("error", "No se pudo registrar la compra")
        # Actualizar detalles para ver el cupo actualizado
        self.controlador.buscar_cliente_por_tarjeta(numero_tarjeta)
        self.resetear_vista()
        self.page.update()


    # --- Sección de registro de tarjeta y cliente (ya existente) ---
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
                self.lbl_mensaje.value = "Ingrese la cédula del cliente"
                self.page.update()
                return
            respuesta = self.controlador.buscar_cliente_por_cedula(cedula)
            if "error" in respuesta:
                self.lbl_mensaje.value = f"Cliente con cédula {cedula} no ha sido encontrado"
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
                self.lbl_mensaje.value = "Complete todos los datos del nuevo cliente"
                self.page.update()
                return
            try:
                sueldo = float(sueldo)
                edad = int(edad)
            except:
                self.lbl_mensaje.value = "Sueldo debe ser numérico y edad entera"
                self.page.update()
                return
            respuesta = self.controlador.registrar_cliente_nuevo(nombre, cedula, sueldo, edad)
            if "error" in respuesta:
                self.lbl_mensaje.value = respuesta["error"]
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
            self.lbl_mensaje.value = "No se ha obtenido el cliente. Registre el cliente primero."
            self.page.update()
            return
        nombre_banco = self.txt_nombre_banco.value.strip()
        cupo_total = self.txt_cupo_total.value.strip()
        numero_tarjeta = self.txt_tarjeta.value.strip()
        if not (nombre_banco and cupo_total and numero_tarjeta):
            self.lbl_mensaje.value = "Complete todos los datos de la tarjeta"
            self.page.update()
            return
        try:
            cupo_total = float(cupo_total)
        except ValueError:
            self.lbl_mensaje.value = "El cupo total debe ser un número"
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
            self.lbl_mensaje.value = f"Tarjeta de crédito del banco {nombre_banco} creada correctamente"
        else:
            self.lbl_mensaje.value = respuesta.get("error", "No se ha podido crear la tarjeta")
        self.controlador.buscar_cliente_por_tarjeta(numero_tarjeta)
        self.resetear_vista()
        self.page.update()

    @staticmethod
    def formatear_pesos(valor):
        return f"${valor:,.0f} COP"

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

