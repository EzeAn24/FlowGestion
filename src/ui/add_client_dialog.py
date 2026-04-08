from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from src.database.controller import registrar_cliente

class AddClientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Cliente / Fidelización")
        self.setFixedSize(320, 350)
        
        layout = QVBoxLayout(self)

        self.txt_dni = QLineEdit(placeholderText="DNI (Sin puntos)")
        self.txt_nombre = QLineEdit(placeholderText="Nombre y Apellido")
        self.txt_tel = QLineEdit(placeholderText="Teléfono / WhatsApp")
        self.txt_email = QLineEdit(placeholderText="Correo Electrónico (Opcional)")
        self.txt_dir = QLineEdit(placeholderText="Dirección (Opcional)")

        btn_guardar = QPushButton("💾 Guardar Cliente")
        btn_guardar.setObjectName("btnVenta")
        btn_guardar.clicked.connect(self.guardar)

        layout.addWidget(QLabel("<h3>Perfil de Cliente</h3>"))
        layout.addWidget(self.txt_dni)
        layout.addWidget(self.txt_nombre)
        layout.addWidget(self.txt_tel)
        layout.addWidget(self.txt_email)
        layout.addWidget(self.txt_dir)
        layout.addStretch()
        layout.addWidget(btn_guardar)

    def guardar(self):
        if not self.txt_dni.text() or not self.txt_nombre.text():
            QMessageBox.warning(self, "Error", "El DNI y Nombre son obligatorios.")
            return
            
        ex, msj = registrar_cliente(
            self.txt_dni.text(), self.txt_nombre.text(), 
            self.txt_tel.text(), self.txt_email.text(), self.txt_dir.text()
        )
        if ex:
            QMessageBox.information(self, "Éxito", msj)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", msj)