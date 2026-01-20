# src/database/controller.py
from sqlalchemy.orm import sessionmaker
from .models import engine, Producto

# Configuramos la sesión
Session = sessionmaker(bind=engine)

def registrar_producto(codigo, nombre, precio, stock, categoria):
    """Guarda un nuevo producto en la base de datos."""
    session = Session()
    try:
        nuevo_prod = Producto(
            codigo_barras=codigo,
            nombre=nombre,
            precio_venta=float(precio),
            stock_actual=int(stock),
            categoria=categoria
        )
        session.add(nuevo_prod)
        session.commit()
        return True, "Producto guardado con éxito"
    except Exception as e:
        session.rollback()
        return False, f"Error: {str(e)}"
    finally:
        session.close()

def obtener_todos_los_productos():
    """Recupera la lista completa de productos."""
    session = Session()
    productos = session.query(Producto).all()
    session.close()
    return productos