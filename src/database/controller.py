# src/database/controller.py
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_, func
from .models import engine, Producto, Venta, DetalleVenta, Perdida
import datetime

Session = sessionmaker(bind=engine)

def registrar_producto(codigo, nombre, costo, venta, stock, cat):
    session = Session()
    try:
        nuevo = Producto(codigo_barras=codigo, nombre=nombre, precio_costo=float(costo), 
                         precio_venta=float(venta), stock_actual=int(stock), categoria=cat)
        session.add(nuevo); session.commit(); return True, "Producto guardado"
    except: session.rollback(); return False, "Código ya existe"
    finally: session.close()

def editar_producto(p_id, codigo, nombre, costo, venta, stock, cat):
    session = Session()
    try:
        p = session.query(Producto).filter(Producto.id == p_id).first()
        if p:
            p.codigo_barras, p.nombre, p.precio_costo = codigo, nombre, float(costo)
            p.precio_venta, p.stock_actual, p.categoria = float(venta), int(stock), cat
            session.commit(); return True, "Actualizado"
        return False, "No encontrado"
    except Exception as e: session.rollback(); return False, str(e)
    finally: session.close()

def registrar_venta_completa(total, lista_items):
    session = Session()
    try:
        nueva_venta = Venta(total=total)
        session.add(nueva_venta); session.flush()
        for i in lista_items:
            p = session.query(Producto).filter(Producto.id == i['id']).first()
            detalle = DetalleVenta(venta_id=nueva_venta.id, producto_id=i['id'], 
                                   cantidad=i['cant'], precio_unitario=i['precio'],
                                   precio_costo_momento=p.precio_costo)
            session.add(detalle)
            p.stock_actual -= i['cant']
        session.commit(); return True
    except: session.rollback(); return False
    finally: session.close()

def registrar_perdida(p_id, cant, motivo):
    session = Session()
    try:
        p = session.query(Producto).filter(Producto.id == p_id).first()
        if p and p.stock_actual >= int(cant):
            nueva_p = Perdida(producto_id=p_id, cantidad=int(cant), motivo=motivo)
            p.stock_actual -= int(cant)
            session.add(nueva_p); session.commit(); return True, "Pérdida registrada"
        return False, "Stock insuficiente para registrar pérdida"
    except Exception as e: session.rollback(); return False, str(e)
    finally: session.close()

def obtener_reporte_periodo(dias=1):
    session = Session()
    fecha_limite = datetime.datetime.now() - datetime.timedelta(days=dias)
    try:
        ventas = session.query(Venta).filter(Venta.fecha >= fecha_limite).all()
        total_recaudado = sum(v.total for v in ventas)
        # Ganancia estimada (Venta - Costo en el momento)
        detalles = session.query(DetalleVenta).join(Venta).filter(Venta.fecha >= fecha_limite).all()
        costo_total = sum(d.cantidad * d.precio_costo_momento for d in detalles)
        
        perdidas = session.query(Perdida).filter(Perdida.fecha >= fecha_limite).all()
        valor_perdida = sum(per.cantidad * 0 # Aquí podrías multiplicar por precio_costo si te interesa
                            for per in perdidas) 
        
        return {
            'ingresos': total_recaudado,
            'ganancia': total_recaudado - costo_total,
            'operaciones': len(ventas),
            'perdidas_cont': len(perdidas)
        }
    finally: session.close()

def obtener_todos_los_productos():
    session = Session(); p = session.query(Producto).all(); session.close(); return p

def buscar_productos(t):
    session = Session(); p = session.query(Producto).filter(or_(Producto.nombre.ilike(f"%{t}%"), Producto.codigo_barras.ilike(f"%{t}%"))).all(); session.close(); return p