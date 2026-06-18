# 🧊 YC HIELO - Sistema de Gestión

Sistema integral de gestión para la venta de hielo con control de costos, precios, clientes, ventas, producción y pedidos.

## 🎯 Características

✅ **Cálculo Automático de Costos** - Calcula automáticamente precios minorista y mayorista
✅ **Control de Gastos** - Agua, Luz, Folletos, Bolsas y otros
✅ **Múltiples Presentaciones** - Bolsas de 3kg, 5kg, 10kg y 15kg
✅ **Margen de Ganancia Configurable** - Por porcentaje para minorista y mayorista
✅ **Gestión de Clientes** - Agregar, editar y eliminar clientes
✅ **Control de Ventas** - Registro completo con boletas
✅ **Generación de PDF** - Crear boletas en PDF
✅ **Generador de QR** - Códigos QR para boletas
✅ **Registro de Pedidos** - Control de pedidos pendientes
✅ **Control de Producción** - Registro diario, semanal y mensual
✅ **Modo Noche** - Tema oscuro integrado
✅ **Configuración Personalizada** - Logo y datos de la empresa
✅ **Base de Datos SQLite** - Todos los datos guardados localmente
✅ **Moneda en Pesos Argentinos** - Configurado para Argentina

## 📋 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/porta36/yc-hielo-app.git
cd yc-hielo-app
```

### 2. Crear un Entorno Virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

## 💻 Uso

### Ejecutar la Aplicación

```bash
python main.py
```

### Crear Ejecutable (.exe)

```bash
pip install pyinstaller
pyinstaller build.spec
```

El archivo ejecutable se encontrará en la carpeta `dist/YC_HIELO/YC_HIELO.exe`

### Crear Instalador

```bash
python setup.py bdist_msi
```

## 📱 Interfaz

### Pestaña Ventas
- Seleccionar cliente
- Elegir tipo de venta (Minorista/Mayorista)
- Ingresar cantidades de bolsas
- **Cálculo automático** del total
- Generar boletas en PDF y QR

### Pestaña Gastos
- Registrar gastos por tipo
- Editar gastos existentes
- Eliminar registros
- Detalles completos de gasto y fecha

### Pestaña Producción
- Registrar producción diaria
- Editar registros de producción
- Ver histórico
- Total de bolsas producidas

### Pestaña Clientes
- Agregar nuevos clientes
- Editar información de clientes
- Eliminar clientes
- Ver saldo de cuenta corriente

### Pestaña Pedidos
- Crear nuevos pedidos
- Editar estado de pedidos
- Eliminar pedidos
- Gestionar fechas de entrega

### Configuración
- Personalizar nombre de empresa
- Configurar costos operativos
- Establecer precios base de bolsas
- Definir márgenes de ganancia
- Agregar logo personalizado

### Generador de Precios
- Calcular automáticamente precios sugeridos
- Ver ganancia por presentación
- Guardar nuevos precios

## 🗄️ Base de Datos

La aplicación usa SQLite para almacenar:
- Configuración de la empresa
- Información de clientes
- Registro de ventas y boletas
- Control de gastos
- Producción diaria
- Pedidos pendientes
- Movimientos de cuenta corriente

## 🎨 Temas

- **Modo Claro**: Interfaz clara y profesional
- **Modo Noche**: Tema oscuro para trabajar en ambientes con poca luz

## 📝 Notas

- Todos los datos se guardan automáticamente en `datos_yc_hielo.db`
- Los precios se calculan automáticamente basándose en los márgenes configurados
- Las boletas incluyen número único generado por fecha y hora
- Los QR contienen información de la boleta para rastreo

## 📞 Soporte

Para problemas o sugerencias, contacta al desarrollador.

## 📄 Licencia

Este proyecto es propiedad de YC HIELO.

---

**YC HIELO - Sistema de Gestión v1.0**
Rosario, Argentina 🇦🇷
