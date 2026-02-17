# src/database/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class Producto(Base):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True)
    codigo_barras = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    precio_costo = Column(Float, default=0.0)
    precio_venta = Column(Float, default=0.0)
    stock_actual = Column(Integer, default=0)
    categoria = Column(String(50))

class Venta(Base):
    __tablename__ = 'ventas'
    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, default=datetime.datetime.now)
    total = Column(Float, nullable=False)
    detalles = relationship("DetalleVenta", back_populates="venta")

class DetalleVenta(Base):
    __tablename__ = 'detalles_venta'
    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey('ventas.id'))
    producto_id = Column(Integer, ForeignKey('productos.id'))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    precio_costo_momento = Column(Float, default=0.0)
    venta = relationship("Venta", back_populates="detalles")

class Perdida(Base):
    __tablename__ = 'perdidas'
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey('productos.id'))
    cantidad = Column(Integer, nullable=False)
    motivo = Column(String(200))
    fecha = Column(DateTime, default=datetime.datetime.now)

engine = create_engine('sqlite:///flowgestion.db')

def inicializar_db():
    Base.metadata.create_all(engine)
    print("Base de datos de FlowGestion inicializada con éxito.")