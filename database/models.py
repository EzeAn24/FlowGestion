from sqlalchemy import create_all, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class Producto(Base):
    __tablename__ = 'productos'
    
    id = Column(Integer, primary_key=True)
    codigo_barras = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    precio_venta = Column(Float, default=0.0)
    stock_actual = Column(Integer, default=0)
    categoria = Column(String(50))

# Esto crea el archivo de base de datos local (SQLite)
engine = create_engine('sqlite:///flowgestion.db')

def inicializar_db():
    Base.metadata.create_all(engine)
    print("Base de datos de FlowGestion inicializada con éxito.")