# src/ui/login_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from src.database.controller import verificar_login

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlowGestion - Iniciar Sesión")
        self.setFixedSize(300, 350)
        self.rol_usuario = None
        self.nombre_usuario = None

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        lbl_logo = QLabel("<h2>FlowGestion</h2>")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setStyleSheet("color: #1E293B; font-size: 24px; margin-bottom: 20px;")

        self.txt_user = QLineEdit()
        self.txt_user.setPlaceholderText("Usuario")
        self.txt_user.setStyleSheet("padding: 10px; font-size: 14px; border-radius: 5px;")
        
        self.txt_pass = QLineEdit()
        self.txt_pass.setPlaceholderText("Contraseña")
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pass.setStyleSheet("padding: 10px; font-size: 14px; border-radius: 5px;")
        self.txt_pass.returnPressed.connect(self.login)

        btn_login = QPushButton("Ingresar")
        btn_login.setObjectName("btnVenta")
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login.clicked.connect(self.login)

        layout.addWidget(lbl_logo)
        layout.addWidget(QLabel("Usuario:"))
        layout.addWidget(self.txt_user)
        layout.addWidget(QLabel("Contraseña:"))
        layout.addWidget(self.txt_pass)
        layout.addWidget(btn_login)

        # Tips temporales para el usuario
        lbl_tips = QLabel("<small>Admin: admin / 123<br>Cajero: cajero / 123</small>")
        lbl_tips.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_tips)

    def login(self):
        user = self.txt_user.text()
        pwd = self.txt_pass.text()
        exito, rol, nombre = verificar_login(user, pwd)
        
        if exito:
            self.rol_usuario = rol
            self.nombre_usuario = nombre
            self.accept()
        else:
            QMessageBox.warning(self, "Error de Acceso", "Usuario o contraseña incorrectos.")