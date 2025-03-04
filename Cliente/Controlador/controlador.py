from Modelo.modelo import ClienteModelo
import time

class ClienteControlador:
    def __init__(self, vista):
        self.modelo = ClienteModelo()
        self.vista = vista
        self.ultimo_detalle = None

    def conectar_al_servidor(self):
        max_reintentos = 5
        for intento in range(1, max_reintentos + 1):
            respuesta = self.modelo.conectar()
            if "mensaje" in respuesta:
                mensaje = respuesta["mensaje"]
                # Se muestra el mensaje en la consola y en la vista.
                print(mensaje)
                self.vista.mostrar_mensaje(mensaje)
                self.vista.habilitar_ver_detalles()
                return True
            else:
                reintento_msg = f"{intento} reintento de conexión"
                print(reintento_msg)
                self.vista.mostrar_mensaje(reintento_msg)
                if intento < max_reintentos:
                    time.sleep(60)  # Espera 1 minuto antes del siguiente intento.
        # Si después de 5 intentos aún no se conecta:
        error_msg = "No se pudo conectar al servidor, cerrando el cliente."
        print(error_msg)
        self.vista.mostrar_mensaje(error_msg)
        self.vista.page.window.destroy()  # O el método correspondiente para cerrar la aplicación
    
    def buscar_cliente_por_tarjeta(self, numero_tarjeta, fecha_inicio=None, fecha_fin=None):
        detalle = self.modelo.obtener_detalle_por_tarjeta(numero_tarjeta, fecha_inicio, fecha_fin)
        if "error" in detalle:
            self.vista.mostrar_mensaje(detalle["error"])
            self.vista.mostrar_registro_tarjeta()
        else:
            self.ultimo_detalle = detalle  # Guardamos el último detalle obtenido
            self.vista.mostrar_detalle(detalle)

    def registrar_tarjeta(self, datos):
        respuesta = self.modelo.enviar_peticion(datos)
        print("Respuesta del servidor:", respuesta)  # Debugging
        return respuesta

    #def cargar_clientes(self):
    #    #Obtiene la lista de clientes y la envía a la vista
    #    clientes = self.modelo.obtener_clientes()
    #    if "clientes" in clientes:
    #        self.vista.mostrar_clientes(clientes["clientes"])
    #    else:
    #        self.vista.mostrar_mensaje("Error al obtener clientes")
    
        
    def buscar_cliente_por_cedula(self, cedula):
        datos = {"accion": "buscar_cliente_por_cedula", "cedula": cedula}
        return self.modelo.enviar_peticion(datos)


    def registrar_cliente_nuevo(self, nombre, cedula, sueldo, edad):
        datos = {
            "accion": "registrar_cliente_nuevo",
            "nombre": nombre,
            "cedula": cedula,
            "sueldo": sueldo,
            "edad": edad
        }
        return self.modelo.enviar_peticion(datos)
            
    def mostrar_compras(self):
        # Muestra el listado de compras del detalle previamente obtenido
        if self.ultimo_detalle and "compras" in self.ultimo_detalle:
            self.vista.mostrar_compras(self.ultimo_detalle["compras"])
        else:
            self.vista.mostrar_mensaje("No hay compras para mostrar")
            
    def mostrar_detalle_cliente(self, id_cliente, fecha_inicio=None, fecha_fin=None):
        #Obtiene los detalles del cliente y los envía a la vista
        detalle = self.modelo.obtener_detalle_cliente(id_cliente, fecha_inicio, fecha_fin)
        if "error" in detalle:
            self.vista.mostrar_mensaje(detalle["error"])
        else:
            self.vista.mostrar_detalle(detalle)
