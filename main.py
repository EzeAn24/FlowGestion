# main.py
import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.login_dialog import LoginDialog # NUEVO IMPORT
from src.database.models import inicializar_db
from src.database.controller import inicializar_usuarios # NUEVO IMPORT

def main():
    inicializar_db()
    inicializar_usuarios() # Crea los usuarios por defecto si no existen
    
    app = QApplication(sys.argv)
    
    try:
        with open("assets/style.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Advertencia: No se encontró style.qss")

    # Mostrar primero la ventana de Login
    login = LoginDialog()
    if login.exec() == 1: # Si el login es exitoso (Accepted)
        # Pasamos los datos del usuario a la ventana principal
        window = MainWindow(usuario=login.nombre_usuario, rol=login.rol_usuario)
        window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()