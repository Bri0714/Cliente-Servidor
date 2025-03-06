from Modelo.BaseDeDatos import BaseDeDatos
from threading import Lock

class Controlador:
    def __init__(self):
        self.db = BaseDeDatos()
        self.bloqueo = Lock()
        self.tarjetas_bloqueadas = {}  # Diccionario para bloquear tarjetas
    
    def procesar_peticion(self, datos):
        
        if datos["accion"] == "ping":
            return {"mensaje": "conexion exitosa"}
        
        if datos["accion"] == "listar_clientes":
            clientes = self.db.obtener_clientes()
            return {"clientes": [{"id": c[0], "nombre": c[1]} for c in clientes]}
        
        elif datos["accion"] == "detalle_cliente":
            id_cliente = datos.get("id_cliente")
            fecha_inicio = datos.get("fecha_inicio")
            fecha_fin = datos.get("fecha_fin")
            
            cliente, tarjetas, compras = self.db.obtener_detalle_cliente(id_cliente, fecha_inicio, fecha_fin)
            if not cliente:
                return {"error": "Cliente no encontrado"}
            
            return {
                "nombre": cliente[0],
                "num_compras": len(compras),
                "tarjetas": [
                    {
                        "nombre_banco": t[0], 
                        "numero_tarjeta": t[1],
                        "cupo_total": t[2],
                        "cupo_disponible": t[3]
                    } 
                    for t in tarjetas],
                "compras": [
                    {
                        "id": c[0],
                        "fecha": c[1], 
                        "monto": c[2], 
                        "descripcion": c[3],
                        "nombre_banco": c[4],
                        "numero_tarjeta": c[5]
                    } 
                    for c in compras]
            }
        
        # Nueva acción para obtener el detalle de una tarjeta
        elif datos["accion"] == "detalle_tarjeta":
            numero_tarjeta = datos.get("numero_tarjeta")
            
            with self.bloqueo:
                if numero_tarjeta in self.tarjetas_bloqueadas:
                    print(f"El número de tarjeta {numero_tarjeta} ya está siendo consultado. Intente con otro.")
                    return {"error": f"El número de tarjeta {numero_tarjeta} ya está siendo consultado. Intente con otro."}
                self.tarjetas_bloqueadas[numero_tarjeta] = True 
                
            fecha_inicio = datos.get("fecha_inicio")
            fecha_fin = datos.get("fecha_fin")
            
            cliente, tarjetas, compras = self.db.obtener_detalle_por_tarjeta(numero_tarjeta, fecha_inicio, fecha_fin)
            if not cliente:
                return {"error": "Tarjeta no encontrada"}
            
            return {
                "nombre": cliente[0],
                "num_compras": len(compras),
                "tarjetas": [
                    {
                        "nombre_banco": t[1], 
                        "numero_tarjeta": t[2],
                        "cupo_total": t[3],
                        "cupo_disponible": t[4]
                    } 
                    for t in tarjetas
                ],
                "compras": [
                    {
                        "id": c[0],  # <- ¡Corregido! Incluye el id de la compra
                        "fecha": c[1], 
                        "monto": c[2], 
                        "descripcion": c[3],
                        "nombre_banco": c[4],
                        "numero_tarjeta": c[5]
                    } 
                    for c in compras
                ]
            }
        
        # Nueva acción para liberar tarjeta
        elif datos["accion"] == "liberar_tarjeta":
            numero_tarjeta = datos["numero_tarjeta"]
            with self.bloqueo:
                # Verificar existencia antes de eliminar
                if numero_tarjeta in self.tarjetas_bloqueadas:
                    del self.tarjetas_bloqueadas[numero_tarjeta]
                    print(f"✅ Tarjeta {numero_tarjeta} liberada")
                else:
                    print(f"⚠️ Tarjeta {numero_tarjeta} no estaba bloqueada")
            return {"mensaje": "Operación completada"}

        # Nueva acción para registrar una tarjeta
        elif datos["accion"] == "registrar_tarjeta":
            # Se asume que el cliente ya está registrado y se envía su id en id_cliente
            id_cliente = datos.get("id_cliente")
            if not id_cliente:
                return {"error": "No se ha obtenido el cliente. Registre el cliente primero."}
            
            # Datos de la tarjeta
            nombre_banco = datos.get("nombre_banco")
            numero_tarjeta = datos.get("numero_tarjeta")
            cupo_total = datos.get("cupo_total")
            if not (nombre_banco and numero_tarjeta and cupo_total):
                return {"error": "Faltan datos para registrar la tarjeta"}
            
            res = self.db.registrar_tarjeta(id_cliente, nombre_banco, numero_tarjeta, cupo_total)
            if res:
                return {"mensaje": "Tarjeta creada correctamente"}
            else:
                return {"error": "Error al registrar la tarjeta"}

        
        # acción para buscar un cliente por cedula 
        elif datos["accion"] == "buscar_cliente_por_cedula":
            cedula = datos.get("cedula")
            cliente = self.db.obtener_cliente_por_cedula(cedula)
            if not cliente:
                return {"error": f"Cliente con cédula {cedula} no ha sido encontrado"}
            else:
                return {"id_cliente": cliente[0], "nombre": cliente[1], "sueldo": cliente[2], "edad": cliente[3]}
            
        # acción para registrar un cliente nuevo
        elif datos["accion"] == "registrar_cliente_nuevo":
            nombre = datos.get("nombre")
            cedula = datos.get("cedula")
            sueldo = datos.get("sueldo")
            edad = datos.get("edad")
            if not (nombre and cedula and sueldo and edad):
                return {"error": "Faltan datos para registrar el cliente"}
            id_cliente = self.db.registrar_cliente(nombre, cedula, sueldo, edad)
            if not id_cliente:
                return {"error": "Error al registrar el cliente"}
            return {"id_cliente": id_cliente, "nombre": nombre, "sueldo": float(sueldo), "edad": edad, "mensaje": "Cliente creado correctamente"}
        
        # acción para registrar una compra
        elif datos["accion"] == "registrar_compra":
            numero_tarjeta = datos.get("numero_tarjeta")
            fecha = datos.get("fecha")
            monto = datos.get("monto")
            descripcion = datos.get("descripcion")
            if not (numero_tarjeta and fecha and monto and descripcion):
                return {"error": "Faltan datos para registrar la compra"}
            
            resultado = self.db.registrar_compra(numero_tarjeta, fecha, monto, descripcion)
            if "error" in resultado:
                return resultado  # Retorna el mensaje de error
            else:
                return {"mensaje": "La compra ha sido registrada satisfactoriamente", "nuevo_cupo": resultado["nuevo_cupo"]}
            
        # accion generar pago 
        elif datos["accion"] == "registrar_pago":
            numero_tarjeta = datos.get("numero_tarjeta")
            id_compra = datos.get("id_compra")
            fecha_pago = datos.get("fecha_pago")
            monto_pagado = datos.get("monto_pagado")
            descripcion = datos.get("descripcion")
            if not (numero_tarjeta and fecha_pago and monto_pagado and descripcion):
                print("Faltan datos para registrar el pago")
                return {"error": "Faltan datos para registrar el pago"}
            
            resultado = self.db.registrar_pago(numero_tarjeta,id_compra, fecha_pago, monto_pagado, descripcion)
            return resultado



