import sys
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from PIL import Image, ImageDraw
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QMessageBox, QFileDialog,
                             QDialog, QFormLayout, QListWidget, QListWidgetItem, QTextEdit, QGroupBox,
                             QGridLayout, QHeaderView, QCheckBox, QCalendarWidget, QScrollArea, QDateTimeEdit)
from PyQt6.QtCore import Qt, QDate, QDateTime, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QColor, QPixmap
from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt6.QtCore import QTimer

class Database:
    def __init__(self):
        self.db_path = Path('datos_yc_hielo.db')
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de configuración
        cursor.execute('''CREATE TABLE IF NOT EXISTS configuracion (
            id INTEGER PRIMARY KEY,
            nombre_empresa TEXT,
            ciudad TEXT,
            precio_agua REAL,
            precio_luz REAL,
            precio_bolsa_3kg REAL,
            precio_bolsa_5kg REAL,
            precio_bolsa_10kg REAL,
            precio_bolsa_15kg REAL,
            margen_ganancia_minorista REAL,
            margen_ganancia_mayorista REAL,
            costo_folleto REAL,
            costo_otros REAL,
            logo_path TEXT,
            fecha_actualizacion TEXT
        )''')
        
        # Tabla de clientes
        cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            telefono TEXT,
            email TEXT,
            tipo TEXT,
            saldo REAL,
            fecha_registro TEXT
        )''')
        
        # Tabla de ventas
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            fecha TEXT,
            bolsas_3kg INTEGER,
            bolsas_5kg INTEGER,
            bolsas_10kg INTEGER,
            bolsas_15kg INTEGER,
            total REAL,
            tipo_venta TEXT,
            numero_boleta TEXT,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )''')
        
        # Tabla de gastos
        cursor.execute('''CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            descripcion TEXT,
            monto REAL,
            fecha TEXT
        )''')
        
        # Tabla de producción
        cursor.execute('''CREATE TABLE IF NOT EXISTS produccion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            bolsas_3kg INTEGER,
            bolsas_5kg INTEGER,
            bolsas_10kg INTEGER,
            bolsas_15kg INTEGER,
            total_producido REAL
        )''')
        
        # Tabla de pedidos
        cursor.execute('''CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            fecha_pedido TEXT,
            fecha_entrega TEXT,
            bolsas_3kg INTEGER,
            bolsas_5kg INTEGER,
            bolsas_10kg INTEGER,
            bolsas_15kg INTEGER,
            estado TEXT,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )''')
        
        # Tabla de cuenta corriente
        cursor.execute('''CREATE TABLE IF NOT EXISTS cuenta_corriente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            tipo_movimiento TEXT,
            monto REAL,
            fecha TEXT,
            concepto TEXT,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )''')
        
        conn.commit()
        conn.close()
        
        # Insertar configuración por defecto si no existe
        if not self.get_configuracion():
            self.guardar_configuracion({
                'nombre_empresa': 'YC HIELO',
                'ciudad': 'Rosario',
                'precio_agua': 50.0,
                'precio_luz': 100.0,
                'precio_bolsa_3kg': 15.0,
                'precio_bolsa_5kg': 20.0,
                'precio_bolsa_10kg': 35.0,
                'precio_bolsa_15kg': 50.0,
                'margen_ganancia_minorista': 30.0,
                'margen_ganancia_mayorista': 20.0,
                'costo_folleto': 10.0,
                'costo_otros': 0.0,
                'logo_path': ''
            })
    
    def guardar_configuracion(self, config):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        config['fecha_actualizacion'] = datetime.now().isoformat()
        
        cursor.execute('DELETE FROM configuracion')
        cursor.execute('''INSERT INTO configuracion (nombre_empresa, ciudad, precio_agua, precio_luz,
                          precio_bolsa_3kg, precio_bolsa_5kg, precio_bolsa_10kg, precio_bolsa_15kg,
                          margen_ganancia_minorista, margen_ganancia_mayorista, costo_folleto,
                          costo_otros, logo_path, fecha_actualizacion) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (config.get('nombre_empresa', 'YC HIELO'),
                        config.get('ciudad', 'Rosario'),
                        config.get('precio_agua', 50.0),
                        config.get('precio_luz', 100.0),
                        config.get('precio_bolsa_3kg', 15.0),
                        config.get('precio_bolsa_5kg', 20.0),
                        config.get('precio_bolsa_10kg', 35.0),
                        config.get('precio_bolsa_15kg', 50.0),
                        config.get('margen_ganancia_minorista', 30.0),
                        config.get('margen_ganancia_mayorista', 20.0),
                        config.get('costo_folleto', 10.0),
                        config.get('costo_otros', 0.0),
                        config.get('logo_path', ''),
                        config['fecha_actualizacion']))
        conn.commit()
        conn.close()
    
    def get_configuracion(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM configuracion')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'nombre_empresa': row[1],
                'ciudad': row[2],
                'precio_agua': row[3],
                'precio_luz': row[4],
                'precio_bolsa_3kg': row[5],
                'precio_bolsa_5kg': row[6],
                'precio_bolsa_10kg': row[7],
                'precio_bolsa_15kg': row[8],
                'margen_ganancia_minorista': row[9],
                'margen_ganancia_mayorista': row[10],
                'costo_folleto': row[11],
                'costo_otros': row[12],
                'logo_path': row[13]
            }
        return None
    
    def agregar_cliente(self, nombre, telefono, email, tipo):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO clientes (nombre, telefono, email, tipo, saldo, fecha_registro)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                       (nombre, telefono, email, tipo, 0, datetime.now().isoformat()))
        conn.commit()
        cliente_id = cursor.lastrowid
        conn.close()
        return cliente_id
    
    def actualizar_cliente(self, cliente_id, nombre, telefono, email, tipo):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''UPDATE clientes SET nombre=?, telefono=?, email=?, tipo=? WHERE id=?''',
                       (nombre, telefono, email, tipo, cliente_id))
        conn.commit()
        conn.close()
    
    def eliminar_cliente(self, cliente_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM clientes WHERE id=?', (cliente_id,))
        conn.commit()
        conn.close()
    
    def obtener_clientes(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clientes')
        clientes = cursor.fetchall()
        conn.close()
        return clientes
    
    def obtener_cliente(self, cliente_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clientes WHERE id=?', (cliente_id,))
        cliente = cursor.fetchone()
        conn.close()
        return cliente
    
    def registrar_venta(self, cliente_id, bolsas_3kg, bolsas_5kg, bolsas_10kg, bolsas_15kg, total, tipo_venta):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        numero_boleta = f"BOL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor.execute('''INSERT INTO ventas (cliente_id, fecha, bolsas_3kg, bolsas_5kg, bolsas_10kg, 
                         bolsas_15kg, total, tipo_venta, numero_boleta)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (cliente_id, datetime.now().isoformat(), bolsas_3kg, bolsas_5kg, 
                        bolsas_10kg, bolsas_15kg, total, tipo_venta, numero_boleta))
        
        conn.commit()
        venta_id = cursor.lastrowid
        conn.close()
        
        return numero_boleta, venta_id
    
    def actualizar_venta(self, venta_id, cliente_id, bolsas_3kg, bolsas_5kg, bolsas_10kg, bolsas_15kg, total, tipo_venta):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''UPDATE ventas SET cliente_id=?, bolsas_3kg=?, bolsas_5kg=?, 
                         bolsas_10kg=?, bolsas_15kg=?, total=?, tipo_venta=? WHERE id=?''',
                       (cliente_id, bolsas_3kg, bolsas_5kg, bolsas_10kg, bolsas_15kg, total, tipo_venta, venta_id))
        conn.commit()
        conn.close()
    
    def eliminar_venta(self, venta_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM ventas WHERE id=?', (venta_id,))
        conn.commit()
        conn.close()
    
    def obtener_ventas(self, fecha_inicio=None, fecha_fin=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if fecha_inicio and fecha_fin:
            cursor.execute('''SELECT v.*, c.nombre FROM ventas v 
                             JOIN clientes c ON v.cliente_id = c.id
                             WHERE DATE(v.fecha) BETWEEN ? AND ?
                             ORDER BY v.fecha DESC''',
                           (fecha_inicio, fecha_fin))
        else:
            cursor.execute('''SELECT v.*, c.nombre FROM ventas v 
                             JOIN clientes c ON v.cliente_id = c.id
                             ORDER BY v.fecha DESC''')
        
        ventas = cursor.fetchall()
        conn.close()
        return ventas
    
    def registrar_gasto(self, tipo, descripcion, monto):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO gastos (tipo, descripcion, monto, fecha)
                         VALUES (?, ?, ?, ?)''',
                       (tipo, descripcion, monto, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def actualizar_gasto(self, gasto_id, tipo, descripcion, monto):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''UPDATE gastos SET tipo=?, descripcion=?, monto=? WHERE id=?''',
                       (tipo, descripcion, monto, gasto_id))
        conn.commit()
        conn.close()
    
    def eliminar_gasto(self, gasto_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM gastos WHERE id=?', (gasto_id,))
        conn.commit()
        conn.close()
    
    def obtener_gastos(self, fecha_inicio=None, fecha_fin=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if fecha_inicio and fecha_fin:
            cursor.execute('''SELECT * FROM gastos 
                             WHERE DATE(fecha) BETWEEN ? AND ?
                             ORDER BY fecha DESC''',
                           (fecha_inicio, fecha_fin))
        else:
            cursor.execute('SELECT * FROM gastos ORDER BY fecha DESC')
        
        gastos = cursor.fetchall()
        conn.close()
        return gastos
    
    def registrar_produccion(self, bolsas_3kg, bolsas_5kg, bolsas_10kg, bolsas_15kg, total):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO produccion (fecha, bolsas_3kg, bolsas_5kg, bolsas_10kg, 
                         bolsas_15kg, total_producido)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                       (datetime.now().isoformat(), bolsas_3kg, bolsas_5kg, 
                        bolsas_10kg, bolsas_15kg, total))
        conn.commit()
        conn.close()
    
    def actualizar_produccion(self, produccion_id, bolsas_3kg, bolsas_5kg, bolsas_10kg, bolsas_15kg, total):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''UPDATE produccion SET bolsas_3kg=?, bolsas_5kg=?, bolsas_10kg=?, 
                         bolsas_15kg=?, total_producido=? WHERE id=?''',
                       (bolsas_3kg, bolsas_5kg, bolsas_10kg, bolsas_15kg, total, produccion_id))
        conn.commit()
        conn.close()
    
    def eliminar_produccion(self, produccion_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produccion WHERE id=?', (produccion_id,))
        conn.commit()
        conn.close()
    
    def obtener_produccion(self, fecha_inicio=None, fecha_fin=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if fecha_inicio and fecha_fin:
            cursor.execute('''SELECT * FROM produccion 
                             WHERE DATE(fecha) BETWEEN ? AND ?
                             ORDER BY fecha DESC''',
                           (fecha_inicio, fecha_fin))
        else:
            cursor.execute('SELECT * FROM produccion ORDER BY fecha DESC')
        
        produccion = cursor.fetchall()
        conn.close()
        return produccion
    
    def agregar_pedido(self, cliente_id, fecha_entrega, bolsas_3kg, bolsas_5kg, bolsas_10kg, bolsas_15kg):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO pedidos (cliente_id, fecha_pedido, fecha_entrega, bolsas_3kg,
                         bolsas_5kg, bolsas_10kg, bolsas_15kg, estado)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (cliente_id, datetime.now().isoformat(), fecha_entrega, bolsas_3kg,
                        bolsas_5kg, bolsas_10kg, bolsas_15kg, 'Pendiente'))
        conn.commit()
        pedido_id = cursor.lastrowid
        conn.close()
        return pedido_id
    
    def actualizar_pedido(self, pedido_id, cliente_id, fecha_entrega, bolsas_3kg, bolsas_5kg, bolsas_10kg, bolsas_15kg, estado):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''UPDATE pedidos SET cliente_id=?, fecha_entrega=?, bolsas_3kg=?, 
                         bolsas_5kg=?, bolsas_10kg=?, bolsas_15kg=?, estado=? WHERE id=?''',
                       (cliente_id, fecha_entrega, bolsas_3kg, bolsas_5kg, bolsas_10kg, bolsas_15kg, estado, pedido_id))
        conn.commit()
        conn.close()
    
    def eliminar_pedido(self, pedido_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM pedidos WHERE id=?', (pedido_id,))
        conn.commit()
        conn.close()
    
    def obtener_pedidos(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT p.*, c.nombre FROM pedidos p 
                         JOIN clientes c ON p.cliente_id = c.id
                         ORDER BY p.fecha_entrega''')
        pedidos = cursor.fetchall()
        conn.close()
        return pedidos
    
    def obtener_pedido(self, pedido_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT p.*, c.nombre FROM pedidos p 
                         JOIN clientes c ON p.cliente_id = c.id
                         WHERE p.id=?''', (pedido_id,))
        pedido = cursor.fetchone()
        conn.close()
        return pedido
    
    def registrar_cuenta_corriente(self, cliente_id, tipo_movimiento, monto, concepto):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO cuenta_corriente (cliente_id, tipo_movimiento, monto, fecha, concepto)
                         VALUES (?, ?, ?, ?, ?)''',
                       (cliente_id, tipo_movimiento, monto, datetime.now().isoformat(), concepto))
        conn.commit()
        conn.close()
    
    def obtener_cuenta_corriente(self, cliente_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM cuenta_corriente WHERE cliente_id = ? ORDER BY fecha DESC''',
                       (cliente_id,))
        movimientos = cursor.fetchall()
        conn.close()
        return movimientos

class CostoCalculador:
    """Calcula automáticamente costos basados en la configuración"""
    
    def __init__(self, config):
        self.config = config
    
    def calcular_precio_venta(self, presentacion, tipo_venta='Minorista'):
        """Calcula precio de venta automáticamente"""
        precio_base_map = {
            '3kg': self.config['precio_bolsa_3kg'],
            '5kg': self.config['precio_bolsa_5kg'],
            '10kg': self.config['precio_bolsa_10kg'],
            '15kg': self.config['precio_bolsa_15kg']
        }
        
        precio_base = precio_base_map.get(presentacion, 0)
        margen = self.config['margen_ganancia_minorista'] if tipo_venta == 'Minorista' else self.config['margen_ganancia_mayorista']
        
        precio_venta = precio_base * (1 + margen / 100)
        return precio_venta
    
    def calcular_ganancia_unitaria(self, presentacion, tipo_venta='Minorista'):
        """Calcula ganancia unitaria por bolsa"""
        precio_base_map = {
            '3kg': self.config['precio_bolsa_3kg'],
            '5kg': self.config['precio_bolsa_5kg'],
            '10kg': self.config['precio_bolsa_10kg'],
            '15kg': self.config['precio_bolsa_15kg']
        }
        
        precio_base = precio_base_map.get(presentacion, 0)
        margen = self.config['margen_ganancia_minorista'] if tipo_venta == 'Minorista' else self.config['margen_ganancia_mayorista']
        
        ganancia = precio_base * (margen / 100)
        return ganancia
    
    def calcular_total_venta(self, bolsas_3kg, bolsas_5kg, bolsas_10kg, bolsas_15kg, tipo_venta='Minorista'):
        """Calcula total de venta automáticamente"""
        total = (
            bolsas_3kg * self.calcular_precio_venta('3kg', tipo_venta) +
            bolsas_5kg * self.calcular_precio_venta('5kg', tipo_venta) +
            bolsas_10kg * self.calcular_precio_venta('10kg', tipo_venta) +
            bolsas_15kg * self.calcular_precio_venta('15kg', tipo_venta)
        )
        return total

class GeneradorPreciosDialog(QDialog):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.config = db.get_configuracion()
        self.calculador = CostoCalculador(self.config)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Generador de Precios Sugeridos")
        self.setGeometry(100, 100, 900, 600)
        
        layout = QVBoxLayout()
        
        # Costos unitarios
        form_layout = QFormLayout()
        
        self.costo_3kg = QDoubleSpinBox()
        self.costo_3kg.setValue(self.config['precio_bolsa_3kg'])
        self.costo_3kg.setMaximum(1000)
        self.costo_3kg.valueChanged.connect(self.calcular_precios)
        form_layout.addRow("Costo Bolsa 3kg ($):", self.costo_3kg)
        
        self.costo_5kg = QDoubleSpinBox()
        self.costo_5kg.setValue(self.config['precio_bolsa_5kg'])
        self.costo_5kg.setMaximum(1000)
        self.costo_5kg.valueChanged.connect(self.calcular_precios)
        form_layout.addRow("Costo Bolsa 5kg ($):", self.costo_5kg)
        
        self.costo_10kg = QDoubleSpinBox()
        self.costo_10kg.setValue(self.config['precio_bolsa_10kg'])
        self.costo_10kg.setMaximum(1000)
        self.costo_10kg.valueChanged.connect(self.calcular_precios)
        form_layout.addRow("Costo Bolsa 10kg ($):", self.costo_10kg)
        
        self.costo_15kg = QDoubleSpinBox()
        self.costo_15kg.setValue(self.config['precio_bolsa_15kg'])
        self.costo_15kg.setMaximum(1000)
        self.costo_15kg.valueChanged.connect(self.calcular_precios)
        form_layout.addRow("Costo Bolsa 15kg ($):", self.costo_15kg)
        
        # Márgenes de ganancia
        self.margen_minorista = QDoubleSpinBox()
        self.margen_minorista.setValue(self.config['margen_ganancia_minorista'])
        self.margen_minorista.setMaximum(100)
        self.margen_minorista.valueChanged.connect(self.calcular_precios)
        form_layout.addRow("Margen Minorista (%):", self.margen_minorista)
        
        self.margen_mayorista = QDoubleSpinBox()
        self.margen_mayorista.setValue(self.config['margen_ganancia_mayorista'])
        self.margen_mayorista.setMaximum(100)
        self.margen_mayorista.valueChanged.connect(self.calcular_precios)
        form_layout.addRow("Margen Mayorista (%):", self.margen_mayorista)
        
        layout.addLayout(form_layout)
        
        # Tabla de resultados
        self.tabla_precios = QTableWidget()
        self.tabla_precios.setColumnCount(5)
        self.tabla_precios.setHorizontalHeaderLabels(["Presentación", "Costo", "Precio Minorista", "Precio Mayorista", "Ganancia Min."])
        self.tabla_precios.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_precios)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_calcular = QPushButton("Calcular Precios")
        btn_calcular.clicked.connect(self.calcular_precios)
        btn_layout.addWidget(btn_calcular)
        
        btn_guardar = QPushButton("Guardar Precios")
        btn_guardar.clicked.connect(self.guardar_precios)
        btn_layout.addWidget(btn_guardar)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Calcular al abrir
        self.calcular_precios()
    
    def calcular_precios(self):
        self.tabla_precios.setRowCount(4)
        
        datos = [
            ("3 kg", self.costo_3kg.value()),
            ("5 kg", self.costo_5kg.value()),
            ("10 kg", self.costo_10kg.value()),
            ("15 kg", self.costo_15kg.value())
        ]
        
        for i, (presentacion, costo) in enumerate(datos):
            precio_minorista = costo * (1 + self.margen_minorista.value() / 100)
            precio_mayorista = costo * (1 + self.margen_mayorista.value() / 100)
            ganancia_minorista = precio_minorista - costo
            
            self.tabla_precios.setItem(i, 0, QTableWidgetItem(presentacion))
            self.tabla_precios.setItem(i, 1, QTableWidgetItem(f"${costo:.2f}"))
            self.tabla_precios.setItem(i, 2, QTableWidgetItem(f"${precio_minorista:.2f}"))
            self.tabla_precios.setItem(i, 3, QTableWidgetItem(f"${precio_mayorista:.2f}"))
            self.tabla_precios.setItem(i, 4, QTableWidgetItem(f"${ganancia_minorista:.2f}"))
    
    def guardar_precios(self):
        self.config['precio_bolsa_3kg'] = self.costo_3kg.value()
        self.config['precio_bolsa_5kg'] = self.costo_5kg.value()
        self.config['precio_bolsa_10kg'] = self.costo_10kg.value()
        self.config['precio_bolsa_15kg'] = self.costo_15kg.value()
        self.config['margen_ganancia_minorista'] = self.margen_minorista.value()
        self.config['margen_ganancia_mayorista'] = self.margen_mayorista.value()
        
        self.db.guardar_configuracion(self.config)
        QMessageBox.information(self, "Éxito", "Precios guardados correctamente")

class GeneradorBoleta(QDialog):
    def __init__(self, parent, db, venta_id, numero_boleta):
        super().__init__(parent)
        self.db = db
        self.venta_id = venta_id
        self.numero_boleta = numero_boleta
        self.config = db.get_configuracion()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Boleta {self.numero_boleta}")
        self.setGeometry(100, 100, 600, 700)
        
        layout = QVBoxLayout()
        
        # Información de la boleta
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        
        html = f"""
        <h2 style='text-align: center;'>{self.config['nombre_empresa']}</h2>
        <p style='text-align: center;'>{self.config['ciudad']} - Pesos Argentinos</p>
        <hr>
        <p><b>Número de Boleta:</b> {self.numero_boleta}</p>
        <p><b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        <hr>
        <p>Gracias por su compra</p>
        """
        
        info_text.setHtml(html)
        layout.addWidget(info_text)
        
        # Botones
        btn_layout = QHBoxLayout()
        
        btn_pdf = QPushButton("Generar PDF")
        btn_pdf.clicked.connect(self.generar_pdf)
        btn_layout.addWidget(btn_pdf)
        
        btn_qr = QPushButton("Generar QR")
        btn_qr.clicked.connect(self.generar_qr)
        btn_layout.addWidget(btn_qr)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        btn_layout.addWidget(btn_cerrar)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def generar_pdf(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar Boleta", f"boleta_{self.numero_boleta}.pdf", "PDF Files (*.pdf)")
        
        if filename:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=14,
                textColor=colors.HexColor('#1f77b4'),
                spaceAfter=30,
                alignment=1
            )
            
            elements.append(Paragraph(self.config['nombre_empresa'], title_style))
            elements.append(Paragraph(f"{self.config['ciudad']} - Pesos Argentinos", styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            elements.append(Paragraph(f"<b>Boleta Nº:</b> {self.numero_boleta}", styles['Normal']))
            elements.append(Paragraph(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            elements.append(Paragraph("Gracias por su compra", styles['Normal']))
            
            doc.build(elements)
            QMessageBox.information(self, "Éxito", f"PDF guardado en {filename}")
    
    def generar_qr(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar QR", f"qr_{self.numero_boleta}.png", "PNG Files (*.png)")
        
        if filename:
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(f"Boleta {self.numero_boleta} - {datetime.now().strftime('%d/%m/%Y')}")
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(filename)
            QMessageBox.information(self, "Éxito", f"QR guardado en {filename}")

class ConfiguracionDialog(QDialog):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.config = db.get_configuracion()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Configuración")
        self.setGeometry(100, 100, 700, 800)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Información de la empresa
        self.nombre_empresa = QLineEdit()
        self.nombre_empresa.setText(self.config['nombre_empresa'])
        layout.addRow("Nombre Empresa:", self.nombre_empresa)
        
        self.ciudad = QLineEdit()
        self.ciudad.setText(self.config['ciudad'])
        layout.addRow("Ciudad:", self.ciudad)
        
        # Costos operativos
        group_costos = QGroupBox("Costos Operativos")
        costos_layout = QFormLayout()
        
        self.precio_agua = QDoubleSpinBox()
        self.precio_agua.setValue(self.config['precio_agua'])
        self.precio_agua.setMaximum(10000)
        costos_layout.addRow("Costo Agua ($):", self.precio_agua)
        
        self.precio_luz = QDoubleSpinBox()
        self.precio_luz.setValue(self.config['precio_luz'])
        self.precio_luz.setMaximum(10000)
        costos_layout.addRow("Costo Luz ($):", self.precio_luz)
        
        self.costo_folleto = QDoubleSpinBox()
        self.costo_folleto.setValue(self.config['costo_folleto'])
        self.costo_folleto.setMaximum(10000)
        costos_layout.addRow("Costo Folleto ($):", self.costo_folleto)
        
        self.costo_otros = QDoubleSpinBox()
        self.costo_otros.setValue(self.config['costo_otros'])
        self.costo_otros.setMaximum(10000)
        costos_layout.addRow("Otros Costos ($):", self.costo_otros)
        
        group_costos.setLayout(costos_layout)
        layout.addRow(group_costos)
        
        # Costos de bolsas
        group_bolsas = QGroupBox("Costos de Bolsas")
        bolsas_layout = QFormLayout()
        
        self.costo_bolsa_3kg = QDoubleSpinBox()
        self.costo_bolsa_3kg.setValue(self.config['precio_bolsa_3kg'])
        self.costo_bolsa_3kg.setMaximum(1000)
        bolsas_layout.addRow("Costo Bolsa 3kg ($):", self.costo_bolsa_3kg)
        
        self.costo_bolsa_5kg = QDoubleSpinBox()
        self.costo_bolsa_5kg.setValue(self.config['precio_bolsa_5kg'])
        self.costo_bolsa_5kg.setMaximum(1000)
        bolsas_layout.addRow("Costo Bolsa 5kg ($):", self.costo_bolsa_5kg)
        
        self.costo_bolsa_10kg = QDoubleSpinBox()
        self.costo_bolsa_10kg.setValue(self.config['precio_bolsa_10kg'])
        self.costo_bolsa_10kg.setMaximum(1000)
        bolsas_layout.addRow("Costo Bolsa 10kg ($):", self.costo_bolsa_10kg)
        
        self.costo_bolsa_15kg = QDoubleSpinBox()
        self.costo_bolsa_15kg.setValue(self.config['precio_bolsa_15kg'])
        self.costo_bolsa_15kg.setMaximum(1000)
        bolsas_layout.addRow("Costo Bolsa 15kg ($):", self.costo_bolsa_15kg)
        
        group_bolsas.setLayout(bolsas_layout)
        layout.addRow(group_bolsas)
        
        # Márgenes
        group_margenes = QGroupBox("Márgenes de Ganancia")
        margenes_layout = QFormLayout()
        
        self.margen_minorista = QDoubleSpinBox()
        self.margen_minorista.setValue(self.config['margen_ganancia_minorista'])
        self.margen_minorista.setMaximum(100)
        margenes_layout.addRow("Margen Minorista (%):", self.margen_minorista)
        
        self.margen_mayorista = QDoubleSpinBox()
        self.margen_mayorista.setValue(self.config['margen_ganancia_mayorista'])
        self.margen_mayorista.setMaximum(100)
        margenes_layout.addRow("Margen Mayorista (%):", self.margen_mayorista)
        
        group_margenes.setLayout(margenes_layout)
        layout.addRow(group_margenes)
        
        # Logo
        self.logo_path = QLineEdit()
        self.logo_path.setText(self.config['logo_path'])
        self.logo_path.setReadOnly(True)
        layout.addRow("Logo Path:", self.logo_path)
        
        btn_logo = QPushButton("Seleccionar Logo")
        btn_logo.clicked.connect(self.seleccionar_logo)
        layout.addRow("", btn_logo)
        
        scroll.setWidget(widget)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        
        # Botones
        btn_layout = QHBoxLayout()
        
        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(self.guardar)
        btn_layout.addWidget(btn_guardar)
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)
        
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)
    
    def seleccionar_logo(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Seleccionar Logo", "", "Image Files (*.png *.jpg *.jpeg)")
        if filename:
            self.logo_path.setText(filename)
    
    def guardar(self):
        self.config['nombre_empresa'] = self.nombre_empresa.text()
        self.config['ciudad'] = self.ciudad.text()
        self.config['precio_agua'] = self.precio_agua.value()
        self.config['precio_luz'] = self.precio_luz.value()
        self.config['costo_folleto'] = self.costo_folleto.value()
        self.config['costo_otros'] = self.costo_otros.value()
        self.config['precio_bolsa_3kg'] = self.costo_bolsa_3kg.value()
        self.config['precio_bolsa_5kg'] = self.costo_bolsa_5kg.value()
        self.config['precio_bolsa_10kg'] = self.costo_bolsa_10kg.value()
        self.config['precio_bolsa_15kg'] = self.costo_bolsa_15kg.value()
        self.config['margen_ganancia_minorista'] = self.margen_minorista.value()
        self.config['margen_ganancia_mayorista'] = self.margen_mayorista.value()
        self.config['logo_path'] = self.logo_path.text()
        
        self.db.guardar_configuracion(self.config)
        QMessageBox.information(self, "Éxito", "Configuración guardada correctamente")
        self.accept()

class AgregarEditarClienteDialog(QDialog):
    def __init__(self, parent, db, cliente_id=None):
        super().__init__(parent)
        self.db = db
        self.cliente_id = cliente_id
        self.init_ui()
    
    def init_ui(self):
        if self.cliente_id:
            self.setWindowTitle("Editar Cliente")
            cliente = self.db.obtener_cliente(self.cliente_id)
        else:
            self.setWindowTitle("Agregar Cliente")
            cliente = None
        
        self.setGeometry(100, 100, 400, 300)
        
        layout = QFormLayout()
        
        self.nombre = QLineEdit()
        if cliente:
            self.nombre.setText(cliente[1])
        layout.addRow("Nombre:", self.nombre)
        
        self.telefono = QLineEdit()
        if cliente:
            self.telefono.setText(cliente[2])
        layout.addRow("Teléfono:", self.telefono)
        
        self.email = QLineEdit()
        if cliente:
            self.email.setText(cliente[3])
        layout.addRow("Email:", self.email)
        
        self.tipo = QComboBox()
        self.tipo.addItems(["Minorista", "Mayorista", "Particular"])
        if cliente:
            self.tipo.setCurrentText(cliente[4])
        layout.addRow("Tipo:", self.tipo)
        
        btn_layout = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(self.guardar)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_guardar)
        btn_layout.addWidget(btn_cancelar)
        
        layout.addRow(btn_layout)
        self.setLayout(layout)
    
    def guardar(self):
        if not self.nombre.text():
            QMessageBox.warning(self, "Error", "Ingrese nombre del cliente")
            return
        
        if self.cliente_id:
            self.db.actualizar_cliente(
                self.cliente_id,
                self.nombre.text(),
                self.telefono.text(),
                self.email.text(),
                self.tipo.currentText()
            )
        else:
            self.db.agregar_cliente(
                self.nombre.text(),
                self.telefono.text(),
                self.email.text(),
                self.tipo.currentText()
            )
        
        QMessageBox.information(self, "Éxito", "Cliente guardado correctamente")
        self.accept()

class VentasTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.config = db.get_configuracion()
        self.calculador = CostoCalculador(self.config)
        self.venta_actual = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Formulario de venta
        form_layout = QFormLayout()
        
        self.cliente = QComboBox()
        self.actualizar_clientes()
        form_layout.addRow("Cliente:", self.cliente)
        
        self.tipo_venta = QComboBox()
        self.tipo_venta.addItems(["Minorista", "Mayorista"])
        self.tipo_venta.currentTextChanged.connect(self.calcular_total)
        form_layout.addRow("Tipo Venta:", self.tipo_venta)
        
        self.bolsas_3kg = QSpinBox()
        self.bolsas_3kg.valueChanged.connect(self.calcular_total)
        form_layout.addRow("Bolsas 3kg:", self.bolsas_3kg)
        
        self.bolsas_5kg = QSpinBox()
        self.bolsas_5kg.valueChanged.connect(self.calcular_total)
        form_layout.addRow("Bolsas 5kg:", self.bolsas_5kg)
        
        self.bolsas_10kg = QSpinBox()
        self.bolsas_10kg.valueChanged.connect(self.calcular_total)
        form_layout.addRow("Bolsas 10kg:", self.bolsas_10kg)
        
        self.bolsas_15kg = QSpinBox()
        self.bolsas_15kg.valueChanged.connect(self.calcular_total)
        form_layout.addRow("Bolsas 15kg:", self.bolsas_15kg)
        
        self.total_label = QLabel("Total: $0.00")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f77b4;")
        form_layout.addRow(self.total_label)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        btn_registrar = QPushButton("✅ Registrar Venta")
        btn_registrar.clicked.connect(self.registrar_venta)
        btn_layout.addWidget(btn_registrar)
        
        btn_nueva_cliente = QPushButton("➕ Nuevo Cliente")
        btn_nueva_cliente.clicked.connect(self.agregar_cliente)
        btn_layout.addWidget(btn_nueva_cliente)
        
        btn_limpiar = QPushButton("🗑️ Limpiar")
        btn_limpiar.clicked.connect(self.limpiar_formulario)
        btn_layout.addWidget(btn_limpiar)
        
        layout.addLayout(btn_layout)
        
        # Tabla de ventas
        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(10)
        self.tabla_ventas.setHorizontalHeaderLabels(["ID", "Fecha", "Cliente", "3kg", "5kg", "10kg", "15kg", "Total", "Boleta", "Acciones"])
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_ventas.itemDoubleClicked.connect(self.editar_venta)
        layout.addWidget(self.tabla_ventas)
        
        self.actualizar_tabla()
        
        self.setLayout(layout)
    
    def actualizar_clientes(self):
        self.cliente.clear()
        clientes = self.db.obtener_clientes()
        for cliente in clientes:
            self.cliente.addItem(cliente[1], cliente[0])
    
    def agregar_cliente(self):
        dialog = AgregarEditarClienteDialog(self, self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.actualizar_clientes()
    
    def calcular_total(self):
        self.total_actual = self.calculador.calcular_total_venta(
            self.bolsas_3kg.value(),
            self.bolsas_5kg.value(),
            self.bolsas_10kg.value(),
            self.bolsas_15kg.value(),
            self.tipo_venta.currentText()
        )
        self.total_label.setText(f"Total: ${self.total_actual:.2f}")
    
    def registrar_venta(self):
        if self.cliente.currentIndex() == -1:
            QMessageBox.warning(self, "Error", "Seleccione un cliente")
            return
        
        cliente_id = self.cliente.currentData()
        numero_boleta, venta_id = self.db.registrar_venta(
            cliente_id,
            self.bolsas_3kg.value(),
            self.bolsas_5kg.value(),
            self.bolsas_10kg.value(),
            self.bolsas_15kg.value(),
            self.total_actual,
            self.tipo_venta.currentText()
        )
        
        QMessageBox.information(self, "Éxito", f"Venta registrada con Boleta: {numero_boleta}")
        
        # Mostrar generador de boleta
        dialog = GeneradorBoleta(self, self.db, venta_id, numero_boleta)
        dialog.exec()
        
        self.actualizar_tabla()
        self.limpiar_formulario()
    
    def editar_venta(self, item):
        row = item.row()
        venta_id = int(self.tabla_ventas.item(row, 0).text())
        # Aquí iría la lógica para editar
        QMessageBox.information(self, "Info", f"Editar venta {venta_id}")
    
    def limpiar_formulario(self):
        self.bolsas_3kg.setValue(0)
        self.bolsas_5kg.setValue(0)
        self.bolsas_10kg.setValue(0)
        self.bolsas_15kg.setValue(0)
        self.calcular_total()
    
    def actualizar_tabla(self):
        ventas = self.db.obtener_ventas()
        self.tabla_ventas.setRowCount(len(ventas))
        
        for i, venta in enumerate(ventas):
            fecha = venta[2][:10] if venta[2] else ""
            
            self.tabla_ventas.setItem(i, 0, QTableWidgetItem(str(venta[0])))
            self.tabla_ventas.setItem(i, 1, QTableWidgetItem(fecha))
            self.tabla_ventas.setItem(i, 2, QTableWidgetItem(venta[-1]))
            self.tabla_ventas.setItem(i, 3, QTableWidgetItem(str(venta[3])))
            self.tabla_ventas.setItem(i, 4, QTableWidgetItem(str(venta[4])))
            self.tabla_ventas.setItem(i, 5, QTableWidgetItem(str(venta[5])))
            self.tabla_ventas.setItem(i, 6, QTableWidgetItem(str(venta[6])))
            self.tabla_ventas.setItem(i, 7, QTableWidgetItem(f"${venta[7]:.2f}"))
            self.tabla_ventas.setItem(i, 8, QTableWidgetItem(venta[9]))
            
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            
            btn_editar = QPushButton("✏️")
            btn_editar.setMaximumWidth(40)
            btn_editar.clicked.connect(lambda checked, vid=venta[0]: self.editar_venta_dialog(vid))
            btn_layout.addWidget(btn_editar)
            
            btn_eliminar = QPushButton("🗑️")
            btn_eliminar.setMaximumWidth(40)
            btn_eliminar.clicked.connect(lambda checked, vid=venta[0]: self.eliminar_venta(vid))
            btn_layout.addWidget(btn_eliminar)
            
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_widget.setLayout(btn_layout)
            self.tabla_ventas.setCellWidget(i, 9, btn_widget)
    
    def editar_venta_dialog(self, venta_id):
        QMessageBox.information(self, "Info", f"Función de editar en desarrollo para venta {venta_id}")
    
    def eliminar_venta(self, venta_id):
        respuesta = QMessageBox.question(self, "Confirmar", "¿Desea eliminar esta venta?")
        if respuesta == QMessageBox.StandardButton.Yes:
            self.db.eliminar_venta(venta_id)
            self.actualizar_tabla()
            QMessageBox.information(self, "Éxito", "Venta eliminada correctamente")

class GastosTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.gasto_actual_id = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Formulario de gastos
        form_layout = QFormLayout()
        
        self.tipo_gasto = QComboBox()
        self.tipo_gasto.addItems(["Agua", "Luz", "Folleto", "Bolsas", "Otro"])
        form_layout.addRow("Tipo Gasto:", self.tipo_gasto)
        
        self.descripcion = QLineEdit()
        form_layout.addRow("Descripción:", self.descripcion)
        
        self.monto = QDoubleSpinBox()
        self.monto.setMaximum(100000)
        form_layout.addRow("Monto ($):", self.monto)
        
        self.fecha_gasto = QDateTimeEdit()
        self.fecha_gasto.setDateTime(QDateTime.currentDateTime())
        form_layout.addRow("Fecha:", self.fecha_gasto)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        btn_registrar = QPushButton("✅ Registrar Gasto")
        btn_registrar.clicked.connect(self.registrar_gasto)
        btn_layout.addWidget(btn_registrar)
        
        btn_limpiar = QPushButton("🗑️ Limpiar")
        btn_limpiar.clicked.connect(self.limpiar_formulario)
        btn_layout.addWidget(btn_limpiar)
        
        layout.addLayout(btn_layout)
        
        # Tabla de gastos
        self.tabla_gastos = QTableWidget()
        self.tabla_gastos.setColumnCount(6)
        self.tabla_gastos.setHorizontalHeaderLabels(["ID", "Fecha", "Tipo", "Descripción", "Monto", "Acciones"])
        self.tabla_gastos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_gastos)
        
        self.actualizar_tabla()
        
        self.setLayout(layout)
    
    def registrar_gasto(self):
        if self.monto.value() <= 0:
            QMessageBox.warning(self, "Error", "Ingrese un monto válido")
            return
        
        if self.gasto_actual_id:
            self.db.actualizar_gasto(
                self.gasto_actual_id,
                self.tipo_gasto.currentText(),
                self.descripcion.text(),
                self.monto.value()
            )
            QMessageBox.information(self, "Éxito", "Gasto actualizado correctamente")
            self.gasto_actual_id = None
        else:
            self.db.registrar_gasto(
                self.tipo_gasto.currentText(),
                self.descripcion.text(),
                self.monto.value()
            )
            QMessageBox.information(self, "Éxito", "Gasto registrado correctamente")
        
        self.actualizar_tabla()
        self.limpiar_formulario()
    
    def limpiar_formulario(self):
        self.descripcion.clear()
        self.monto.setValue(0)
        self.tipo_gasto.setCurrentIndex(0)
        self.gasto_actual_id = None
    
    def editar_gasto(self, gasto_id):
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM gastos WHERE id=?', (gasto_id,))
        gasto = cursor.fetchone()
        conn.close()
        
        if gasto:
            self.tipo_gasto.setCurrentText(gasto[1])
            self.descripcion.setText(gasto[2])
            self.monto.setValue(gasto[3])
            self.gasto_actual_id = gasto_id
    
    def eliminar_gasto(self, gasto_id):
        respuesta = QMessageBox.question(self, "Confirmar", "¿Desea eliminar este gasto?")
        if respuesta == QMessageBox.StandardButton.Yes:
            self.db.eliminar_gasto(gasto_id)
            self.actualizar_tabla()
            QMessageBox.information(self, "Éxito", "Gasto eliminado correctamente")
    
    def actualizar_tabla(self):
        gastos = self.db.obtener_gastos()
        self.tabla_gastos.setRowCount(len(gastos))
        
        for i, gasto in enumerate(gastos):
            fecha = gasto[4][:10] if gasto[4] else ""
            
            self.tabla_gastos.setItem(i, 0, QTableWidgetItem(str(gasto[0])))
            self.tabla_gastos.setItem(i, 1, QTableWidgetItem(fecha))
            self.tabla_gastos.setItem(i, 2, QTableWidgetItem(gasto[1]))
            self.tabla_gastos.setItem(i, 3, QTableWidgetItem(gasto[2]))
            self.tabla_gastos.setItem(i, 4, QTableWidgetItem(f"${gasto[3]:.2f}"))
            
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            
            btn_editar = QPushButton("✏️")
            btn_editar.setMaximumWidth(40)
            btn_editar.clicked.connect(lambda checked, gid=gasto[0]: self.editar_gasto(gid))
            btn_layout.addWidget(btn_editar)
            
            btn_eliminar = QPushButton("🗑️")
            btn_eliminar.setMaximumWidth(40)
            btn_eliminar.clicked.connect(lambda checked, gid=gasto[0]: self.eliminar_gasto(gid))
            btn_layout.addWidget(btn_eliminar)
            
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_widget.setLayout(btn_layout)
            self.tabla_gastos.setCellWidget(i, 5, btn_widget)

class ProduccionTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.produccion_actual_id = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Formulario de producción
        form_layout = QFormLayout()
        
        self.bolsas_3kg = QSpinBox()
        self.bolsas_3kg.valueChanged.connect(self.calcular_total)
        form_layout.addRow("Bolsas 3kg:", self.bolsas_3kg)
        
        self.bolsas_5kg = QSpinBox()
        self.bolsas_5kg.valueChanged.connect(self.calcular_total)
        form_layout.addRow("Bolsas 5kg:", self.bolsas_5kg)
        
        self.bolsas_10kg = QSpinBox()
        self.bolsas_10kg.valueChanged.connect(self.calcular_total)
        form_layout.addRow("Bolsas 10kg:", self.bolsas_10kg)
        
        self.bolsas_15kg = QSpinBox()
        self.bolsas_15kg.valueChanged.connect(self.calcular_total)
        form_layout.addRow("Bolsas 15kg:", self.bolsas_15kg)
        
        self.fecha_produccion = QDateTimeEdit()
        self.fecha_produccion.setDateTime(QDateTime.currentDateTime())
        form_layout.addRow("Fecha:", self.fecha_produccion)
        
        self.total_producido = QLabel("Total: 0 bolsas")
        self.total_producido.setStyleSheet("font-weight: bold; color: #1f77b4;")
        form_layout.addRow(self.total_producido)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        btn_registrar = QPushButton("✅ Registrar Producción")
        btn_registrar.clicked.connect(self.registrar_produccion)
        btn_layout.addWidget(btn_registrar)
        
        btn_limpiar = QPushButton("🗑️ Limpiar")
        btn_limpiar.clicked.connect(self.limpiar_formulario)
        btn_layout.addWidget(btn_limpiar)
        
        layout.addLayout(btn_layout)
        
        # Tabla de producción
        self.tabla_produccion = QTableWidget()
        self.tabla_produccion.setColumnCount(8)
        self.tabla_produccion.setHorizontalHeaderLabels(["ID", "Fecha", "3kg", "5kg", "10kg", "15kg", "Total", "Acciones"])
        self.tabla_produccion.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_produccion)
        
        self.actualizar_tabla()
        
        self.setLayout(layout)
    
    def calcular_total(self):
        total = (self.bolsas_3kg.value() + self.bolsas_5kg.value() + 
                self.bolsas_10kg.value() + self.bolsas_15kg.value())
        self.total_producido.setText(f"Total: {total} bolsas")
    
    def registrar_produccion(self):
        total = (self.bolsas_3kg.value() + self.bolsas_5kg.value() + 
                self.bolsas_10kg.value() + self.bolsas_15kg.value())
        
        if total == 0:
            QMessageBox.warning(self, "Error", "Ingrese al menos una bolsa")
            return
        
        if self.produccion_actual_id:
            self.db.actualizar_produccion(
                self.produccion_actual_id,
                self.bolsas_3kg.value(),
                self.bolsas_5kg.value(),
                self.bolsas_10kg.value(),
                self.bolsas_15kg.value(),
                total
            )
            QMessageBox.information(self, "Éxito", "Producción actualizada correctamente")
            self.produccion_actual_id = None
        else:
            self.db.registrar_produccion(
                self.bolsas_3kg.value(),
                self.bolsas_5kg.value(),
                self.bolsas_10kg.value(),
                self.bolsas_15kg.value(),
                total
            )
            QMessageBox.information(self, "Éxito", "Producción registrada correctamente")
        
        self.actualizar_tabla()
        self.limpiar_formulario()
    
    def editar_produccion(self, produccion_id):
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produccion WHERE id=?', (produccion_id,))
        prod = cursor.fetchone()
        conn.close()
        
        if prod:
            self.bolsas_3kg.setValue(prod[2])
            self.bolsas_5kg.setValue(prod[3])
            self.bolsas_10kg.setValue(prod[4])
            self.bolsas_15kg.setValue(prod[5])
            self.produccion_actual_id = produccion_id
    
    def eliminar_produccion(self, produccion_id):
        respuesta = QMessageBox.question(self, "Confirmar", "¿Desea eliminar este registro de producción?")
        if respuesta == QMessageBox.StandardButton.Yes:
            self.db.eliminar_produccion(produccion_id)
            self.actualizar_tabla()
            QMessageBox.information(self, "Éxito", "Producción eliminada correctamente")
    
    def limpiar_formulario(self):
        self.bolsas_3kg.setValue(0)
        self.bolsas_5kg.setValue(0)
        self.bolsas_10kg.setValue(0)
        self.bolsas_15kg.setValue(0)
        self.calcular_total()
    
    def actualizar_tabla(self):
        produccion = self.db.obtener_produccion()
        self.tabla_produccion.setRowCount(len(produccion))
        
        for i, prod in enumerate(produccion):
            fecha = prod[1][:10] if prod[1] else ""
            
            self.tabla_produccion.setItem(i, 0, QTableWidgetItem(str(prod[0])))
            self.tabla_produccion.setItem(i, 1, QTableWidgetItem(fecha))
            self.tabla_produccion.setItem(i, 2, QTableWidgetItem(str(prod[2])))
            self.tabla_produccion.setItem(i, 3, QTableWidgetItem(str(prod[3])))
            self.tabla_produccion.setItem(i, 4, QTableWidgetItem(str(prod[4])))
            self.tabla_produccion.setItem(i, 5, QTableWidgetItem(str(prod[5])))
            self.tabla_produccion.setItem(i, 6, QTableWidgetItem(str(prod[6])))
            
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            
            btn_editar = QPushButton("✏️")
            btn_editar.setMaximumWidth(40)
            btn_editar.clicked.connect(lambda checked, pid=prod[0]: self.editar_produccion(pid))
            btn_layout.addWidget(btn_editar)
            
            btn_eliminar = QPushButton("🗑️")
            btn_eliminar.setMaximumWidth(40)
            btn_eliminar.clicked.connect(lambda checked, pid=prod[0]: self.eliminar_produccion(pid))
            btn_layout.addWidget(btn_eliminar)
            
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_widget.setLayout(btn_layout)
            self.tabla_produccion.setCellWidget(i, 7, btn_widget)

class ClientesTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        btn_agregar = QPushButton("➕ Agregar Cliente")
        btn_agregar.clicked.connect(self.agregar_cliente)
        btn_layout.addWidget(btn_agregar)
        
        layout.addLayout(btn_layout)
        
        # Tabla de clientes
        self.tabla_clientes = QTableWidget()
        self.tabla_clientes.setColumnCount(7)
        self.tabla_clientes.setHorizontalHeaderLabels(["ID", "Nombre", "Teléfono", "Email", "Tipo", "Saldo", "Acciones"])
        self.tabla_clientes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_clientes)
        
        self.actualizar_tabla()
        
        self.setLayout(layout)
    
    def agregar_cliente(self):
        dialog = AgregarEditarClienteDialog(self, self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.actualizar_tabla()
    
    def editar_cliente(self, cliente_id):
        dialog = AgregarEditarClienteDialog(self, self.db, cliente_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.actualizar_tabla()
    
    def eliminar_cliente(self, cliente_id):
        respuesta = QMessageBox.question(self, "Confirmar", "¿Desea eliminar este cliente?")
        if respuesta == QMessageBox.StandardButton.Yes:
            self.db.eliminar_cliente(cliente_id)
            self.actualizar_tabla()
            QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente")
    
    def actualizar_tabla(self):
        clientes = self.db.obtener_clientes()
        self.tabla_clientes.setRowCount(len(clientes))
        
        for i, cliente in enumerate(clientes):
            self.tabla_clientes.setItem(i, 0, QTableWidgetItem(str(cliente[0])))
            self.tabla_clientes.setItem(i, 1, QTableWidgetItem(cliente[1]))
            self.tabla_clientes.setItem(i, 2, QTableWidgetItem(cliente[2]))
            self.tabla_clientes.setItem(i, 3, QTableWidgetItem(cliente[3]))
            self.tabla_clientes.setItem(i, 4, QTableWidgetItem(cliente[4]))
            self.tabla_clientes.setItem(i, 5, QTableWidgetItem(f"${cliente[5]:.2f}"))
            
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            
            btn_editar = QPushButton("✏️")
            btn_editar.setMaximumWidth(40)
            btn_editar.clicked.connect(lambda checked, cid=cliente[0]: self.editar_cliente(cid))
            btn_layout.addWidget(btn_editar)
            
            btn_eliminar = QPushButton("🗑️")
            btn_eliminar.setMaximumWidth(40)
            btn_eliminar.clicked.connect(lambda checked, cid=cliente[0]: self.eliminar_cliente(cid))
            btn_layout.addWidget(btn_eliminar)
            
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_widget.setLayout(btn_layout)
            self.tabla_clientes.setCellWidget(i, 6, btn_widget)

class PedidosTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.pedido_actual_id = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Formulario de pedido
        form_layout = QFormLayout()
        
        self.cliente = QComboBox()
        self.actualizar_clientes()
        form_layout.addRow("Cliente:", self.cliente)
        
        self.fecha_entrega = QDateEdit()
        self.fecha_entrega.setDate(QDate.currentDate().addDays(1))
        form_layout.addRow("Fecha Entrega:", self.fecha_entrega)
        
        self.estado = QComboBox()
        self.estado.addItems(["Pendiente", "En Proceso", "Completado", "Cancelado"])
        form_layout.addRow("Estado:", self.estado)
        
        self.bolsas_3kg = QSpinBox()
        form_layout.addRow("Bolsas 3kg:", self.bolsas_3kg)
        
        self.bolsas_5kg = QSpinBox()
        form_layout.addRow("Bolsas 5kg:", self.bolsas_5kg)
        
        self.bolsas_10kg = QSpinBox()
        form_layout.addRow("Bolsas 10kg:", self.bolsas_10kg)
        
        self.bolsas_15kg = QSpinBox()
        form_layout.addRow("Bolsas 15kg:", self.bolsas_15kg)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        btn_agregar = QPushButton("✅ Registrar Pedido")
        btn_agregar.clicked.connect(self.agregar_pedido)
        btn_layout.addWidget(btn_agregar)
        
        btn_limpiar = QPushButton("🗑️ Limpiar")
        btn_limpiar.clicked.connect(self.limpiar_formulario)
        btn_layout.addWidget(btn_limpiar)
        
        layout.addLayout(btn_layout)
        
        # Tabla de pedidos
        self.tabla_pedidos = QTableWidget()
        self.tabla_pedidos.setColumnCount(10)
        self.tabla_pedidos.setHorizontalHeaderLabels(["ID", "Cliente", "F. Entrega", "3kg", "5kg", "10kg", "15kg", "Estado", "Acción", ""])
        self.tabla_pedidos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_pedidos)
        
        self.actualizar_tabla()
        
        self.setLayout(layout)
    
    def actualizar_clientes(self):
        self.cliente.clear()
        clientes = self.db.obtener_clientes()
        for cliente in clientes:
            self.cliente.addItem(cliente[1], cliente[0])
    
    def agregar_pedido(self):
        if self.cliente.currentIndex() == -1:
            QMessageBox.warning(self, "Error", "Seleccione un cliente")
            return
        
        total = (self.bolsas_3kg.value() + self.bolsas_5kg.value() + 
                self.bolsas_10kg.value() + self.bolsas_15kg.value())
        
        if total == 0:
            QMessageBox.warning(self, "Error", "Ingrese al menos una bolsa")
            return
        
        if self.pedido_actual_id:
            self.db.actualizar_pedido(
                self.pedido_actual_id,
                self.cliente.currentData(),
                self.fecha_entrega.date().toString("yyyy-MM-dd"),
                self.bolsas_3kg.value(),
                self.bolsas_5kg.value(),
                self.bolsas_10kg.value(),
                self.bolsas_15kg.value(),
                self.estado.currentText()
            )
            QMessageBox.information(self, "Éxito", "Pedido actualizado correctamente")
            self.pedido_actual_id = None
        else:
            self.db.agregar_pedido(
                self.cliente.currentData(),
                self.fecha_entrega.date().toString("yyyy-MM-dd"),
                self.bolsas_3kg.value(),
                self.bolsas_5kg.value(),
                self.bolsas_10kg.value(),
                self.bolsas_15kg.value()
            )
            QMessageBox.information(self, "Éxito", "Pedido registrado correctamente")
        
        self.actualizar_tabla()
        self.limpiar_formulario()
    
    def editar_pedido(self, pedido_id):
        pedido = self.db.obtener_pedido(pedido_id)
        if pedido:
            for i in range(self.cliente.count()):
                if self.cliente.itemData(i) == pedido[1]:
                    self.cliente.setCurrentIndex(i)
                    break
            self.fecha_entrega.setDate(QDate.fromString(pedido[3][:10], "yyyy-MM-dd"))
            self.bolsas_3kg.setValue(pedido[4])
            self.bolsas_5kg.setValue(pedido[5])
            self.bolsas_10kg.setValue(pedido[6])
            self.bolsas_15kg.setValue(pedido[7])
            self.estado.setCurrentText(pedido[8])
            self.pedido_actual_id = pedido_id
    
    def eliminar_pedido(self, pedido_id):
        respuesta = QMessageBox.question(self, "Confirmar", "¿Desea eliminar este pedido?")
        if respuesta == QMessageBox.StandardButton.Yes:
            self.db.eliminar_pedido(pedido_id)
            self.actualizar_tabla()
            QMessageBox.information(self, "Éxito", "Pedido eliminado correctamente")
    
    def limpiar_formulario(self):
        self.bolsas_3kg.setValue(0)
        self.bolsas_5kg.setValue(0)
        self.bolsas_10kg.setValue(0)
        self.bolsas_15kg.setValue(0)
        self.estado.setCurrentIndex(0)
    
    def actualizar_tabla(self):
        pedidos = self.db.obtener_pedidos()
        self.tabla_pedidos.setRowCount(len(pedidos))
        
        for i, pedido in enumerate(pedidos):
            fecha_entrega = pedido[3][:10] if pedido[3] else ""
            
            self.tabla_pedidos.setItem(i, 0, QTableWidgetItem(str(pedido[0])))
            self.tabla_pedidos.setItem(i, 1, QTableWidgetItem(pedido[-1]))
            self.tabla_pedidos.setItem(i, 2, QTableWidgetItem(fecha_entrega))
            self.tabla_pedidos.setItem(i, 3, QTableWidgetItem(str(pedido[4])))
            self.tabla_pedidos.setItem(i, 4, QTableWidgetItem(str(pedido[5])))
            self.tabla_pedidos.setItem(i, 5, QTableWidgetItem(str(pedido[6])))
            self.tabla_pedidos.setItem(i, 6, QTableWidgetItem(str(pedido[7])))
            self.tabla_pedidos.setItem(i, 7, QTableWidgetItem(pedido[8]))
            
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            
            btn_editar = QPushButton("✏️")
            btn_editar.setMaximumWidth(40)
            btn_editar.clicked.connect(lambda checked, pid=pedido[0]: self.editar_pedido(pid))
            btn_layout.addWidget(btn_editar)
            
            btn_eliminar = QPushButton("🗑️")
            btn_eliminar.setMaximumWidth(40)
            btn_eliminar.clicked.connect(lambda checked, pid=pedido[0]: self.eliminar_pedido(pid))
            btn_layout.addWidget(btn_eliminar)
            
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_widget.setLayout(btn_layout)
            self.tabla_pedidos.setCellWidget(i, 8, btn_widget)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.config = self.db.get_configuracion()
        self.dark_mode = False
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("YC HIELO - Sistema de Gestión")
        self.setGeometry(0, 0, 1600, 1000)
        
        # Icono de la aplicación
        icon = QIcon("yc_hielo_icon.png")
        self.setWindowIcon(icon)
        
        # Widget central
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Encabezado
        header = QHBoxLayout()
        
        titulo = QLabel("YC HIELO - Sistema de Gestión")
        titulo_font = QFont()
        titulo_font.setPointSize(16)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        titulo.setStyleSheet("color: #1f77b4;")
        header.addWidget(titulo)
        
        header.addStretch()
        
        btn_dark_mode = QPushButton("🌙 Modo Noche")
        btn_dark_mode.clicked.connect(self.toggle_dark_mode)
        header.addWidget(btn_dark_mode)
        
        btn_config = QPushButton("⚙️ Configuración")
        btn_config.clicked.connect(self.abrir_configuracion)
        header.addWidget(btn_config)
        
        btn_precios = QPushButton("💰 Precios Sugeridos")
        btn_precios.clicked.connect(self.abrir_precios)
        header.addWidget(btn_precios)
        
        layout.addLayout(header)
        
        # Pestañas
        tabs = QTabWidget()
        
        self.tab_ventas = VentasTab(self.db)
        self.tab_gastos = GastosTab(self.db)
        self.tab_produccion = ProduccionTab(self.db)
        self.tab_clientes = ClientesTab(self.db)
        self.tab_pedidos = PedidosTab(self.db)
        
        tabs.addTab(self.tab_ventas, "📊 Ventas")
        tabs.addTab(self.tab_gastos, "💸 Gastos")
        tabs.addTab(self.tab_produccion, "🏭 Producción")
        tabs.addTab(self.tab_clientes, "👥 Clientes")
        tabs.addTab(self.tab_pedidos, "📦 Pedidos")
        
        layout.addWidget(tabs)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        self.apply_style()
    
    def apply_style(self):
        if self.dark_mode:
            style = """
            QMainWindow { background-color: #2b2b2b; }
            QWidget { background-color: #2b2b2b; color: #ffffff; }
            QTabWidget::pane { border: 1px solid #404040; }
            QTabBar::tab { background-color: #1e1e1e; color: #ffffff; padding: 8px; }
            QTabBar::tab:selected { background-color: #404040; }
            QPushButton { background-color: #1f77b4; color: white; border: none; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #1555a0; }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTableWidget, QDateEdit, QDateTimeEdit { 
                background-color: #1e1e1e; 
                color: #ffffff; 
                border: 1px solid #404040;
                padding: 4px;
            }
            QTableWidget::item { padding: 4px; }
            QHeaderView::section { background-color: #1555a0; color: white; padding: 4px; }
            QGroupBox { color: #ffffff; border: 1px solid #404040; }
            """
        else:
            style = """
            QMainWindow { background-color: #ffffff; }
            QWidget { background-color: #ffffff; }
            QTabWidget::pane { border: 1px solid #cccccc; }
            QTabBar::tab { background-color: #f0f0f0; padding: 8px; }
            QTabBar::tab:selected { background-color: #ffffff; border-bottom: 2px solid #1f77b4; }
            QPushButton { background-color: #1f77b4; color: white; border: none; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #1555a0; }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTableWidget, QDateEdit, QDateTimeEdit { 
                background-color: #ffffff; 
                border: 1px solid #cccccc;
                padding: 4px;
            }
            QHeaderView::section { background-color: #1f77b4; color: white; padding: 4px; }
            QGroupBox { border: 1px solid #cccccc; }
            """
        
        self.setStyleSheet(style)
    
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_style()
    
    def abrir_configuracion(self):
        dialog = ConfiguracionDialog(self, self.db)
        dialog.exec()
        self.config = self.db.get_configuracion()
        self.tab_ventas.config = self.config
        self.tab_ventas.calculador = CostoCalculador(self.config)
    
    def abrir_precios(self):
        dialog = GeneradorPreciosDialog(self, self.db)
        dialog.exec()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
