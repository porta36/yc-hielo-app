# 📋 Guía de Instalación y Uso - YC HIELO

## 🚀 Instalación Rápida

### Opción 1: Ejecutar desde Python (Recomendado para desarrollo)

**Paso 1: Instalar Python**
- Descargar Python 3.8+ desde https://www.python.org/
- Marcar "Add Python to PATH" durante la instalación

**Paso 2: Clonar el Repositorio**
```bash
git clone https://github.com/porta36/yc-hielo-app.git
cd yc-hielo-app
```

**Paso 3: Crear Entorno Virtual**
```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En macOS/Linux
source venv/bin/activate
```

**Paso 4: Instalar Dependencias**
```bash
pip install -r requirements.txt
```

**Paso 5: Ejecutar la Aplicación**
```bash
python main.py
```

---

### Opción 2: Crear Ejecutable (.exe)

**Paso 1: Instalar PyInstaller**
```bash
pip install pyinstaller
```

**Paso 2: Generar el Ejecutable**
```bash
pyinstaller build.spec
```

**Paso 3: Ubicar el Ejecutable**
El archivo se creará en:
```
dist/YC_HIELO/YC_HIELO.exe
```

**Paso 4: Crear Acceso Directo**
- Haz clic derecho en `YC_HIELO.exe`
- Selecciona "Crear acceso directo"
- Coloca el acceso directo en tu escritorio

---

### Opción 3: Crear Instalador (.msi)

**Paso 1: Instalar herramientas necesarias**
```bash
pip install pyinstaller cx-Freeze
```

**Paso 2: Generar el Instalador**
```bash
python setup.py bdist_msi
```

**Paso 3: Ubicar el Instalador**
El archivo `.msi` se creará en la carpeta `dist/`

**Paso 4: Instalar**
- Haz doble clic en el archivo `.msi`
- Sigue las instrucciones del instalador

---

## 📱 Guía de Uso

### 🔧 Configuración Inicial

**1. Abre la Aplicación**
- Ejecuta `python main.py` o abre el `.exe`

**2. Haz Clic en "⚙️ Configuración"**
- Nombre de la Empresa: YC HIELO
- Ciudad: Rosario
- Ingresa los costos operativos (agua, luz, etc.)
- Define los precios base de las bolsas
- Establece márgenes de ganancia
- Carga tu logo (opcional)

**3. Guarda la Configuración**

### 📊 Pestaña de Ventas

**Para registrar una venta:**
1. Selecciona un cliente
2. Elige tipo de venta (Minorista/Mayorista)
3. Ingresa las cantidades de bolsas
4. El total se **calcula automáticamente**
5. Haz clic en "✅ Registrar Venta"
6. Genera PDF y/o QR de la boleta

**Acciones adicionales:**
- ✏️ **Editar**: Haz clic en el icono para editar
- 🗑️ **Eliminar**: Elimina la venta

### 💸 Pestaña de Gastos

**Para registrar gastos:**
1. Selecciona tipo de gasto (Agua, Luz, Folleto, Bolsas, Otro)
2. Agrega descripción
3. Ingresa el monto
4. Haz clic en "✅ Registrar Gasto"

**Editar gastos:**
1. Haz clic en ✏️ para cargar los datos
2. Modifica los valores
3. Haz clic en "✅ Registrar Gasto" para actualizar

**Eliminar:**
- Haz clic en 🗑️ y confirma

### 🏭 Pestaña de Producción

**Para registrar producción:**
1. Ingresa cantidades de bolsas por presentación
2. El total se **calcula automáticamente**
3. Haz clic en "✅ Registrar Producción"

**Opciones:**
- ✏️ **Editar**: Carga datos previos para actualizar
- 🗑️ **Eliminar**: Borra el registro

### 👥 Pestaña de Clientes

**Agregar cliente:**
1. Haz clic en "➕ Agregar Cliente"
2. Completa nombre, teléfono, email, tipo
3. Haz clic en "Guardar"

**Editar cliente:**
1. Haz clic en ✏️
2. Modifica los datos
3. Haz clic en "Guardar"

**Eliminar cliente:**
1. Haz clic en 🗑️
2. Confirma la eliminación

### 📦 Pestaña de Pedidos

**Crear pedido:**
1. Selecciona cliente
2. Define fecha de entrega
3. Selecciona estado (Pendiente/En Proceso/Completado/Cancelado)
4. Ingresa cantidades de bolsas
5. Haz clic en "✅ Registrar Pedido"

**Editar pedido:**
1. Haz clic en ✏️
2. Actualiza los datos
3. Haz clic en "✅ Registrar Pedido"

**Eliminar:**
1. Haz clic en 🗑️

### 💰 Generador de Precios Sugeridos

**Acceso:**
1. Haz clic en "💰 Precios Sugeridos"

**Características:**
- Visualiza precios minorista y mayorista
- Ve la ganancia por presentación
- Modifica costos y márgenes en tiempo real
- Guarda nuevos precios

---

## 🌙 Tema Oscuro

Haz clic en "🌙 Modo Noche" para cambiar entre temas claro y oscuro.

---

## 💾 Datos Guardados

Todos los datos se almacenan en:
```
datos_yc_hielo.db
```

Este archivo se crea automáticamente en la misma carpeta que la aplicación.

---

## 🎯 Cálculos Automáticos

La aplicación calcula automáticamente:

✅ **Precio de venta** = Costo base × (1 + margen%)
✅ **Ganancia unitaria** = Precio de venta - Costo base
✅ **Total de venta** = Suma de todas las bolsas vendidas
✅ **Total de producción** = Suma de todas las bolsas producidas

---

## ⚙️ Configuración Avanzada

### Estructura de Carpetas

```
yc-hielo-app/
├── main.py                 # Aplicación principal
├── requirements.txt        # Dependencias
├── setup.py               # Script de instalación
├── build.spec             # Configuración PyInstaller
├── README.md              # Documentación
├── INSTALL.md             # Esta guía
└── datos_yc_hielo.db      # Base de datos (se crea automáticamente)
```

### Tipos de Gasto

- **Agua**: Costo del agua
- **Luz**: Costo de electricidad
- **Folleto**: Costo de publicidad/folletos
- **Bolsas**: Costo de bolsas
- **Otro**: Otros gastos

### Tipos de Cliente

- **Minorista**: Compras pequeñas, márgenes más altos
- **Mayorista**: Compras grandes, márgenes más bajos
- **Particular**: Compras ocasionales

### Estados de Pedido

- **Pendiente**: Pedido recibido, sin procesar
- **En Proceso**: Se está preparando el pedido
- **Completado**: Pedido entregado
- **Cancelado**: Pedido cancelado

---

## 🐛 Solución de Problemas

### Error: "No module named 'PyQt6'"
**Solución:**
```bash
pip install -r requirements.txt
```

### Error: "Database is locked"
**Solución:** La aplicación intenta acceder a la BD desde dos instancias
- Cierra todas las instancias de la aplicación
- Espera 30 segundos
- Vuelve a abrir

### El ejecutable no se crea
**Solución:**
```bash
pip install --upgrade pyinstaller
pyinstaller build.spec
```

### Permiso denegado en Linux/Mac
**Solución:**
```bash
chmod +x main.py
python main.py
```

---

## 📞 Soporte

Para problemas o sugerencias:
- Abre un issue en GitHub
- Contacta al desarrollador

---

## 📄 Licencia

Proyecto propietario de YC HIELO

---

**Versión:** 1.0.0
**Última actualización:** Junio 2026
**Desarrollado para:** YC HIELO - Rosario, Argentina 🇦🇷
