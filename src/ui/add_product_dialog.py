# src/ui/add_product_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from src.database.controller import registrar_producto, editar_producto

class AddProductDialog(QDialog):
    def __init__(self, parent=None, producto_id=None):
        super().__init__(parent)
        self.p_id = producto_id
        self.setWindowTitle("Producto" if not self.p_id else "Editar Producto")
        layout = QVBoxLayout(self)

        self.txt_codigo = QLineEdit(placeholderText="Código")
        self.txt_nombre = QLineEdit(placeholderText="Nombre")
        self.txt_costo = QLineEdit(placeholderText="Precio Costo ($)")
        self.txt_venta = QLineEdit(placeholderText="Precio Venta ($)")
        self.txt_stock = QLineEdit(placeholderText="Stock")
        self.txt_cat = QLineEdit(placeholderText="Categoría")

        btn = QPushButton("💾 Guardar"); btn.setObjectName("btnVenta"); btn.clicked.connect(self.guardar)

        layout.addWidget(QLabel(f"<h3>{self.windowTitle()}</h3>"))
        for w in [self.txt_codigo, self.txt_nombre, self.txt_costo, self.txt_venta, self.txt_stock, self.txt_cat, btn]:
            layout.addWidget(w)

    def guardar(self):
        vals = [self.txt_codigo.text(), self.txt_nombre.text(), self.txt_costo.text(), 
                self.txt_venta.text(), self.txt_stock.text(), self.txt_cat.text()]
        if not all(vals):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios"); return

        f = editar_producto if self.p_id else registrar_producto
        args = [self.p_id] + vals if self.p_id else vals
        exito, msj = f(*args)
        
        if exito: QMessageBox.information(self, "Éxito", msj); self.accept()
        else: QMessageBox.critical(self, "Error", msj)