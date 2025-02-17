from Modelo.modelo import ClienteModelo

class ClienteControlador:
    #Clase que maneja la lógica de la aplicación
    def __init__(self, vista):
        self.modelo = ClienteModelo()
        self.vista = vista

    def cargar_clientes(self):
        #Obtiene la lista de clientes y la envía a la vista
        clientes = self.modelo.obtener_clientes()
        if "clientes" in clientes:
            self.vista.mostrar_clientes(clientes["clientes"])
        else:
            self.vista.mostrar_mensaje("Error al obtener clientes")

    def mostrar_detalle_cliente(self, id_cliente, fecha_inicio=None, fecha_fin=None):
        #Obtiene los detalles del cliente y los envía a la vista
        detalle = self.modelo.obtener_detalle_cliente(id_cliente, fecha_inicio, fecha_fin)
        if "error" in detalle:
            self.vista.mostrar_mensaje(detalle["error"])
        else:
            self.vista.mostrar_detalle(detalle)
