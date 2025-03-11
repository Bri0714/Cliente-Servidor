import socket
import json

class ClienteModelo:
    #Clase encargada de la comunicación con el servidor

    def __init__(self, host="localhost", puerto=9000):
        self.host = host
        self.puerto = puerto
        self.sock = None  # Atributo para la conexión persistente
        self.conectar_persistente()  # Establece la conexión persistente al iniciar

    def conectar_persistente(self):
        """Establece una conexión persistente con el balanceador/servidor."""
        if self.sock is None:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.puerto))
                print("Conexión persistente establecida con el balanceador.")
            except Exception as e:
                self.sock = None
                print("Error en conexión persistente:", e)
                return {"error": f"Error de conexión persistente: {e}"}
        return {"estado": "conectado"}

    def enviar_peticion(self, datos):
        """Envía una petición JSON al servidor y recibe la respuesta"""
        try:
            # Se utiliza la conexión persistente si está disponible
            if self.sock is None:
                # En caso de no haber conexión persistente, se crea una conexión temporal
                cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                cliente.connect((self.host, self.puerto))
                cliente.sendall(json.dumps(datos).encode("utf-8"))
                respuesta = json.loads(cliente.recv(4096).decode("utf-8"))
                cliente.close()
                return respuesta
            else:
                self.sock.sendall(json.dumps(datos).encode("utf-8"))
                respuesta = json.loads(self.sock.recv(4096).decode("utf-8"))
                return respuesta
        except Exception as e:
            # Si ocurre un error, se cierra la conexión persistente para que se pueda reestablecer
            if self.sock is not None:
                try:
                    self.sock.close()
                except Exception:
                    pass
                self.sock = None
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
