# src/ui/add_product_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QMessageBox)
from src.database.controller import registrar_producto

class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Producto - FlowGestion")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)

        # Campos de texto con estilo
        self.txt_codigo = QLineEdit(placeholderText="Código de Barras")
        self.txt_nombre = QLineEdit(placeholderText="Nombre del Producto")
        self.txt_precio = QLineEdit(placeholderText="Precio de Venta")
        self.txt_stock = QLineEdit(placeholderText="Stock Inicial")
        self.txt_categoria = QLineEdit(placeholderText="Categoría (Ej: Almacén)")

        # Botón para guardar
        btn_guardar = QPushButton("💾 Guardar Producto")
        btn_guardar.setObjectName("btnVenta") # Reutilizamos el estilo verde alegre
        btn_guardar.clicked.connect(self.guardar)

        # Agregar al diseño
        layout.addWidget(QLabel("<h3>Registrar Producto</h3>"))
        layout.addWidget(self.txt_codigo)
        layout.addWidget(self.txt_nombre)
        layout.addWidget(self.txt_precio)
        layout.addWidget(self.txt_stock)
        layout.addWidget(self.txt_categoria)
        layout.addWidget(btn_guardar)

    def guardar(self):
        exito, msj = registrar_producto(
            self.txt_codigo.text(),
            self.txt_nombre.text(),
            self.txt_precio.text(),
            self.txt_stock.text(),
            self.txt_categoria.text()
        )
        
        if exito:
            QMessageBox.information(self, "Éxito", msj)
            self.accept() # Cierra la ventana
        else:
            QMessageBox.critical(self, "Error", msj)