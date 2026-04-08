from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_, func
from .models import engine, Producto, Venta, DetalleVenta, Perdida, TurnoCaja, Usuario, Configuracion, Cliente, PagoCuentaCorriente
import datetime
import pandas as pd

Session = sessionmaker(bind=engine)

# --- CLIENTES Y FIDELIZACIÓN ---
def registrar_cliente(dni, nombre, telefono, email, direccion):
    session = Session()
    try:
        nuevo = Cliente(dni=dni, nombre=nombre, telefono=telefono, email=email, direccion=direccion)
        session.add(nuevo); session.commit(); return True, "Cliente registrado exitosamente."
    except Exception as e: session.rollback(); return False, "El DNI ya se encuentra registrado."
    finally: session.close()

def obtener_clientes():
    session = Session(); c = session.query(Cliente).all(); session.close(); return c

def registrar_pago_cc(cliente_id, monto):
    session = Session()
    try:
        cliente = session.query(Cliente).filter(Cliente.id == cliente_id).first()
        if cliente and cliente.saldo_cuenta_corriente >= monto:
            cliente.saldo_cuenta_corriente -= monto
            session.add(PagoCuentaCorriente(cliente_id=cliente.id, monto=monto))
            session.commit(); return True, f"Se abonó ${monto} a la cuenta de {cliente.nombre}."
        return False, "El monto supera la deuda o el cliente no existe."
    except Exception as e: session.rollback(); return False, str(e)
    finally: session.close()

# --- CONFIGURACIÓN DEL LOCAL ---
def obtener_configuracion():
    session = Session()
    try:
        conf = session.query(Configuracion).first()
        if not conf: conf = Configuracion(); session.add(conf); session.commit()
        return {'nombre': conf.nombre_local, 'cuit': conf.cuit, 'direccion': conf.direccion, 'telefono': conf.telefono}
    finally: session.close()

def guardar_configuracion(nombre, cuit, dirc, tel):
    session = Session()
    try:
        conf = session.query(Configuracion).first()
        if not conf: conf = Configuracion(); session.add(conf)
        conf.nombre_local, conf.cuit, conf.direccion, conf.telefono = nombre, cuit, dirc, tel
        session.commit(); return True, "Datos actualizados."
    except Exception as e: session.rollback(); return False, str(e)
    finally: session.close()

# --- USUARIOS ---
def inicializar_usuarios():
    session = Session()
    try:
        if session.query(Usuario).count() == 0:
            session.add_all([Usuario(username="admin", password="123", rol="Administrador"), 
                             Usuario(username="cajero", password="123", rol="Cajero")])
            session.commit()
    finally: session.close()

def verificar_login(username, password):
    session = Session()
    try:
        user = session.query(Usuario).filter(Usuario.username == username, Usuario.password == password).first()
        if user: return True, user.rol, user.username
        return False, None, None
    finally: session.close()

def obtener_usuarios():
    session = Session(); u = session.query(Usuario).all(); session.close(); return u

def crear_usuario(user, pwd, rol):
    session = Session()
    try:
        session.add(Usuario(username=user, password=pwd, rol=rol)); session.commit(); return True, "Registrado."
    except: session.rollback(); return False, "El usuario ya existe."
    finally: session.close()

def eliminar_usuario(u_id):
    session = Session()
    try:
        u = session.query(Usuario).filter(Usuario.id == u_id).first()
        if u and u.username == "admin": return False, "No puedes eliminar al administrador."
        if u: session.delete(u); session.commit(); return True, "Eliminado."
        return False, "No encontrado."
    except: session.rollback(); return False, "Error."
    finally: session.close()

# --- CAJA ---
def estado_caja():
    session = Session(); c = session.query(TurnoCaja).filter(TurnoCaja.estado == "Abierta").first(); session.close(); return c

def abrir_caja(monto):
    session = Session()
    try: session.add(TurnoCaja(monto_inicial=float(monto))); session.commit(); return True, "Caja abierta."
    except Exception as e: session.rollback(); return False, str(e)
    finally: session.close()

def cerrar_caja(monto_real):
    session = Session()
    try:
        caja = session.query(TurnoCaja).filter(TurnoCaja.estado == "Abierta").first()
        if not caja: return False, "No hay caja abierta."
        ventas_efectivo = session.query(Venta).filter(Venta.fecha >= caja.fecha_apertura, Venta.metodo_pago == "Efectivo").all()
        pagos_cc = session.query(PagoCuentaCorriente).filter(PagoCuentaCorriente.fecha >= caja.fecha_apertura).all()
        
        total_ingresos = sum(v.total for v in ventas_efectivo) + sum(p.monto for p in pagos_cc)
        caja.fecha_cierre = datetime.datetime.now()
        caja.monto_final_esperado = caja.monto_inicial + total_ingresos
        caja.monto_final_real = float(monto_real)
        caja.estado = "Cerrada"
        session.commit()
        return True, f"Caja cerrada.\nEsperado: ${caja.monto_final_esperado:.2f}\nReal: ${caja.monto_final_real:.2f}\nDiferencia: ${(caja.monto_final_real - caja.monto_final_esperado):.2f}"
    except Exception as e: session.rollback(); return False, str(e)
    finally: session.close()

def calcular_ingresos_turno_actual():
    session = Session()
    try:
        caja = session.query(TurnoCaja).filter(TurnoCaja.estado == "Abierta").first()
        if not caja: return 0.0
        ventas_efectivo = sum(v.total for v in session.query(Venta).filter(Venta.fecha >= caja.fecha_apertura, Venta.metodo_pago == "Efectivo").all())
        pagos_cc = sum(p.monto for p in session.query(PagoCuentaCorriente).filter(PagoCuentaCorriente.fecha >= caja.fecha_apertura).all())
        return ventas_efectivo + pagos_cc
    finally: session.close()

# --- PRODUCTOS Y VENTAS ---
def registrar_producto(codigo, nombre, costo, venta, stock, cat):
    session = Session()
    try:
        session.add(Producto(codigo_barras=codigo, nombre=nombre, precio_costo=float(costo), precio_venta=float(venta), stock_actual=int(stock), categoria=cat))
        session.commit(); return True, "Producto guardado"
    except: session.rollback(); return False, "El código de barras ya existe."
    finally: session.close()

def editar_producto(p_id, codigo, nombre, costo, venta, stock, cat):
    session = Session()
    try:
        p = session.query(Producto).filter(Producto.id == p_id).first()
        if p:
            p.codigo_barras, p.nombre, p.precio_costo, p.precio_venta, p.stock_actual, p.categoria = codigo, nombre, float(costo), float(venta), int(stock), cat
            session.commit(); return True, "Actualizado"
        return False, "No encontrado"
    except Exception as e: session.rollback(); return False, str(e)
    finally: session.close()

def registrar_venta_completa(total, lista_items, metodo_pago="Efectivo", cliente_id=None):
    session = Session()
    try:
        nueva_venta = Venta(total=total, metodo_pago=metodo_pago, cliente_id=cliente_id)
        session.add(nueva_venta); session.flush()
        
        # SISTEMA DE FIDELIZACIÓN Y CUENTAS CORRIENTES
        if cliente_id:
            cliente = session.query(Cliente).filter(Cliente.id == cliente_id).first()
            if cliente:
                if metodo_pago == "Cuenta Corriente":
                    cliente.saldo_cuenta_corriente += total
                
                # Suman 1 punto por cada $1000 gastados (ajustable)
                puntos_ganados = int(total // 1000)
                cliente.puntos_fidelidad += puntos_ganados

        for i in lista_items:
            p = session.query(Producto).filter(Producto.id == i['id']).first()
            session.add(DetalleVenta(venta_id=nueva_venta.id, producto_id=i['id'], cantidad=i['cant'], precio_unitario=i['precio'], precio_costo_momento=p.precio_costo))
            p.stock_actual -= i['cant']
        session.commit(); return True
    except Exception as e: print(e); session.rollback(); return False
    finally: session.close()

def registrar_perdida(p_id, cant, motivo):
    session = Session()
    try:
        p = session.query(Producto).filter(Producto.id == p_id).first()
        if p and p.stock_actual >= int(cant):
            session.add(Perdida(producto_id=p_id, cantidad=int(cant), motivo=motivo))
            p.stock_actual -= int(cant)
            session.commit(); return True, "Registrada"
        return False, "Stock insuficiente"
    except: session.rollback(); return False, "Error"
    finally: session.close()

# --- REPORTES ---
def obtener_reporte_periodo(dias=1):
    session = Session(); lim = datetime.datetime.now() - datetime.timedelta(days=dias)
    try:
        ventas = session.query(Venta).filter(Venta.fecha >= lim).all()
        ingresos = sum(v.total for v in ventas)
        costos = sum(d.cantidad * d.precio_costo_momento for d in session.query(DetalleVenta).join(Venta).filter(Venta.fecha >= lim).all())
        p_db = session.query(Perdida, Producto).join(Producto).filter(Perdida.fecha >= lim).all()
        return {'ingresos': ingresos, 'ganancia': ingresos - costos, 'operaciones': len(ventas), 
                'perdidas_total_val': sum(per.cantidad * p.precio_costo for per, p in p_db), 
                'lista_detallada_perdidas': [{'prod': p.nombre, 'cant': per.cantidad, 'motivo': per.motivo} for per, p in p_db]}
    finally: session.close()

def obtener_datos_grafico_completo(dias=1):
    session = Session(); lim = datetime.datetime.now() - datetime.timedelta(days=dias)
    try:
        v_cat = session.query(Producto.categoria, func.sum(DetalleVenta.cantidad * DetalleVenta.precio_unitario)).join(DetalleVenta, Producto.id == DetalleVenta.producto_id).join(Venta, Venta.id == DetalleVenta.venta_id).filter(Venta.fecha >= lim).group_by(Producto.categoria).all()
        p_cat = session.query(Producto.categoria, func.sum(Perdida.cantidad * Producto.precio_costo)).join(Perdida, Producto.id == Perdida.producto_id).filter(Perdida.fecha >= lim).group_by(Producto.categoria).all()
        data = {}
        for cat, m in v_cat: data[cat] = {'ventas': m, 'perdidas': 0}
        for cat, m in p_cat:
            if cat in data: data[cat]['perdidas'] = m
            else: data[cat] = {'ventas': 0, 'perdidas': m}
        return data
    finally: session.close()

def exportar_datos_excel(dias=1):
    session = Session(); lim = datetime.datetime.now() - datetime.timedelta(days=dias)
    try:
        q = session.query(Venta.fecha, Producto.nombre, DetalleVenta.cantidad, DetalleVenta.precio_unitario, Venta.metodo_pago)\
            .join(DetalleVenta, Venta.id == DetalleVenta.venta_id).join(Producto, Producto.id == DetalleVenta.producto_id)\
            .filter(Venta.fecha >= lim).all()
        return pd.DataFrame(q, columns=['Fecha', 'Producto', 'Cantidad', 'Precio', 'Pago'])
    finally: session.close()

def obtener_todos_los_productos():
    session = Session(); p = session.query(Producto).all(); session.close(); return p

def buscar_productos(t):
    session = Session(); p = session.query(Producto).filter(or_(Producto.nombre.ilike(f"%{t}%"), Producto.codigo_barras.ilike(f"%{t}%"))).all(); session.close(); return p