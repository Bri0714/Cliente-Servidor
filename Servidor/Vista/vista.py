import sys
import os

# Agregar el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import socket
import json
import threading
from Controlador.Controlador import Controlador

class ServidorVista:
    #Clase que representa el servidor y maneja múltiples clientes usando hilos.

    def __init__(self, host="localhost", puerto=5000):
        #Inicializa el servidor con los datos básicos."""
        self.host = host
        self.puerto = puerto
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controlador = Controlador()  # Instancia del controlador

    def iniciar_servidor(self):
        #Inicia el servidor y espera conexiones de clientes.
        self.servidor.bind((self.host, self.puerto)) # .bind() enlaza el socket a la dirección y puerto especificados
        self.servidor.listen(5) # .listen() pone el socket en modo de escucha para aceptar conexiones
        print(f"Servidor iniciado en {self.host}:{self.puerto}")
        
        while True:
            conexion, _ = self.servidor.accept()
            print("Cliente conectado.")
            hilo = threading.Thread(target=self.manejar_cliente, args=(conexion,))
            hilo.start()  # Iniciar el hilo para manejar al cliente

    def manejar_cliente(self, conexion):
        #Maneja la conexión de un cliente en un hilo separado.
        try:
            datos = json.loads(conexion.recv(1024).decode("utf-8"))
            respuesta = self.controlador.procesar_peticion(datos)  # Procesar petición con el controlador
            conexion.sendall(json.dumps(respuesta).encode("utf-8"))
        except Exception as e:
            conexion.sendall(json.dumps({"error": f"Error del servidor: {e}"}).encode("utf-8"))
        finally:
            conexion.close()

if __name__ == "__main__":
    servidor = ServidorVista()
    servidor.iniciar_servidor()