🗺️ Hoja de Ruta - Proyecto FlowGestion
Este documento detalla el progreso y la planificación del sistema de gestión para comercios (almacenes, kioscos y minimercados) desarrollado en Python y PyQt6.

🏁 1. Hitos Alcanzados (Lo que ya hicimos)
Configuración del Entorno y Estructura
Identidad del Proyecto: Definición del nombre final como FlowGestion y establecimiento de la estructura de carpetas profesional (src, assets, database).

Gestión de Dependencias: Creación del archivo requirements.txt incluyendo PyQt6, SQLAlchemy y Pandas.

Entorno de Desarrollo: Configuración de VS Code y entorno virtual .venv.

Base de Datos
Modelo de Datos: Definición de la clase Producto con campos para código de barras, nombre, precio, stock y categoría.

Motor de DB: Configuración de SQLite para almacenamiento local ligero y portable.

Interfaz de Usuario (UI)
Ventana Principal: Creación del QMainWindow con un diseño de panel lateral (Sidebar) y área de contenido central.

Estilo Visual (QSS): Implementación de una hoja de estilos moderna con colores corporativos (Azul oscuro #1E293B y Verde #22C55E), bordes redondeados y tipografía limpia.

Punto de Entrada: Archivo main.py funcional que integra la UI con el motor de estilos.

🚀 2. Próximos Pasos (Lo que vamos a hacer)
Fase 1: Gestión de Inventario (Prioridad Alta)
[ ] Navegación Dinámica: Implementar QStackedWidget para cambiar entre pantallas sin cerrar la ventana.

[ ] Controlador de DB: Crear funciones para CRUD (Crear, Leer, Actualizar, Borrar) productos.

[ ] Módulo de Carga: Ventana emergente (Dialog) para registrar nuevos productos manualmente.

[ ] Visualización: Tabla de stock con filtros de búsqueda rápida.

Fase 2: Módulo de Ventas (El Corazón del Sistema)
[ ] Lector de Barras: Lógica para buscar productos automáticamente al escanear.

[ ] Carrito de Compras: Lista temporal de productos, cálculo de subtotal, IVA y total.

[ ] Finalización de Venta: Registro en base de datos y actualización automática de stock.

Fase 3: Clientes y Reportes
[ ] Gestión de Clientes: Registro para cuentas corrientes o fidelización.

[ ] Reportes con Pandas: Generación de estadísticas de ventas diarias/mensuales y exportación a Excel.

Fase 4: Pulido y Extras
[ ] Tickets: Generación de tickets de venta (formato térmico).

[ ] Seguridad: Sistema de login para empleados y administradores.

[ ] Sincronización: (Opcional) Conexión con base de datos en la nube.

Nota: Este proyecto busca la eficiencia y una experiencia de usuario fluida para el comerciante.