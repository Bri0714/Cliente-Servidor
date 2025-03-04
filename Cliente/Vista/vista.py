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

        # Envolver todos los controles en un contenedor (Column) con scroll vertical
        scrollable_content = ft.Column(
            controls=[
                self.btn_conectar,
                self.txt_tarjeta,
                self.fecha_inicio,
                self.fecha_fin,
                self.btn_ver_detalles,
                self.btn_compras,
                self.detalles_cliente,
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

    def resetear_vista(self):
        """Oculta y limpia todos los controles de registro, detalles y compras previos."""
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
        # Limpiar contenidos de los campos (excepto el número de tarjeta, si se desea conservarlo)
        self.txt_cedula_existente.value = ""
        self.txt_nuevo_nombre.value = ""
        self.txt_nueva_cedula.value = ""
        self.txt_nuevo_sueldo.value = ""
        self.txt_nueva_edad.value = ""
        self.txt_nombre_banco.value = ""
        self.txt_cupo_total.value = ""
        self.page.update()

    def limpiar_campos_registro_cliente(self):
        """Limpia únicamente los campos de registro del cliente."""
        self.txt_cedula_existente.value = ""
        self.txt_nuevo_nombre.value = ""
        self.txt_nueva_cedula.value = ""
        self.txt_nuevo_sueldo.value = ""
        self.txt_nueva_edad.value = ""
        self.page.update()

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
        if not self.txt_tarjeta.value:
            self.mostrar_mensaje("Debe ingresar un número de tarjeta válido")
            return
        # Conservar el número y reiniciar la vista para iniciar la búsqueda sin datos residuales
        num = self.txt_tarjeta.value
        self.resetear_vista()
        self.txt_tarjeta.value = num
        fecha_inicio = self.fecha_inicio.value or None
        fecha_fin = self.fecha_fin.value or None
        self.controlador.buscar_cliente_por_tarjeta(num, fecha_inicio, fecha_fin)
        self.page.update()

    def mostrar_detalle(self, detalle):
        if "error" in detalle:
            # Si la tarjeta no existe, se muestra la sección de registro
            self.mostrar_registro_tarjeta()
            self.mostrar_mensaje(detalle["error"])
        else:
            texto = f"Titular: {detalle['nombre']}\n"
            card = None
            for t in detalle['tarjetas']:
                if t['numero_tarjeta'] == self.txt_tarjeta.value:
                    card = t
                    break
            if card:
                texto += f"Banco: {card['nombre_banco']}\n"
                texto += f"Cupo Total: {self.formatear_pesos(card['cupo_total'])}\n"
                texto += f"Cupo Disponible: {self.formatear_pesos(card['cupo_disponible'])}\n"
            texto += f"Número de compras: {detalle['num_compras']}\n"
            self.detalles_cliente.value = texto
            self.btn_compras.disabled = False if detalle['compras'] else True
        self.page.update()

    def mostrar_compras(self, e):
        if self.controlador.ultimo_detalle is None:
            self.mostrar_mensaje("Primero vea los detalles de la tarjeta")
            return
        compras = self.controlador.ultimo_detalle.get("compras", [])
        if not compras:
            self.mostrar_mensaje("No hay compras para mostrar")
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
        # Este método se invoca al presionar "Siguiente" en la sección de registro
        if self.radio_group.value == "registrado":
            cedula = self.txt_cedula_existente.value
            if not cedula:
                self.mostrar_mensaje("Ingrese la cédula del cliente")
                return
            respuesta = self.controlador.buscar_cliente_por_cedula(cedula)
            if "error" in respuesta:
                self.mostrar_mensaje(f"Cliente con cédula {cedula} no ha sido encontrado")
                return
            else:
                self.cliente_id = respuesta.get("id_cliente")
                self.cliente_sueldo = respuesta.get("sueldo")
                self.detalles_cliente.value = f"Cliente encontrado: {respuesta.get('nombre')}, Sueldo: {self.formatear_pesos(self.cliente_sueldo)}"
                self.limpiar_campos_registro_cliente()
                self.mostrar_campos_tarjeta()
        elif self.radio_group.value == "nuevo":
            nombre = self.txt_nuevo_nombre.value
            cedula = self.txt_nueva_cedula.value
            sueldo = self.txt_nuevo_sueldo.value
            edad = self.txt_nueva_edad.value
            if not (nombre and cedula and sueldo and edad):
                self.mostrar_mensaje("Complete todos los datos del nuevo cliente")
                return
            try:
                sueldo = float(sueldo)
                edad = int(edad)
            except:
                self.mostrar_mensaje("Sueldo debe ser numérico y edad entera")
                return
            respuesta = self.controlador.registrar_cliente_nuevo(nombre, cedula, sueldo, edad)
            if "error" in respuesta:
                self.mostrar_mensaje(respuesta["error"])
                return
            else:
                self.cliente_id = respuesta.get("id_cliente")
                self.cliente_sueldo = float(sueldo)
                self.detalles_cliente.value = f"Cliente creado: {nombre}, Sueldo: {self.formatear_pesos(self.cliente_sueldo)}"
                self.limpiar_campos_registro_cliente()
                self.mostrar_campos_tarjeta()
        self.page.update()

    def limpiar_campos_registro_cliente(self):
        """Limpia los campos de registro del cliente."""
        self.txt_cedula_existente.value = ""
        self.txt_nuevo_nombre.value = ""
        self.txt_nueva_cedula.value = ""
        self.txt_nuevo_sueldo.value = ""
        self.txt_nueva_edad.value = ""
        self.page.update()

    def mostrar_campos_tarjeta(self):
        # Oculta los controles de registro y muestra los campos para crear la tarjeta
        self.aviso_registro.visible = False
        self.radio_group.visible = False
        self.txt_cedula_existente.visible = False
        self.txt_nuevo_nombre.visible = False
        self.txt_nueva_cedula.visible = False
        self.txt_nuevo_sueldo.visible = False
        self.txt_nueva_edad.visible = False
        self.btn_siguiente_registro.visible = False
        self.btn_atras.visible = False
        # Mostrar los campos para la tarjeta
        self.txt_nombre_banco.visible = True
        self.txt_cupo_total.visible = True
        self.btn_crear_tarjeta.visible = True
        # Pre-cargar el número de tarjeta (el mismo ingresado al inicio)
        # Calcular cupo_total como el doble del sueldo del cliente
        if self.cliente_sueldo is not None:
            computed_cupo = 2 * self.cliente_sueldo
            self.txt_cupo_total.value = str(computed_cupo)
        self.page.update()

    def ocultar_registro(self, e):
        self.resetear_vista()
        self.page.update()

    def registrar_tarjeta(self, e):
        if not self.cliente_id:
            self.mostrar_mensaje("No se ha obtenido el cliente. Registre el cliente primero.")
            return
        nombre_banco = self.txt_nombre_banco.value
        cupo_total = self.txt_cupo_total.value  # Ya calculado automáticamente
        numero_tarjeta = self.txt_tarjeta.value  # Se utiliza el número ingresado al inicio
        if not (nombre_banco and cupo_total and numero_tarjeta):
            self.mostrar_mensaje("Complete todos los datos de la tarjeta")
            return
        datos = {
            "accion": "registrar_tarjeta",
            "tipo_cliente": "registrado",  # Se asume que el cliente ya está creado
            "id_cliente": self.cliente_id,
            "nombre_banco": nombre_banco,
            "numero_tarjeta": numero_tarjeta,
            "cupo_total": None
        }
        try:
            datos["cupo_total"] = float(cupo_total)
        except ValueError:
            self.mostrar_mensaje("El cupo total debe ser un número")
            return
        respuesta = self.controlador.registrar_tarjeta(datos)
        if "mensaje" in respuesta:
            self.mostrar_mensaje(f"Tarjeta de crédito del banco {nombre_banco} creada correctamente")
        else:
            self.mostrar_mensaje(respuesta.get("error", "No se ha podido crear la tarjeta"))
        # Actualiza el detalle (opcional) y luego limpia la vista
        self.controlador.buscar_cliente_por_tarjeta(numero_tarjeta)
        self.resetear_vista()
        self.page.update()

    @staticmethod
    def formatear_pesos(valor):
        return f"${valor:,.0f} COP"

    def mostrar_mensaje(self, mensaje):
        self.page.snack_bar = ft.SnackBar(ft.Text(mensaje), duration=3)
        self.page.snack_bar.open = True
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

