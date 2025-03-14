from Modelo.modelo import ClienteModelo
import time
import threading

class ClienteControlador:
    def __init__(self, vista):
        self.modelo = ClienteModelo()
        self.vista = vista
        self.ultimo_detalle = None
        self.tarjeta_actual = None  # Para almacenar la tarjeta actualmente consultada
        self.pending_actions = []   # Cola para almacenar acciones pendientes en caso de fallo

        # Inicia un hilo en background para monitorizar la conexión
        #threading.Thread(target=self.monitor_conexion, daemon=True).start()
        

    def monitor_conexion(self):
        while True:
            time.sleep(10)
            respuesta = self.modelo.conectar()  # Realiza un ping
            if "mensaje" in respuesta:
                self.procesar_acciones_pendientes()
            else:
                # Si falla el ping, se notifica y se reconecta automáticamente
                print("Conexión perdida, intentando reconectar automáticamente...")
                self.vista.conectado = False
                self.vista.mostrar_mensaje("El servidor se ha caído, reconectando...")
                # Se llama a reconectar sin necesidad de acción del usuario
                self.conectar_al_servidor()


    def conectar_al_servidor(self):
        max_reintentos = 5
        for intento in range(1, max_reintentos + 1):
            respuesta = self.modelo.conectar_persistente()
            if "estado" in respuesta and respuesta["estado"] == "conectado":
                puerto = respuesta.get("puerto")
                mensaje = f"Cliente conectado exitosamente a puerto {puerto}."
                print(mensaje)
                self.vista.mostrar_mensaje(mensaje)
                self.vista.habilitar_ver_detalles()
                self.vista.conectado = True  # Se marca que ya se conectó
                # Iniciamos el monitor (si aún no está en ejecución)
                if not hasattr(self.vista, "monitor_enabled") or not self.vista.monitor_enabled:
                    self.vista.monitor_enabled = True
                    threading.Thread(target=self.monitor_conexion, daemon=True).start()
                return True
            else:
                reintento_msg = f"{intento} reintento de conexión"
                print(reintento_msg)
                self.vista.mostrar_mensaje(reintento_msg)
                if intento < max_reintentos:
                    time.sleep(25)
        error_msg = "No se pudo conectar al servidor, cerrando el cliente."
        print(error_msg)
        self.vista.mostrar_mensaje(error_msg)
        self.vista.page.window.destroy()


    def agregar_a_cola(self, accion, datos):
        """Agrega una acción pendiente a la cola para reenvío al reconectar."""
        self.pending_actions.append((accion, datos))
        self.vista.mostrar_mensaje(f"Acción '{accion}' agregada a la cola y se enviará al reconectar.")

    def procesar_acciones_pendientes(self):
        """Recorre la cola de acciones pendientes y reenvía cada petición que se procese correctamente."""
        if not self.pending_actions:
            return

        # Se recorre una copia de la cola para eliminar elementos sin problemas
        for accion, datos in self.pending_actions.copy():
            respuesta = self.modelo.enviar_peticion(datos)
            if "error" not in respuesta:
                self.pending_actions.remove((accion, datos))
                self.vista.mostrar_mensaje(f"Acción '{accion}' procesada correctamente.")
                print(f"Acción '{accion}' procesada: {respuesta}")
            else:
                print(f"Reintento de '{accion}' fallido: {respuesta['error']}")

    # --- Métodos existentes ---

    # Liberar tarjeta anterior ANTES de asignar la nueva
    def buscar_cliente_por_tarjeta(self, numero_tarjeta, fecha_inicio=None, fecha_fin=None):
        if self.tarjeta_actual:
            self.liberar_tarjeta(self.tarjeta_actual)
            self.tarjeta_actual = None  # Asegurar que se borra la referencia

        detalle = self.modelo.obtener_detalle_por_tarjeta(numero_tarjeta, fecha_inicio, fecha_fin)
        
        # Si se recibió un mensaje de redirección, lo mostramos y salimos
        if "estado" in detalle and detalle["estado"] == "redirigido":
            self.vista.mostrar_mensaje(detalle["mensaje"])
            return

        if "error" in detalle:
            if "ya está siendo consultado" in detalle["error"]:
                self.vista.mostrar_mensaje(detalle["error"])
            return
        else:
            self.tarjeta_actual = numero_tarjeta  # Asignar solo si no hay error
            self.ultimo_detalle = detalle
            self.vista.mostrar_detalle(detalle)


    def liberar_tarjeta(self, numero_tarjeta):
        if numero_tarjeta:
            datos = {"accion": "liberar_tarjeta", "numero_tarjeta": numero_tarjeta}
            try:
                # Enviar liberación y esperar confirmación
                respuesta = self.modelo.enviar_peticion(datos)
                print(f"Liberación exitosa de tarjeta {numero_tarjeta}: {respuesta}")
            except Exception as e:
                print(f"Error al liberar tarjeta: {str(e)}")
            finally:
                self.tarjeta_actual = None

    def registrar_tarjeta(self, datos):
        respuesta = self.modelo.enviar_peticion(datos)
        print("Respuesta del servidor:", respuesta)  # Debugging
        if "error" in respuesta and "conexión" in respuesta["error"].lower():
            self.agregar_a_cola("registrar_tarjeta", datos)
        return respuesta
    
    def registrar_compra(self, datos):
        # Envía la petición al servidor para registrar la compra
        respuesta = self.modelo.enviar_peticion(datos)
        print("Respuesta del servidor (compra):", respuesta)
        # Si hay un error o no se recibió una respuesta con el campo esperado (por ejemplo, "mensaje" o "estado")
        if "error" in respuesta or "mensaje" not in respuesta:
            self.agregar_a_cola("registrar_compra", datos)
        return respuesta

    
    def registrar_pago(self, datos):
        try:
            # Se espera que datos["id_compra"] sea un string conteniendo solo el ID (por ejemplo, "3")
            id_compra = int(datos["id_compra"])
            datos["compra_id"] = id_compra  # Asigna el valor convertido
        except Exception as e:
            return {"error": "Formato de ID de compra inválido"}
        
        respuesta = self.modelo.enviar_peticion(datos)
        if "error" in respuesta and "conexión" in respuesta["error"].lower():
            self.agregar_a_cola("registrar_pago", datos)
        return respuesta

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
        # Obtiene los detalles del cliente y los envía a la vista
        detalle = self.modelo.obtener_detalle_cliente(id_cliente, fecha_inicio, fecha_fin)
        if "error" in detalle:
            self.vista.mostrar_mensaje(detalle["error"])
        else:
            self.vista.mostrar_detalle(detalle)
