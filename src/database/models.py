from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class Configuracion(Base):
    __tablename__ = 'configuracion'
    id = Column(Integer, primary_key=True)
    nombre_local = Column(String(100), default="FlowGestion")
    cuit = Column(String(50), default="00-00000000-0")
    direccion = Column(String(200), default="Sin Dirección")
    telefono = Column(String(50), default="0000-000000")

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    rol = Column(String(50), nullable=False)

# --- CLIENTES CON PERFIL DE FIDELIZACIÓN ---
class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    dni = Column(String(20), unique=True, nullable=False) # Fundamental para evitar duplicados
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(50))
    email = Column(String(100)) # Para tickets y promociones
    direccion = Column(String(200))
    puntos_fidelidad = Column(Integer, default=0) # Sistema de premios
    saldo_cuenta_corriente = Column(Float, default=0.0) # Lo mantenemos por si alguna vez se necesita

class PagoCuentaCorriente(Base):
    __tablename__ = 'pagos_cc'
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.datetime.now)

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
    metodo_pago = Column(String(50), default="Efectivo")
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=True)
    
    detalles = relationship("DetalleVenta", back_populates="venta")
    cliente = relationship("Cliente")

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

class TurnoCaja(Base):
    __tablename__ = 'turno_caja'
    id = Column(Integer, primary_key=True)
    fecha_apertura = Column(DateTime, default=datetime.datetime.now)
    monto_inicial = Column(Float, default=0.0)
    fecha_cierre = Column(DateTime, nullable=True)
    monto_final_esperado = Column(Float, default=0.0)
    monto_final_real = Column(Float, default=0.0)
    estado = Column(String(20), default="Abierta")

engine = create_engine('sqlite:///flowgestion.db')

def inicializar_db():
    Base.metadata.create_all(engine)
    print("Base de datos inicializada.")