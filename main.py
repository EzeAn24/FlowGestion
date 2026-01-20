# main.py
import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.database.models import inicializar_db # Importamos la función

def main():
    # 1. Crear la base de datos si no existe
    inicializar_db() 
    
    app = QApplication(sys.argv)
    
    with open("assets/style.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()