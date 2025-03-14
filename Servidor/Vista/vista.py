import sys
import os

# Agregar el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# vista.py
import sys
import os
import socket
import json
import threading
from Controlador.Controlador import Controlador

class ServidorVista:
    def __init__(self, host="localhost", puerto=5000):
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
                    self.servidor.settimeout(1.0)
                    conexion, _ = self.servidor.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break

                print(f"Cliente conectado en {self.host}:{self.puerto}")
                hilo = threading.Thread(target=self.manejar_cliente, args=(conexion,))
                hilo.daemon = True
                hilo.start()
        except Exception as e:
            print(f"Error en {self.host}:{self.puerto}: {e}")
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
    # Recibir el puerto como argumento. Si no se proporciona, usa 5000 por defecto.
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    servidor = ServidorVista(host="localhost", puerto=puerto)
    hilo = threading.Thread(target=servidor.iniciar_servidor)
    hilo.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Interrupción recibida. Cerrando servidor...")
        servidor.cerrar_servidor()
        hilo.join()
