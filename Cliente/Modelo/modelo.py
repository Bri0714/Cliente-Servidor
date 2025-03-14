import socket
import json

class ClienteModelo:
    def __init__(self, host="localhost", puerto=9000):
        self.host = host
        self.puerto = puerto
        self.sock = None  # Conexión persistente
        self.welcome_received = False

    def conectar_persistente(self):
        """Establece una conexión persistente con el balanceador/servidor."""
        if self.sock is None:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.puerto))
                # Recibir el mensaje de bienvenida
                data = self.sock.recv(4096)
                if data:
                    welcome = json.loads(data.decode("utf-8"))
                    print(welcome["mensaje"])
                    self.welcome_received = True
                    return welcome
                else:
                    return {"error": "No se recibió mensaje de bienvenida."}
            except Exception as e:
                self.sock = None
                print("Error en conexión persistente:", e)
                return {"error": f"Error de conexión persistente: {e}"}
        return {"estado": "conectado"}

    def enviar_peticion(self, datos):
        try:
            if self.sock is not None:
                self.sock.sendall(json.dumps(datos).encode("utf-8"))
                respuesta = json.loads(self.sock.recv(4096).decode("utf-8"))
                return respuesta
            else:
                temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                temp_sock.connect((self.host, self.puerto))
                temp_sock.recv(4096)  # Descartar mensaje de bienvenida
                temp_sock.sendall(json.dumps(datos).encode("utf-8"))
                respuesta = json.loads(temp_sock.recv(4096).decode("utf-8"))
                temp_sock.close()
                return respuesta
        except Exception as e:
            # Al detectar error, cerramos la conexión persistente y dejamos que el monitor se encargue de reconectar.
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
