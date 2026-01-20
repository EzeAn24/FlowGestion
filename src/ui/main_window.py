# src/ui/main_window.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, 
                             QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt
from .add_product_dialog import AddProductDialog
from src.database.controller import obtener_todos_los_productos # Importamos la función de consulta

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlowGestion - Sistema de Ventas")
        self.resize(1100, 700)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- SIDEBAR ---
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("FlowGestion")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin: 20px;")
        sidebar_layout.addWidget(title)

        self.btn_venta = QPushButton("🛒 Nueva Venta")
        self.btn_stock = QPushButton("📦 Inventario")
        self.btn_clientes = QPushButton("👥 Clientes")
        
        # Conexiones de navegación
        self.btn_venta.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_stock.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        sidebar_layout.addWidget(self.btn_venta)
        sidebar_layout.addWidget(self.btn_stock)
        sidebar_layout.addWidget(self.btn_clientes)

        # --- CONTENIDO DINÁMICO ---
        self.stack = QStackedWidget()
        self.stack.setObjectName("MainContent")

        # Configurar páginas
        self.init_page_ventas()
        self.init_page_inventario()

        layout.addWidget(sidebar)
        layout.addWidget(self.stack)

    def init_page_ventas(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("Pantalla de Ventas - Próximamente")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.stack.addWidget(page) # Índice 0

    def init_page_inventario(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        # Cabecera de la página
        header_layout = QHBoxLayout()
        header_label = QLabel("Gestión de Inventario")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        btn_nuevo = QPushButton("+ Agregar Producto")
        btn_nuevo.setObjectName("btnVenta")
        btn_nuevo.setFixedWidth(200)
        btn_nuevo.clicked.connect(self.abrir_carga_producto)

        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(btn_nuevo)

        # Tabla de productos
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(5)
        self.tabla_productos.setHorizontalHeaderLabels(["Código", "Nombre", "Precio", "Stock", "Categoría"])
        self.tabla_productos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_productos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_productos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout.addLayout(header_layout)
        layout.addWidget(self.tabla_productos)
        
        self.stack.addWidget(page) # Índice 1
        self.actualizar_tabla() # Cargar datos iniciales

    def actualizar_tabla(self):
        """Consulta la DB y refresca la tabla."""
        productos = obtener_todos_los_productos()
        self.tabla_productos.setRowCount(0)
        
        for p in productos:
            row = self.tabla_productos.rowCount()
            self.tabla_productos.insertRow(row)
            self.tabla_productos.setItem(row, 0, QTableWidgetItem(str(p.codigo_barras)))
            self.tabla_productos.setItem(row, 1, QTableWidgetItem(str(p.nombre)))
            self.tabla_productos.setItem(row, 2, QTableWidgetItem(f"$ {p.precio_venta:.2f}"))
            self.tabla_productos.setItem(row, 3, QTableWidgetItem(str(p.stock_actual)))
            self.tabla_productos.setItem(row, 4, QTableWidgetItem(str(p.categoria)))

    def abrir_carga_producto(self):
        dialogo = AddProductDialog(self)
        if dialogo.exec(): # Si el usuario guardó correctamente
            self.actualizar_tabla() # Refrescamos la lista automáticamente