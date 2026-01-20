from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Producto(Base):
    __tablename__ = 'productos'
    
    id = Column(Integer, primary_key=True)
    codigo_barras = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    precio_venta = Column(Float, default=0.0)
    stock_actual = Column(Integer, default=0)
    categoria = Column(String(50))

# Configuración del motor de la base de datos
engine = create_engine('sqlite:///flowgestion.db')

def inicializar_db():
    # Aquí es donde se usa el metadata para crear las tablas
    Base.metadata.create_all(engine)
    print("Base de datos de FlowGestion inicializada con éxito.")