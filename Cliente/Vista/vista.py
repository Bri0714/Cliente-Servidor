import flet as ft
from Controlador.controlador import ClienteControlador

class ClienteVista:
    #Interfaz gráfica de la aplicación

    def __init__(self, page: ft.Page):
        self.page = page
        self.controlador = ClienteControlador(self)
        self.lista_clientes = ft.Dropdown()
        self.detalles_cliente = ft.Text(value="Selecciona un cliente para ver detalles")

        # Botón para cargar clientes
        self.btn_cargar = ft.ElevatedButton("Cargar Clientes", on_click=self.cargar_clientes)

        # Botón para ver detalles
        self.btn_detalle = ft.ElevatedButton("Ver Detalles", on_click=self.ver_detalle_cliente)

        # Campos de fecha para filtrar compras
        self.fecha_inicio = ft.TextField(label="Fecha Inicio (YYYY-MM-DD)")
        self.fecha_fin = ft.TextField(label="Fecha Fin (YYYY-MM-DD)")

        # Layout de la interfaz
        self.page.add(
            self.btn_cargar,
            self.lista_clientes,
            self.fecha_inicio,
            self.fecha_fin,
            self.btn_detalle,
            self.detalles_cliente
        )

    def cargar_clientes(self, e):
        """Solicita la lista de clientes al controlador"""
        self.controlador.cargar_clientes()

    def mostrar_clientes(self, clientes):
        """Llena la lista desplegable con los clientes obtenidos"""
        self.lista_clientes.options = [
            ft.dropdown.Option(str(cliente["id"]), cliente["nombre"])
            for cliente in clientes
        ]
        self.page.update()

    def ver_detalle_cliente(self, e):
        #Solicita detalles del cliente seleccionado
        id_cliente = self.lista_clientes.value
        if not id_cliente:
            self.mostrar_mensaje("Selecciona un cliente")
            return

        fecha_inicio = self.fecha_inicio.value or None
        fecha_fin = self.fecha_fin.value or None
        self.controlador.mostrar_detalle_cliente(int(id_cliente), fecha_inicio, fecha_fin)

    def mostrar_detalle(self, detalle):
        #Muestra la información del cliente, tarjetas y compras
        texto = f"Cliente: {detalle['nombre']}\nNúmero de compras: {detalle['num_compras']}\n\n"
        
        for tarjeta in detalle['tarjetas']:
            texto += f"Tarjeta ({tarjeta['nombre_banco']}): {tarjeta['numero_tarjeta']} - Cupo: {tarjeta['cupo_total']}\n"

        if detalle['compras']:
            texto += "\nCompras:\n"
            for compra in detalle['compras']:
                texto += f"Fecha: {compra['fecha']}, Monto: {compra['monto']}, Descripción: {compra['descripcion']}\n"

        self.detalles_cliente.value = texto
        self.page.update()

    def mostrar_mensaje(self, mensaje):
        #Muestra un mensaje de error o advertencia
        self.page.snack_bar = ft.SnackBar(ft.Text(mensaje))
        self.page.snack_bar.open = True
        self.page.update()
