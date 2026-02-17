# src/database/controller.py
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_, func
from .models import engine, Producto, Venta, DetalleVenta, Perdida
import datetime
import pandas as pd

Session = sessionmaker(bind=engine)

def registrar_producto(codigo, nombre, costo, venta, stock, cat):
    session = Session()
    try:
        nuevo = Producto(codigo_barras=codigo, nombre=nombre, precio_costo=float(costo), 
                         precio_venta=float(venta), stock_actual=int(stock), categoria=cat)
        session.add(nuevo); session.commit(); return True, "Producto guardado"
    except: session.rollback(); return False, "El código de barras ya existe."
    finally: session.close()

def editar_producto(p_id, codigo, nombre, costo, venta, stock, cat):
    session = Session()
    try:
        p = session.query(Producto).filter(Producto.id == p_id).first()
        if p:
            p.codigo_barras, p.nombre, p.precio_costo = codigo, nombre, float(costo)
            p.precio_venta, p.stock_actual, p.categoria = float(venta), int(stock), cat
            session.commit(); return True, "Actualizado correctamente"
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
        return False, "Stock insuficiente"
    except: session.rollback(); return False, "Error"
    finally: session.close()

def obtener_reporte_periodo(dias=1):
    session = Session()
    limite = datetime.datetime.now() - datetime.timedelta(days=dias)
    try:
        # Ventas e Ingresos
        ventas = session.query(Venta).filter(Venta.fecha >= limite).all()
        ingresos = sum(v.total for v in ventas)
        
        # Ganancia Neta (Venta - Costo)
        detalles = session.query(DetalleVenta).join(Venta).filter(Venta.fecha >= limite).all()
        costos_ventas = sum(d.cantidad * d.precio_costo_momento for d in detalles)
        
        # Análisis de Pérdidas (en $ y lista de motivos)
        perdidas_db = session.query(Perdida, Producto).join(Producto).filter(Perdida.fecha >= limite).all()
        valor_perdidas = sum(per.cantidad * p.precio_costo for per, p in perdidas_db)
        lista_perdidas = [{'prod': p.nombre, 'cant': per.cantidad, 'motivo': per.motivo} for per, p in perdidas_db]
        
        return {
            'ingresos': ingresos,
            'ganancia': ingresos - costos_ventas,
            'operaciones': len(ventas),
            'perdidas_total_val': valor_perdidas,
            'lista_detallada_perdidas': lista_perdidas
        }
    finally: session.close()

def obtener_ventas_por_categoria(dias=1):
    """Devuelve datos para el gráfico de barras."""
    session = Session()
    limite = datetime.datetime.now() - datetime.timedelta(days=dias)
    try:
        res = session.query(Producto.categoria, func.sum(DetalleVenta.cantidad * DetalleVenta.precio_unitario))\
            .join(DetalleVenta, Producto.id == DetalleVenta.producto_id)\
            .join(Venta, Venta.id == DetalleVenta.venta_id)\
            .filter(Venta.fecha >= limite)\
            .group_by(Producto.categoria).all()
        return res
    finally: session.close()
    
def obtener_datos_grafico_completo(dias=1):
    """Obtiene ventas y pérdidas monetarias agrupadas por categoría."""
    session = Session()
    limite = datetime.datetime.now() - datetime.timedelta(days=dias)
    try:
        # 1. Ventas por categoría
        ventas_cat = session.query(Producto.categoria, func.sum(DetalleVenta.cantidad * DetalleVenta.precio_unitario))\
            .join(DetalleVenta, Producto.id == DetalleVenta.producto_id)\
            .join(Venta, Venta.id == DetalleVenta.venta_id)\
            .filter(Venta.fecha >= limite)\
            .group_by(Producto.categoria).all()

        # 2. Pérdidas por categoría (al costo)
        perdidas_cat = session.query(Producto.categoria, func.sum(Perdida.cantidad * Producto.precio_costo))\
            .join(Perdida, Producto.id == Perdida.producto_id)\
            .filter(Perdida.fecha >= limite)\
            .group_by(Producto.categoria).all()

        # Unificar datos en un diccionario
        data = {}
        for cat, monto in ventas_cat: data[cat] = {'ventas': monto, 'perdidas': 0}
        for cat, monto in perdidas_cat:
            if cat in data: data[cat]['perdidas'] = monto
            else: data[cat] = {'ventas': 0, 'perdidas': monto}
        
        return data
    finally: session.close()

def exportar_datos_excel(dias=1):
    """Extrae ventas y pérdidas a un DataFrame de Pandas."""
    session = Session()
    limite = datetime.datetime.now() - datetime.timedelta(days=dias)
    try:
        # Extraer Ventas
        query_v = session.query(Venta.fecha, Producto.nombre, DetalleVenta.cantidad, DetalleVenta.precio_unitario)\
            .join(DetalleVenta, Venta.id == DetalleVenta.venta_id)\
            .join(Producto, Producto.id == DetalleVenta.producto_id)\
            .filter(Venta.fecha >= limite).all()
        
        df_ventas = pd.DataFrame(query_v, columns=['Fecha', 'Producto', 'Cantidad', 'Precio'])
        return df_ventas
    finally: session.close()

def obtener_todos_los_productos():
    session = Session(); p = session.query(Producto).all(); session.close(); return p

def buscar_productos(t):
    session = Session(); p = session.query(Producto).filter(or_(Producto.nombre.ilike(f"%{t}%"), Producto.codigo_barras.ilike(f"%{t}%"))).all(); session.close(); return p