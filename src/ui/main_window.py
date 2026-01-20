from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QStackedWidget)
from PyQt6.QtCore import Qt

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
        
        # Conectamos los botones a la lógica de cambio de pantalla
        self.btn_venta.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_stock.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        sidebar_layout.addWidget(self.btn_venta)
        sidebar_layout.addWidget(self.btn_stock)
        sidebar_layout.addWidget(self.btn_clientes)

        # --- CONTENIDO DINÁMICO (Stacked Widget) ---
        self.stack = QStackedWidget()
        self.stack.setObjectName("MainContent")

        # Página 1: Ventas (Placeholder por ahora)
        self.page_ventas = QLabel("Pantalla de Ventas - Aquí irá el carrito")
        self.page_ventas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Página 2: Inventario
        self.page_inventario = QLabel("Pantalla de Inventario - Aquí irá la tabla")
        self.page_inventario.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stack.addWidget(self.page_ventas) # Índice 0
        self.stack.addWidget(self.page_inventario) # Índice 1

        layout.addWidget(sidebar)
        layout.addWidget(self.stack)
        
        def abrir_carga_producto(self):
        dialogo = AddProductDialog(self)
        dialogo.exec()