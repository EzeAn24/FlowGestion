from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlowGestion - Sistema de Ventas")
        self.resize(1100, 700)

        # Contenedor principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- SIDEBAR (Menú Lateral) ---
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Logo o Nombre
        title = QLabel("FlowGestion")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin: 20px;")
        sidebar_layout.addWidget(title)

        # Botones de navegación
        self.btn_venta = QPushButton("🛒 Nueva Venta")
        self.btn_venta.setObjectName("btnVenta")
        
        self.btn_stock = QPushButton("📦 Inventario")
        self.btn_clientes = QPushButton("👥 Clientes")
        self.btn_reportes = QPushButton("📊 Reportes")

        sidebar_layout.addWidget(self.btn_venta)
        sidebar_layout.addWidget(self.btn_stock)
        sidebar_layout.addWidget(self.btn_clientes)
        sidebar_layout.addWidget(self.btn_reportes)

        # --- CONTENIDO PRINCIPAL ---
        content_area = QFrame()
        content_area.setObjectName("MainContent")
        content_layout = QVBoxLayout(content_area)
        
        welcome_label = QLabel("Bienvenido al Dashboard")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        content_layout.addWidget(welcome_label, alignment=Qt.AlignmentFlag.AlignTop)

        # Agregar al layout principal
        layout.addWidget(sidebar)
        layout.addWidget(content_area)