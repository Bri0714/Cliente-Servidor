import sys
import os

# Agregar el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import socket
import json
import threading
from Controlador.Controlador import Controlador

class ServidorVista:
    # Clase que representa el servidor y maneja múltiples clientes usando hilos.

    def __init__(self, host="localhost", puerto=5000):
        # Inicializa el servidor con los datos básicos.
        self.host = host
        self.puerto = puerto
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.controlador = Controlador()  # Instancia del controlador
        self.ejecutando = True

    def iniciar_servidor(self):
        try:
            self.servidor.bind((self.host, self.puerto))
            self.servidor.listen(5)
            print(f"Servidor iniciado en {self.host}:{self.puerto}")
            
            while self.ejecutando:
                try:
                    # Usamos un timeout para poder revisar la bandera de cierre
                    self.servidor.settimeout(1.0)
                    conexion, _ = self.servidor.accept()
                except socket.timeout:
                    continue  # Vuelve al inicio del while y revisa si se debe cerrar
                except OSError:
                    # Puede ocurrir si el socket se cierra mientras se espera accept()
                    break

                print(f"Cliente conectado al servidor en {self.host}:{self.puerto}.")
                hilo = threading.Thread(target=self.manejar_cliente, args=(conexion,))
                hilo.daemon = True  # Marcar como daemon para que no impidan el cierre
                hilo.start()
        except Exception as e:
            print(f"Error en el servidor en {self.host}:{self.puerto}: {e}")
        finally:
            self.cerrar_servidor()

    def manejar_cliente(self, conexion):
        try:
            datos = json.loads(conexion.recv(1024).decode("utf-8"))
            respuesta = self.controlador.procesar_peticion(datos)
            conexion.sendall(json.dumps(respuesta).encode("utf-8"))
        except Exception as e:
            try:
                conexion.sendall(json.dumps({"error": f"Error del servidor: {e}"}).encode("utf-8"))
            except Exception:
                pass
        finally:
            conexion.close()

    def cerrar_servidor(self):
        self.ejecutando = False
        try:
            self.servidor.close()
        except Exception as e:
            print("Error al cerrar el servidor:", e)
        print(f"Servidor en {self.host}:{self.puerto} cerrado.")

if __name__ == "__main__":
    # Instancia de dos servidores en puertos diferentes
    servidor_1 = ServidorVista(host="localhost", puerto=5000)
    hilo1 = threading.Thread(target=servidor_1.iniciar_servidor)
    hilo1.start()
    
    # Iniciar cada servidor en un hilo separado
    # servidor_2 = ServidorVista(host="localhost", puerto=5001)
    # hilo2 = threading.Thread(target=servidor_2.iniciar_servidor)
    # hilo2.start()
    
    try:
        # El hilo principal espera indefinidamente
        while True:
            pass
    except KeyboardInterrupt:
        print("Interrupción recibida. Cerrando servidores...")
        servidor_1.cerrar_servidor()
        # servidor_2.cerrar_servidor()
        hilo1.join()
        # hilo2.join()
    
