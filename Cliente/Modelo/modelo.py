import socket
import json

class ClienteModelo:
    #Clase encargada de la comunicación con el servidor

    def __init__(self, host="localhost", puerto=5000):
        self.host = host
        self.puerto = puerto

    def enviar_peticion(self, datos):
        """Envía una petición JSON al servidor y recibe la respuesta"""
        try:
            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cliente.connect((self.host, self.puerto))
            cliente.sendall(json.dumps(datos).encode("utf-8"))
            respuesta = json.loads(cliente.recv(4096).decode("utf-8"))
            cliente.close()
            return respuesta
        except Exception as e:
            return {"error": f"Error de conexión: {e}"}
        
    def conectar(self):
        return self.enviar_peticion({"accion": "ping"})

    #def obtener_clientes(self):
    #    #Solicita la lista de clientes al servidor
    #    return self.enviar_peticion({"accion": "listar_clientes"})
    
    #def obtener_detalle_cliente(self, id_cliente, fecha_inicio=None, fecha_fin=None):
    #    #Solicita detalles de un cliente, incluyendo tarjetas y compras
    #    datos = {"accion": "detalle_cliente", "id_cliente": id_cliente}
    #    if fecha_inicio and fecha_fin:
    #        datos["fecha_inicio"] = fecha_inicio
    #        datos["fecha_fin"] = fecha_fin
    #    return self.enviar_peticion(datos)
    
    def obtener_detalle_por_tarjeta(self, numero_tarjeta, fecha_inicio=None, fecha_fin=None):
        # Solicita detalles usando el número de tarjeta
        datos = {"accion": "detalle_tarjeta", "numero_tarjeta": numero_tarjeta}
        if fecha_inicio and fecha_fin:
            datos["fecha_inicio"] = fecha_inicio
            datos["fecha_fin"] = fecha_fin
        return self.enviar_peticion(datos)
