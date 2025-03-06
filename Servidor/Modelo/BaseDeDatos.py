import sqlite3
from datetime import datetime
import math

class BaseDeDatos:
    
    # Constructor de la clase
    def __init__(self, db_nombre=None):
        # Si no se pasa un nombre, usa una ruta absoluta para el archivo
        if db_nombre is None:
            db_nombre = r"C:\Users\Usuario\Desktop\Proyecto Cliente - Servidor\Servidor\banco_universidad.db"

        try:
            self.conexion = sqlite3.connect(db_nombre, check_same_thread=False)
            self.cursor = self.conexion.cursor()
            self.crear_tablas()
            self.verificar_y_precargar_datos()
            print('Conexión exitosa a la base de datos')
        except sqlite3.Error as e:
            print(f'Error en la conexión a la base de datos: {e}')
            
    # Método para Crear tablas
    def crear_tablas(self):
        try:
            # Tabla cliente
            self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cliente(
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cedula TEXT NOT NULL,
                sueldo REAL NOT NULL,
                edad INTEGER NOT NULL
            )
            """
            )
            print('Tabla Cliente creada con éxito')

            # Tabla tarjeta
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tarjeta(
                    id_tarjeta INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_cliente INTEGER NOT NULL,
                    nombre_banco TEXT NOT NULL,
                    numero_tarjeta TEXT NOT NULL,
                    cupo_total REAL NOT NULL,
                    cupo_disponible REAL NOT NULL,
                    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
                )
                """
            )
            print('Tabla Tarjeta creada con éxito')
            

            # Tabla pago
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS pago(
                    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_compra INTEGER,
                    numero_tarjeta TEXT,
                    fecha_pago TEXT,
                    monto_a_pagar REAL,
                    descripcion TEXT,
                    FOREIGN KEY (id_compra) REFERENCES compras(id)
                )
                """
            )
            print('Tabla Pago creada con éxito')

            # Tabla compras
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS compras(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_tarjeta TEXT,
                    fecha TEXT,
                    monto REAL,
                    descripcion TEXT,
                    FOREIGN KEY (numero_tarjeta) REFERENCES tarjeta(numero_tarjeta)
                )
                """
            )
            print('Tabla Compras creada con éxito')

            self.conexion.commit()
        except sqlite3.Error as e:
            print(f'Error en la creación de la tabla: {e}')
            
    # Método para verificar y precargar los datos
    def verificar_y_precargar_datos(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM cliente")
            resultado = self.cursor.fetchone()
            
            if resultado and resultado[0] == 0:
                self.precargar_datos()
        except sqlite3.Error as e:
            print(f'Error al verificar y precargar datos: {e}')
            
    # Método para precargar los datos
    def precargar_datos(self):
        try:
            self.cursor.executescript(
                """
                -- Insertar clientes con los nuevos campos
                INSERT INTO cliente (nombre, cedula, sueldo, edad) VALUES
                ('Juan Pérez', '123456789', 2500000, 30),
                ('María Gómez', '987654321', 3000000, 28),
                ('Carlos Rodríguez', '456789123', 2800000, 35),
                ('Laura Sánchez', '321654987', 3200000, 40),
                ('Andrés Fernández', '654321987', 2700000, 33),
                ('Diana Castro', '789123456', 2900000, 29),
                ('Sergio Ramírez', '159753486', 3100000, 37),
                ('Valentina López', '357159486', 2600000, 31),
                ('Felipe Morales', '852741963', 3300000, 42),
                ('Camila Vargas', '963852741', 2400000, 27);

                -- Insertar tarjetas con bancos colombianos
                INSERT INTO tarjeta (id_cliente, nombre_banco, numero_tarjeta, cupo_total, cupo_disponible) VALUES
                (1, 'BBVA', '1111-2222-3333-4444', 5000000, 5000000),
                (1, 'Davivienda', '5555-6666-7777-8888', 7000000, 7000000),
                (2, 'Banco Bogotá', '2222-3333-4444-5555', 4000000, 4000000),
                (2, 'Bancolombia', '6666-7777-8888-9999', 6000000, 6000000),
                (3, 'Colpatria', '3333-4444-5555-6666', 3000000, 3000000),
                (3, 'Mastercard', '7777-8888-9999-0000', 8000000, 8000000),
                (4, 'Banco de Occidente', '4444-5555-6666-7777', 5000000, 5000000),
                (4, 'BBVA', '8888-9999-0000-1111', 7000000, 7000000),
                (5, 'Davivienda', '5555-6666-7777-8889', 6000000, 6000000),
                (5, 'Banco Bogotá', '9999-0000-1111-2222', 9000000, 9000000),
                (6, 'Bancolombia', '6666-7777-8888-9998', 5000000, 5000000),
                (6, 'Colpatria', '1111-3333-5555-7777', 7000000, 7000000),
                (7, 'Mastercard', '2222-4444-6666-8888', 4000000, 4000000),
                (7, 'Banco de Occidente', '3333-5555-7777-9999', 8000000, 8000000),
                (8, 'BBVA', '4444-6666-8888-0000', 5000000, 5000000),
                (8, 'Davivienda', '5555-7777-9999-1111', 7000000, 7000000),
                (9, 'Banco Bogotá', '6666-8888-0000-2222', 6000000, 6000000),
                (9, 'Bancolombia', '7777-9999-1111-3333', 9000000, 9000000),
                (10, 'Colpatria', '8888-0000-2222-4444', 5000000, 5000000),
                (10, 'Mastercard', '9999-1111-3333-5555', 7000000, 7000000);

                -- Insertar compras por tarjeta (2 compras por cada tarjeta)
                INSERT INTO compras (numero_tarjeta, fecha, monto, descripcion) VALUES
                ('1111-2222-3333-4444', '2025-02-01', 200000, 'Compra en supermercado'),
                ('1111-2222-3333-4444', '2025-02-05', 300000, 'Pago de servicios'),
                ('1111-2222-3333-4444', '2025-02-01', 200000, 'Compra en supermercado'),
                ('1111-2222-3333-4444', '2025-02-05', 300000, 'Pago de servicios'),
                ('1111-2222-3333-4444', '2025-02-10', 150000, 'Compra en farmacia'),
                ('1111-2222-3333-4444', '2025-02-15', 250000, 'Restaurante'),
                ('1111-2222-3333-4444', '2025-02-20', 100000, 'Gasolina'),
                ('1111-2222-3333-4444', '2025-02-25', 400000, 'Compra en línea'),
                ('1111-2222-3333-4444', '2025-03-01', 500000, 'Electrodomésticos'),
                ('1111-2222-3333-4444', '2025-03-05', 200000, 'Pago de internet'),
                ('1111-2222-3333-4444', '2025-03-10', 300000, 'Compra en ferretería'),
                ('1111-2222-3333-4444', '2025-03-15', 150000, 'Cine y entretenimiento'),
                ('1111-2222-3333-4444', '2025-03-20', 600000, 'Compra de tecnología'),
                ('1111-2222-3333-4444', '2025-03-25', 200000, 'Taxi y transporte'),
                ('1111-2222-3333-4444', '2025-03-30', 100000, 'Compra en librería'),
                ('1111-2222-3333-4444', '2025-04-01', 300000, 'Pago de servicios públicos'),
                ('1111-2222-3333-4444', '2025-04-05', 500000, 'Cena en restaurante'),
                ('5555-6666-7777-8888', '2025-02-02', 400000, 'Compra en tienda de ropa'),
                ('5555-6666-7777-8888', '2025-02-06', 500000, 'Restaurante'),
                ('2222-3333-4444-5555', '2025-02-07', 600000, 'Gasolina'),
                ('2222-3333-4444-5555', '2025-02-10', 200000, 'Compra en línea'),
                ('6666-7777-8888-9999', '2025-02-12', 700000, 'Electrodomésticos'),
                ('6666-7777-8888-9999', '2025-02-15', 300000, 'Pago de internet'),
                ('3333-4444-5555-6666', '2025-02-18', 400000, 'Compra en ferretería'),
                ('3333-4444-5555-6666', '2025-02-20', 150000, 'Cine y entretenimiento'),
                ('7777-8888-9999-0000', '2025-02-21', 800000, 'Compra de tecnología'),
                ('7777-8888-9999-0000', '2025-02-23', 200000, 'Taxi y transporte'),
                ('4444-5555-6666-7777', '2025-02-24', 100000, 'Compra en librería'),
                ('4444-5555-6666-7777', '2025-02-26', 300000, 'Pago de servicios públicos'),
                ('8888-9999-0000-1111', '2025-02-27', 500000, 'Cena en restaurante'),
                ('8888-9999-0000-1111', '2025-02-28', 600000, 'Compra de muebles'),
                ('5555-6666-7777-8889', '2025-03-01', 250000, 'Compra en supermercado'),
                ('5555-6666-7777-8889', '2025-03-03', 350000, 'Pago de gimnasio'),
                ('9999-0000-1111-2222', '2025-03-05', 450000, 'Compra de videojuegos'),
                ('9999-0000-1111-2222', '2025-03-07', 200000, 'Taxi y transporte'),
                ('6666-7777-8888-9998', '2025-03-10', 700000, 'Electrodomésticos'),
                ('6666-7777-8888-9998', '2025-03-12', 500000, 'Pago de internet'),
                ('1111-3333-5555-7777', '2025-03-15', 800000, 'Compra en ferretería'),
                ('1111-3333-5555-7777', '2025-03-17', 300000, 'Cine y entretenimiento'),
                ('2222-4444-6666-8888', '2025-03-18', 500000, 'Compra de tecnología'),
                ('2222-4444-6666-8888', '2025-03-20', 200000, 'Taxi y transporte'),
                ('3333-5555-7777-9999', '2025-03-21', 150000, 'Compra en librería'),
                ('3333-5555-7777-9999', '2025-03-23', 300000, 'Pago de servicios públicos'),
                ('4444-6666-8888-0000', '2025-03-25', 600000, 'Cena en restaurante'),
                ('4444-6666-8888-0000', '2025-03-27', 500000, 'Compra de muebles');

                -- 5 Actualizar el cupo disponible de cada tarjeta
                UPDATE tarjeta
                SET cupo_disponible = cupo_total - (
                    SELECT COALESCE(SUM(monto), 0)
                    FROM compras
                    WHERE compras.numero_tarjeta = tarjeta.numero_tarjeta
                );
                """
            )
            self.conexion.commit()
            print("✅ Datos precargados con éxito")
        except sqlite3.Error as e:
            print(f"❌ Error al precargar datos: {e}")

    # Metodo para obtener los detalles de un cliente
    def obtener_detalle_cliente(self, id_cliente, fecha_inicio=None, fecha_fin=None):
            self.cursor.execute("SELECT nombre FROM cliente WHERE id_cliente = ?", (id_cliente,))
            cliente = self.cursor.fetchone()
            
            self.cursor.execute("SELECT nombre_banco, numero_tarjeta, cupo_total, cupo_disponible FROM tarjeta WHERE id_cliente = ?", (id_cliente,))
            tarjetas = self.cursor.fetchall()
            
            query = """
                    SELECT c.fecha, c.monto, c.descripcion, t.nombre_banco, t.numero_tarjeta
                    FROM compras c
                    JOIN tarjeta t ON c.numero_tarjeta = t.numero_tarjeta
                    WHERE t.id_cliente = ?
                    """
            params = [id_cliente]
            
            if fecha_inicio and fecha_fin:
                query += " AND fecha BETWEEN ? AND ?"
                params.extend([fecha_inicio, fecha_fin])
            
            self.cursor.execute(query, tuple(params))
            compras = self.cursor.fetchall()
            
            #print(cliente,tarjetas,compras)
            return cliente, tarjetas, compras
        
    def obtener_detalle_por_tarjeta(self, numero_tarjeta, fecha_inicio=None, fecha_fin=None):
        # Se consulta la tarjeta incluyendo el número de tarjeta
        self.cursor.execute(
            "SELECT id_cliente, nombre_banco, numero_tarjeta, cupo_total, cupo_disponible FROM tarjeta WHERE numero_tarjeta = ?",
            (numero_tarjeta,)
        )
        tarjeta = self.cursor.fetchone()
        if not tarjeta:
            print("Tarjeta no encontrada")
            return None, None, None  # Tarjeta no encontrada

        id_cliente = tarjeta[0]

        # Obtenemos el nombre del cliente
        self.cursor.execute("SELECT nombre FROM cliente WHERE id_cliente = ?", (id_cliente,))
        cliente = self.cursor.fetchone()

        # Consulta de compras filtrada solo por el número de tarjeta (y opcionalmente por fechas)
        query = """
                SELECT c.id, c.fecha, c.monto, c.descripcion, t.nombre_banco, t.numero_tarjeta
                FROM compras c
                JOIN tarjeta t ON c.numero_tarjeta = t.numero_tarjeta
                WHERE c.numero_tarjeta = ?
                """
        params = [numero_tarjeta]
        if fecha_inicio and fecha_fin:
            query += " AND c.fecha BETWEEN ? AND ?"
            params.extend([fecha_inicio, fecha_fin])
        
        self.cursor.execute(query, tuple(params))
        compras = self.cursor.fetchall()
        
        return cliente, [tarjeta], compras

    # Metodo para obtener el cliente por cedula 
    def obtener_cliente_por_cedula(self, cedula):
        try:
            self.cursor.execute("SELECT id_cliente, nombre, sueldo, edad FROM cliente WHERE cedula = ?", (cedula,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error al obtener cliente por cédula: {e}")
            return None
        
    # Metodo para registrar un cliente 
    def registrar_cliente(self, nombre, cedula, sueldo, edad):
        try:
            self.cursor.execute(
                "INSERT INTO cliente (nombre, cedula, sueldo, edad) VALUES (?,?,?,?)",
                (nombre, cedula, sueldo, edad)
            )
            self.conexion.commit()
            return self.cursor.lastrowid  # Retorna el id del cliente creado
        except sqlite3.Error as e:
            print(f"Error al registrar cliente: {e}")
            return None
    
    # Metodo para registrar una TARJETA 
    def registrar_tarjeta(self, id_cliente, nombre_banco, numero_tarjeta, cupo_total):
        try:
            # Inserta la tarjeta y asigna cupo_disponible igual al cupo_total
            self.cursor.execute(
                "INSERT INTO tarjeta (id_cliente, nombre_banco, numero_tarjeta, cupo_total, cupo_disponible) VALUES (?,?,?,?,?)",
                (id_cliente, nombre_banco, numero_tarjeta, cupo_total, cupo_total)
            )
            self.conexion.commit()
            return self.cursor.lastrowid  # Retorna el id de la tarjeta creada
        except sqlite3.Error as e:
            print(f"Error al registrar tarjeta: {e}")
            return None
        
    # Metodo para registrar una compra 
    def registrar_compra(self, numero_tarjeta, fecha, monto, descripcion):
        try:
            # Consultar el cupo disponible de la tarjeta
            self.cursor.execute("SELECT cupo_disponible FROM tarjeta WHERE numero_tarjeta = ?", (numero_tarjeta,))
            resultado = self.cursor.fetchone()
            if not resultado:
                print("Tarjeta no encontrada")
                return {"error": "Tarjeta no encontrada"}
            cupo_disponible = resultado[0]
            
            # Validar que el monto no exceda el cupo disponible
            if monto > cupo_disponible:
                print("El monto supera el cupo disponible")
                return {"error": "La compra no se ha podido realizar, ya que el cupo disponible es menor al monto de la compra"}
            
            # Insertar la compra
            self.cursor.execute(
                "INSERT INTO compras (numero_tarjeta, fecha, monto, descripcion) VALUES (?,?,?,?)",
                (numero_tarjeta, fecha, monto, descripcion)
            )
            compra_id = self.cursor.lastrowid
            
            # Actualizar el cupo_disponible de la tarjeta
            nuevo_cupo = cupo_disponible - monto
            self.cursor.execute(
                "UPDATE tarjeta SET cupo_disponible = ? WHERE numero_tarjeta = ?",
                (nuevo_cupo, numero_tarjeta)
            )
            self.conexion.commit()
            return {"compra_id": compra_id, "nuevo_cupo": nuevo_cupo}
        except sqlite3.Error as e:
            print(f"Error al registrar compra: {e}")
            return {"error": "Error al registrar la compra"}
        
    # Metodo para generar un pago 
    def registrar_pago(self, numero_tarjeta, id_compra, fecha_pago, monto_pagado, descripcion):
        try:
            # Buscar la compra usando el id_compra
            print(f"[DEBUG] Datos recibidos: id_compra={id_compra}, monto={monto_pagado}, fecha={fecha_pago}")  # Depuración
        
            # Validar formato de fecha
            datetime.strptime(fecha_pago, "%Y-%m-%d")
            
            self.cursor.execute("SELECT monto FROM compras WHERE id = ?", (id_compra,))
            compra = self.cursor.fetchone()
            if not compra:
                print(f"❌ Compra con ID {id_compra} no existe")
                return {"error": "Compra no encontrada"}
            compra_monto = compra[0]
            
            if not math.isclose(float(monto_pagado), float(compra_monto), rel_tol=1e-5):
                print("El monto de pago debe ser igual al monto de la compra")
                return {"error": "El monto de pago debe ser igual al monto de la compra"}
            
            # Eliminar la compra (o marcarla como pagada)
            #self.cursor.execute("DELETE FROM compras WHERE id = ?", (id_compra,))
            
            # Actualizar el cupo_disponible: se suma el monto pagado (liberando crédito)
            self.cursor.execute("SELECT cupo_disponible FROM tarjeta WHERE numero_tarjeta = ?", (numero_tarjeta,))
            cupo_actual = self.cursor.fetchone()[0]
            nuevo_cupo = cupo_actual + float(monto_pagado)
            self.cursor.execute("UPDATE tarjeta SET cupo_disponible = ? WHERE numero_tarjeta = ?", (nuevo_cupo, numero_tarjeta))
            
            # Insertar el registro de pago
            self.cursor.execute(
                "INSERT INTO pago (id_compra, numero_tarjeta, fecha_pago, monto_a_pagar, descripcion) VALUES (?,?,?,?,?)",
                (id_compra, numero_tarjeta, fecha_pago, monto_pagado, descripcion)
            )
            self.conexion.commit()
            return {"mensaje": "Pago registrado correctamente", "nuevo_cupo": nuevo_cupo}
        except sqlite3.Error as e:
            print(f"Error al registrar pago: {e}")
            return {"error": f"Error al registrar el pago: {e}"}

    # Metodo para obtener todos los clientes
    def obtener_clientes(self):
        self.cursor.execute("SELECT * FROM cliente")
        return self.cursor.fetchall()
    
