from Modelo.BaseDeDatos import BaseDeDatos

class Controlador:
    def __init__(self):
        self.db = BaseDeDatos()
    
    def procesar_peticion(self, datos):
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
                        "fecha": c[0], 
                        "monto": c[1], 
                        "descripcion": c[2],
                        "nombre_banco": c[3],
                        "numero_tarjeta": c[4]
                    } 
                    for c in compras]
            }
        
        return {"error": "Acción no reconocida"}