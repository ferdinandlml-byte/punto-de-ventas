# Punto de Venta - Abarrotes

Aplicación de escritorio en Python (PySide6) con base de datos SQLite. Incluye lectura de códigos de barras (como teclado), carrito, totales y registro de ventas.

## Requisitos
- Windows 10/11
- Python 3.10+

## Instalación (Windows)
1. Crear entorno virtual:
   - `python -m venv .venv`
2. Activar entorno virtual (PowerShell):
   - `.\.venv\Scripts\Activate.ps1`
3. Instalar dependencias:
   - `pip install -r requirements.txt`

## Ejecutar
- `python -m app`

## Acceso
Usuario inicial: `admin`
Contraseña inicial: `1234`

## Ejecutar con .exe (sin instalar Python)
1. En este proyecto, el ejecutable se genera en `dist/AbarrotesPOS/AbarrotesPOS.exe`.
2. Copia la carpeta completa `dist/AbarrotesPOS` a la otra computadora.
3. Ejecuta `AbarrotesPOS.exe`.

## Datos de ejemplo
Al iniciar por primera vez, se cargan productos de ejemplo. También puedes ejecutar:
- `python scripts/seed_data.py`

## Uso rápido
- Escanea el código de barras en el campo de código.
- Ajusta la cantidad si es necesario (piezas o kilos).
- Presiona Enter o el botón "Agregar".
- Finaliza la venta con "Finalizar venta".

## Módulos
- Ventas (IVA, descuentos y ticket en PDF)
- Inventario (agregar/editar/eliminar)
- Clientes, Proveedores, Compras, Gastos, Usuarios
- Reportes (corte diario y top productos) con exportación CSV/Excel/PDF
- Configuración (empresa, moneda, IVA, respaldo, importación)

## Base de datos
El archivo SQLite se guarda en `data/pos.db`.

## Configuración del lector
- El lector debe estar en modo teclado (HID).
- Configura el lector para enviar Enter al final del código.

## Notas
- Cambia los productos de ejemplo por los reales de tu tienda.
- Si vendes a granel, puedes usar cantidades con decimales.
