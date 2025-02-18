import sqlite3
from datetime import datetime

class BaseDeDatos:
    
    # Constructor de la clase
    def __init__(self, db_nombre='banco_universidad.db'):
        try: 
            self.conexion = sqlite3.connect(db_nombre, check_same_thread=False)
            self.cursor = self.conexion.cursor()
            self.crear_tablas()
            #self.precargar_datos() Para que no se vuelvan a replicar los datos cada vez que se inicie el servidor se crea el metodo verificar_y_precargar_datos
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
                    nombre TEXT NOT NULL
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
                -- Insertar clientes
                INSERT INTO cliente (nombre) VALUES
                ('Juan Pérez'),
                ('María Gómez'),
                ('Carlos Rodríguez'),
                ('Laura Sánchez'),
                ('Andrés Fernández'),
                ('Diana Castro'),
                ('Sergio Ramírez'),
                ('Valentina López'),
                ('Felipe Morales'),
                ('Camila Vargas');

                -- Insertar tarjetas con bancos colombianos
                INSERT INTO tarjeta (id_cliente, nombre_banco, numero_tarjeta, cupo_total, cupo_disponible) VALUES
                (1, 'BBVA', '1111-2222-3333-4444', 5000, 5000),
                (1, 'Davivienda', '5555-6666-7777-8888', 7000, 7000),
                (2, 'Banco Bogotá', '2222-3333-4444-5555', 4000, 4000),
                (2, 'Bancolombia', '6666-7777-8888-9999', 6000, 6000),
                (3, 'Colpatria', '3333-4444-5555-6666', 3000, 3000),
                (3, 'Mastercard', '7777-8888-9999-0000', 8000, 8000),
                (4, 'Banco de Occidente', '4444-5555-6666-7777', 5000, 5000),
                (4, 'BBVA', '8888-9999-0000-1111', 7000, 7000),
                (5, 'Davivienda', '5555-6666-7777-8889', 6000, 6000),
                (5, 'Banco Bogotá', '9999-0000-1111-2222', 9000, 9000),
                (6, 'Bancolombia', '6666-7777-8888-9998', 5000, 5000),
                (6, 'Colpatria', '1111-3333-5555-7777', 7000, 7000),
                (7, 'Mastercard', '2222-4444-6666-8888', 4000, 4000),
                (7, 'Banco de Occidente', '3333-5555-7777-9999', 8000, 8000),
                (8, 'BBVA', '4444-6666-8888-0000', 5000, 5000),
                (8, 'Davivienda', '5555-7777-9999-1111', 7000, 7000),
                (9, 'Banco Bogotá', '6666-8888-0000-2222', 6000, 6000),
                (9, 'Bancolombia', '7777-9999-1111-3333', 9000, 9000),
                (10, 'Colpatria', '8888-0000-2222-4444', 5000, 5000),
                (10, 'Mastercard', '9999-1111-3333-5555', 7000, 7000);

                -- Insertar compras por tarjeta (2 compras por cada tarjeta)
                INSERT INTO compras (numero_tarjeta, fecha, monto, descripcion) VALUES
                ('1111-2222-3333-4444', '2025-02-01', 200, 'Compra en supermercado'),
                ('1111-2222-3333-4444', '2025-02-05', 300, 'Pago de servicios'),
                ('5555-6666-7777-8888', '2025-02-02', 400, 'Compra en tienda de ropa'),
                ('5555-6666-7777-8888', '2025-02-06', 500, 'Restaurante'),
                ('2222-3333-4444-5555', '2025-02-07', 600, 'Gasolina'),
                ('2222-3333-4444-5555', '2025-02-10', 200, 'Compra en línea'),
                ('6666-7777-8888-9999', '2025-02-12', 700, 'Electrodomésticos'),
                ('6666-7777-8888-9999', '2025-02-15', 300, 'Pago de internet'),
                ('3333-4444-5555-6666', '2025-02-18', 400, 'Compra en ferretería'),
                ('3333-4444-5555-6666', '2025-02-20', 150, 'Cine y entretenimiento'),
                ('7777-8888-9999-0000', '2025-02-21', 800, 'Compra de tecnología'),
                ('7777-8888-9999-0000', '2025-02-23', 200, 'Taxi y transporte'),
                ('4444-5555-6666-7777', '2025-02-24', 100, 'Compra en librería'),
                ('4444-5555-6666-7777', '2025-02-26', 300, 'Pago de servicios públicos'),
                ('8888-9999-0000-1111', '2025-02-27', 500, 'Cena en restaurante'),
                ('8888-9999-0000-1111', '2025-02-28', 600, 'Compra de muebles'),
                ('5555-6666-7777-8889', '2025-03-01', 250, 'Compra en supermercado'),
                ('5555-6666-7777-8889', '2025-03-03', 350, 'Pago de gimnasio'),
                ('9999-0000-1111-2222', '2025-03-05', 450, 'Compra de videojuegos'),
                ('9999-0000-1111-2222', '2025-03-07', 200, 'Taxi y transporte'),
                ('6666-7777-8888-9998', '2025-03-10', 700, 'Electrodomésticos'),
                ('6666-7777-8888-9998', '2025-03-12', 500, 'Pago de internet'),
                ('1111-3333-5555-7777', '2025-03-15', 800, 'Compra en ferretería'),
                ('1111-3333-5555-7777', '2025-03-17', 300, 'Cine y entretenimiento'),
                ('2222-4444-6666-8888', '2025-03-18', 500, 'Compra de tecnología'),
                ('2222-4444-6666-8888', '2025-03-20', 200, 'Taxi y transporte'),
                ('3333-5555-7777-9999', '2025-03-21', 150, 'Compra en librería'),
                ('3333-5555-7777-9999', '2025-03-23', 300, 'Pago de servicios públicos'),
                ('4444-6666-8888-0000', '2025-03-25', 600, 'Cena en restaurante'),
                ('4444-6666-8888-0000', '2025-03-27', 500, 'Compra de muebles');

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
            
            self.cursor.execute("SELECT nombre_banco, numero_tarjeta, cupo_total FROM tarjeta WHERE id_cliente = ?", (id_cliente,))
            tarjetas = self.cursor.fetchall()
            
            query = "SELECT fecha, monto, descripcion FROM compras WHERE numero_tarjeta IN (SELECT numero_tarjeta FROM tarjeta WHERE id_cliente = ?)"
            params = [id_cliente]
            
            if fecha_inicio and fecha_fin:
                query += " AND fecha BETWEEN ? AND ?"
                params.extend([fecha_inicio, fecha_fin])
            
            self.cursor.execute(query, tuple(params))
            compras = self.cursor.fetchall()
            
            #print(cliente,tarjetas,compras)
            return cliente, tarjetas, compras
    
    # Metodo para obtener todos los clientes
    def obtener_clientes(self):
        self.cursor.execute("SELECT * FROM cliente")
        return self.cursor.fetchall()
    






