from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QComboBox, QPushButton, QLabel, QMessageBox
from src.database.controller import crear_usuario

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Empleado")
        self.setFixedSize(300, 280)
        
        layout = QVBoxLayout(self)

        self.txt_user = QLineEdit(placeholderText="Nombre de Usuario")
        self.txt_pass = QLineEdit(placeholderText="Contraseña")
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.cmb_rol = QComboBox()
        self.cmb_rol.addItems(["Cajero", "Administrador"])

        btn_guardar = QPushButton("💾 Guardar Usuario")
        btn_guardar.setObjectName("btnVenta")
        btn_guardar.clicked.connect(self.guardar)

        layout.addWidget(QLabel("<h3>Nuevo Empleado</h3>"))
        layout.addWidget(self.txt_user)
        layout.addWidget(self.txt_pass)
        layout.addWidget(QLabel("Nivel de Permisos:"))
        layout.addWidget(self.cmb_rol)
        layout.addWidget(btn_guardar)

    def guardar(self):
        if not self.txt_user.text() or not self.txt_pass.text():
            QMessageBox.warning(self, "Error", "Completa usuario y contraseña.")
            return
            
        ex, msj = crear_usuario(self.txt_user.text(), self.txt_pass.text(), self.cmb_rol.currentText())
        if ex:
            QMessageBox.information(self, "Éxito", msj)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", msj)