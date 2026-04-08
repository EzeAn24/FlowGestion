import os
import datetime
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QColor, QFont
from .add_product_dialog import AddProductDialog
from .add_user_dialog import AddUserDialog
from .add_client_dialog import AddClientDialog
from src.database.controller import *
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# LIBRERÍAS PARA EL TICKET PDF
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self, usuario="Admin", rol="Administrador"):
        super().__init__()
        self.usuario_actual = usuario
        self.rol_actual = rol
        
        self.setWindowTitle(f"FlowGestion - {self.rol_actual}")
        self.resize(1200, 850)
        main_widget = QWidget(); self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget); layout.setContentsMargins(0,0,0,0)
        
        sidebar = QFrame(); sidebar.setObjectName("Sidebar")
        s_layout = QVBoxLayout(sidebar); s_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        title = QLabel("FlowGestion"); title.setStyleSheet("color: white; font-size: 22px; font-weight: bold; margin: 20px 20px 5px 20px;")
        lbl_user = QLabel(f"👤 {self.usuario_actual}\n({self.rol_actual})")
        lbl_user.setStyleSheet("color: #94A3B8; font-size: 14px; margin: 0px 20px 20px 20px;")
        s_layout.addWidget(title); s_layout.addWidget(lbl_user)
        
        btns = [("🛒 Ventas", 0), ("👥 Clientes", 1), ("📦 Stock", 2), ("📊 Reportes", 3), ("💰 Caja", 4), ("⚙️ Ajustes", 5)]
        self.nav_btns = []
        for text, index in btns:
            b = QPushButton(text); b.clicked.connect(lambda ch, i=index: self.cambiar_pagina(i))
            s_layout.addWidget(b); self.nav_btns.append(b)
            
        if self.rol_actual == "Cajero":
            self.nav_btns[2].hide(); self.nav_btns[3].hide(); self.nav_btns[5].hide()

        self.stack = QStackedWidget(); self.stack.setObjectName("MainContent")
        self.init_page_ventas(); self.init_page_clientes(); self.init_page_inventario()
        self.init_page_reportes(); self.init_page_caja(); self.init_page_ajustes()
        layout.addWidget(sidebar); layout.addWidget(self.stack)

    def cambiar_pagina(self, i):
        self.stack.setCurrentIndex(i)
        if i == 0: self.actualizar_combo_clientes()
        if i == 1: self.actualizar_tabla_clientes()
        if i == 3 and self.rol_actual == "Administrador": self.cargar_reportes()
        if i == 4: self.actualizar_vista_caja()
        if i == 5 and self.rol_actual == "Administrador": self.cargar_usuarios()

    def actualizar_completer(self):
        productos = obtener_todos_los_productos()
        lista_busqueda = [f"{p.codigo_barras} - {p.nombre}" for p in productos]
        model = QStringListModel(lista_busqueda)
        self.completer.setModel(model)

    def actualizar_combo_clientes(self):
        self.cmb_cliente.clear()
        self.cmb_cliente.addItem("Consumidor Final", None)
        for c in obtener_clientes(): self.cmb_cliente.addItem(c.nombre, c.id)

    # --- VENTAS ---
    def init_page_ventas(self):
        page = QWidget(); layout = QVBoxLayout(page)
        h_opciones = QHBoxLayout()
        self.cmb_cliente = QComboBox()
        self.cmb_pago = QComboBox(); self.cmb_pago.addItems(["Efectivo", "Cuenta Corriente"])
        h_opciones.addWidget(QLabel("<b>Cliente:</b>")); h_opciones.addWidget(self.cmb_cliente)
        h_opciones.addWidget(QLabel("<b>Forma de Pago:</b>")); h_opciones.addWidget(self.cmb_pago)
        h_opciones.addStretch()

        self.txt_scan = QLineEdit(); self.txt_scan.setPlaceholderText("🔍 Escanear o escribir producto...")
        self.txt_scan.setStyleSheet("padding: 15px; font-size: 16px; border: 2px solid #CBD5E1; border-radius: 8px;")
        self.completer = QCompleter(); self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive); self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.txt_scan.setCompleter(self.completer); self.txt_scan.returnPressed.connect(self.agregar_carrito)

        self.tabla_cart = QTableWidget(); self.tabla_cart.setColumnCount(5)
        self.tabla_cart.setHorizontalHeaderLabels(["ID", "Producto", "Precio", "Cant.", "Subtotal"])
        self.tabla_cart.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_cart.cellChanged.connect(self.recalc_fila)
        
        footer = QHBoxLayout()
        self.btn_del = QPushButton("🗑️ Quitar"); self.btn_del.setObjectName("btnEliminar"); self.btn_del.clicked.connect(self.borrar_item)
        self.lbl_tot = QLabel("Total: $ 0.00"); self.lbl_tot.setStyleSheet("font-size: 28px; font-weight: bold;")
        btn_pay = QPushButton("💳 COBRAR Y TICKET"); btn_pay.setObjectName("btnVenta"); btn_pay.clicked.connect(self.cobrar)
        footer.addWidget(self.btn_del); footer.addStretch(); footer.addWidget(self.lbl_tot); footer.addWidget(btn_pay)
        
        layout.addWidget(QLabel("<h1>Caja Registradora</h1>")); layout.addLayout(h_opciones)
        layout.addWidget(self.txt_scan); layout.addWidget(self.tabla_cart); layout.addLayout(footer)
        self.stack.addWidget(page); self.actualizar_combo_clientes()

    def agregar_carrito(self):
        txt = self.txt_scan.text()
        if not txt: return
        codigo = txt.split(" - ")[0] if " - " in txt else txt
        prods = buscar_productos(codigo)
        if not prods: QMessageBox.warning(self, "Aviso", "No encontrado."); return
        p = prods[0]
        if p.stock_actual <= 0: QMessageBox.warning(self, "Sin Stock", f"No hay de: {p.nombre}"); return

        r = self.tabla_cart.rowCount(); self.tabla_cart.insertRow(r)
        self.tabla_cart.blockSignals(True)
        for i, v in enumerate([str(p.id), p.nombre, str(p.precio_venta), "1", str(p.precio_venta)]):
            item = QTableWidgetItem(v)
            if i != 3: item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.tabla_cart.setItem(r, i, item)
        self.tabla_cart.blockSignals(False); self.txt_scan.clear(); self.recalc_total()

    def recalc_fila(self, r, c):
        if c == 3:
            self.tabla_cart.blockSignals(True)
            try:
                sub = int(self.tabla_cart.item(r, 3).text()) * float(self.tabla_cart.item(r, 2).text())
                self.tabla_cart.setItem(r, 4, QTableWidgetItem(f"{sub:.2f}"))
            except: self.tabla_cart.setItem(r, 3, QTableWidgetItem("1"))
            self.tabla_cart.blockSignals(False); self.recalc_total()

    def recalc_total(self):
        self.lbl_tot.setText(f"Total: $ {sum(float(self.tabla_cart.item(r, 4).text()) for r in range(self.tabla_cart.rowCount())):.2f}")

    def borrar_item(self):
        if self.tabla_cart.currentRow() >= 0: self.tabla_cart.removeRow(self.tabla_cart.currentRow()); self.recalc_total()

    # --- GENERADOR DE TICKET PDF (NUEVO) ---
    def generar_ticket_pdf(self, filename, conf, usuario, cliente, metodo, items, total):
        # Calculamos la altura dinámica según la cantidad de items
        height = (80 + len(items) * 5) * mm 
        width = 80 * mm # Formato clásico de ticketera térmica
        
        c = canvas.Canvas(filename, pagesize=(width, height))
        y = height - 10 * mm
        
        # Cabecera del Local
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width/2, y, conf['nombre'].upper())
        y -= 6 * mm
        c.setFont("Helvetica", 9)
        c.drawCentredString(width/2, y, f"CUIT: {conf['cuit']}")
        y -= 4 * mm
        c.drawCentredString(width/2, y, f"Dir: {conf['direccion']}")
        y -= 4 * mm
        c.drawCentredString(width/2, y, f"Tel: {conf['telefono']}")
        y -= 6 * mm
        c.line(5*mm, y, width - 5*mm, y)
        y -= 5 * mm
        
        # Datos de la Operación
        c.setFont("Helvetica", 8)
        c.drawString(5*mm, y, f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
        y -= 4 * mm
        c.drawString(5*mm, y, f"Cajero: {usuario}")
        y -= 4 * mm
        c.drawString(5*mm, y, f"Cliente: {cliente}")
        y -= 4 * mm
        c.drawString(5*mm, y, f"Pago: {metodo}")
        y -= 6 * mm
        c.line(5*mm, y, width - 5*mm, y)
        y -= 5 * mm
        
        # Encabezado Tabla
        c.setFont("Helvetica-Bold", 8)
        c.drawString(5*mm, y, "CANT")
        c.drawString(15*mm, y, "PRODUCTO")
        c.drawRightString(width - 5*mm, y, "SUBTOTAL")
        y -= 5 * mm
        
        # Listado de Productos
        c.setFont("Helvetica", 8)
        for item in items:
            c.drawString(5*mm, y, str(item['cant']))
            nom = item['nombre'][:20] # Truncamos si es muy largo
            c.drawString(15*mm, y, nom)
            c.drawRightString(width - 5*mm, y, f"${item['subtotal']:.2f}")
            y -= 4 * mm
            
        y -= 2 * mm
        c.line(5*mm, y, width - 5*mm, y)
        y -= 6 * mm
        
        # Totales
        c.setFont("Helvetica-Bold", 12)
        c.drawString(5*mm, y, "TOTAL:")
        c.drawRightString(width - 5*mm, y, f"${total:.2f}")
        y -= 10 * mm
        
        # Mensaje de Despedida
        c.setFont("Helvetica", 8)
        c.drawCentredString(width/2, y, "¡Gracias por su compra!")
        
        c.save()

    def cobrar(self):
        if not estado_caja():
            QMessageBox.warning(self, "Caja Cerrada", "Debes abrir la caja."); self.stack.setCurrentIndex(4); return
        if self.tabla_cart.rowCount() == 0: return
        
        cliente_id = self.cmb_cliente.currentData()
        metodo = self.cmb_pago.currentText()
        nombre_cliente = self.cmb_cliente.currentText()

        if metodo == "Cuenta Corriente" and cliente_id is None:
            QMessageBox.warning(self, "Atención", "Para fiar, debes seleccionar a un Cliente registrado.")
            return

        conf = obtener_configuracion()
        items_db = []
        items_pdf = []
        
        for r in range(self.tabla_cart.rowCount()):
            p_id, nom = int(self.tabla_cart.item(r, 0).text()), self.tabla_cart.item(r, 1).text()
            pre, can = float(self.tabla_cart.item(r, 2).text()), int(self.tabla_cart.item(r, 3).text())
            sub = float(self.tabla_cart.item(r, 4).text())
            
            items_db.append({'id': p_id, 'cant': can, 'precio': pre})
            items_pdf.append({'nombre': nom, 'cant': can, 'subtotal': sub})
        
        total_num = float(self.lbl_tot.text().replace("Total: $ ", ""))
        if registrar_venta_completa(total_num, items_db, metodo_pago=metodo, cliente_id=cliente_id):
            os.makedirs("tickets", exist_ok=True)
            fname = f"tickets/ticket_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # LLAMADA A LA GENERACIÓN DE PDF
            self.generar_ticket_pdf(fname, conf, self.usuario_actual, nombre_cliente, metodo, items_pdf, total_num)
            
            QMessageBox.information(self, "Éxito", f"Venta registrada. PDF generado en: {fname}")
            self.tabla_cart.setRowCount(0); self.recalc_total(); self.actualizar_tabla(); self.actualizar_vista_caja()

    # --- CLIENTES ---
    def init_page_clientes(self):
        page = QWidget(); layout = QVBoxLayout(page)
        h = QHBoxLayout()
        btn_pagar = QPushButton("💸 Cobrar Deuda"); btn_pagar.clicked.connect(self.cobrar_deuda_cliente)
        btn_nv = QPushButton("+ Nuevo Cliente"); btn_nv.setObjectName("btnVenta"); btn_nv.clicked.connect(self.abrir_new_cliente)
        h.addWidget(QLabel("<h3>Base de Datos de Clientes</h3>")); h.addStretch(); h.addWidget(btn_pagar); h.addWidget(btn_nv)
        self.t_cli = QTableWidget(); self.t_cli.setColumnCount(6)
        self.t_cli.setHorizontalHeaderLabels(["ID", "DNI", "Nombre", "Email", "Puntos ⭐", "Deuda"])
        self.t_cli.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.t_cli.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(QLabel("<h1>👥 Fidelización y Clientes</h1>")); layout.addLayout(h); layout.addWidget(self.t_cli)
        self.stack.addWidget(page)

    def actualizar_tabla_clientes(self):
        self.t_cli.setRowCount(0)
        for c in obtener_clientes():
            r = self.t_cli.rowCount(); self.t_cli.insertRow(r)
            for i, v in enumerate([str(c.id), c.dni, c.nombre, c.email or "-", str(c.puntos_fidelidad), f"${c.saldo_cuenta_corriente:.2f}"]):
                item = QTableWidgetItem(v); item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                if i == 4 and c.puntos_fidelidad > 0:
                    item.setForeground(QColor("#D97706")); item.setFont(QFont("Arial", weight=QFont.Weight.Bold))
                if i == 5 and c.saldo_cuenta_corriente > 0: item.setForeground(QColor("#B91C1C"))
                self.t_cli.setItem(r, i, item)

    def abrir_new_cliente(self):
        if AddClientDialog(self).exec(): self.actualizar_tabla_clientes(); self.actualizar_combo_clientes()

    def cobrar_deuda_cliente(self):
        r = self.t_cli.currentRow()
        if r < 0: QMessageBox.warning(self, "Atención", "Seleccioná un cliente de la lista."); return
        c_id, nombre = int(self.t_cli.item(r, 0).text()), self.t_cli.item(r, 2).text()
        saldo = float(self.t_cli.item(r, 5).text().replace("$", ""))
        if saldo <= 0: QMessageBox.information(self, "Aviso", f"{nombre} no tiene deudas."); return
        if not estado_caja(): QMessageBox.warning(self, "Caja Cerrada", "Debés abrir la caja para ingresar dinero."); return

        monto, ok = QInputDialog.getDouble(self, "Cobrar Deuda", f"Saldo de {nombre}: ${saldo:.2f}\n¿Cuánto abona ahora?", 0, 0, saldo, 2)
        if ok and monto > 0:
            ex, msj = registrar_pago_cc(c_id, monto)
            if ex: QMessageBox.information(self, "Pago", msj); self.actualizar_tabla_clientes(); self.actualizar_vista_caja()
            else: QMessageBox.warning(self, "Error", msj)

    # --- INVENTARIO ---
    def init_page_inventario(self):
        page = QWidget(); layout = QVBoxLayout(page)
        h = QHBoxLayout()
        btn_per = QPushButton("⚠️ Pérdida"); btn_per.clicked.connect(self.abrir_perdida)
        btn_ed = QPushButton("✏️ Editar"); btn_ed.clicked.connect(self.abrir_edit)
        btn_nv = QPushButton("+ Nuevo"); btn_nv.setObjectName("btnVenta"); btn_nv.clicked.connect(self.abrir_new)
        h.addWidget(QLabel("<h3>Stock</h3>")); h.addStretch(); h.addWidget(btn_per); h.addWidget(btn_ed); h.addWidget(btn_nv)
        self.t_inv = QTableWidget(); self.t_inv.setColumnCount(7)
        self.t_inv.setHorizontalHeaderLabels(["ID", "Código", "Nombre", "Costo", "Venta", "Stock", "Cat"])
        self.t_inv.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.t_inv.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addLayout(h); layout.addWidget(self.t_inv); self.stack.addWidget(page); self.actualizar_tabla()

    def actualizar_tabla(self):
        self.t_inv.setRowCount(0)
        for p in obtener_todos_los_productos():
            r = self.t_inv.rowCount(); self.t_inv.insertRow(r)
            for i, v in enumerate([str(p.id), p.codigo_barras, p.nombre, str(p.precio_costo), str(p.precio_venta), str(p.stock_actual), p.categoria]):
                item = QTableWidgetItem(v); item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                if p.stock_actual <= 5:
                    item.setBackground(QColor("#FECACA")); item.setForeground(QColor("#B91C1C"))
                self.t_inv.setItem(r, i, item)
        self.actualizar_completer()

    def abrir_new(self):
        if AddProductDialog(self).exec(): self.actualizar_tabla()
    def abrir_edit(self):
        r = self.t_inv.currentRow()
        if r >= 0:
            diag = AddProductDialog(self, int(self.t_inv.item(r,0).text()))
            fields = [diag.txt_codigo, diag.txt_nombre, diag.txt_costo, diag.txt_venta, diag.txt_stock, diag.txt_cat]
            for i, f in enumerate(fields): f.setText(self.t_inv.item(r, i+1).text().replace("$ ", ""))
            if diag.exec(): self.actualizar_tabla()
    def abrir_perdida(self):
        r = self.t_inv.currentRow()
        if r < 0: return
        p_id = int(self.t_inv.item(r, 0).text())
        can, ok = QInputDialog.getInt(self, "Pérdida", f"Cant. de {self.t_inv.item(r, 2).text()}:")
        if ok:
            mot, ok_m = QInputDialog.getText(self, "Motivo", "Razón:")
            if ok_m: registrar_perdida(p_id, can, mot); self.actualizar_tabla()

    # --- REPORTES ---
    def init_page_reportes(self):
        page = QWidget(); layout = QVBoxLayout(page)
        header = QHBoxLayout()
        self.combo_per = QComboBox(); self.combo_per.addItems(["Hoy", "30 días", "Año"]); self.combo_per.currentIndexChanged.connect(self.cargar_reportes)
        btn_ex = QPushButton("📁 Excel"); btn_ex.clicked.connect(self.exportar_excel)
        header.addWidget(self.combo_per); header.addStretch(); header.addWidget(btn_ex)
        self.rep_data = QLabel("Resumen..."); self.rep_data.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B;")
        self.canvas = MplCanvas(self, width=5, height=3)
        self.tabla_per = QTableWidget(); self.tabla_per.setColumnCount(3); self.tabla_per.setHorizontalHeaderLabels(["Producto", "Cant", "Motivo"])
        self.tabla_per.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.tabla_per.setFixedHeight(150)
        layout.addWidget(QLabel("<h1>📊 Análisis de Negocio</h1>")); layout.addLayout(header); layout.addWidget(self.rep_data)
        layout.addWidget(QLabel("<h3>Ventas (Verde) vs Pérdidas (Rojo)</h3>")); layout.addWidget(self.canvas)
        layout.addWidget(QLabel("<h3>⚠️ Historial de Pérdidas</h3>")); layout.addWidget(self.tabla_per); self.stack.addWidget(page)

    def cargar_reportes(self):
        idx = self.combo_per.currentIndex(); dias = 1 if idx == 0 else (30 if idx == 1 else 365)
        res = obtener_reporte_periodo(dias); g_data = obtener_datos_grafico_completo(dias)
        self.rep_data.setText(f"💰 Ingresos: $ {res['ingresos']:.2f} | 📈 Ganancia: $ {res['ganancia']:.2f} | ⚠️ Pérdidas $: $ {res['perdidas_total_val']:.2f}")
        self.tabla_per.setRowCount(0)
        for p in res['lista_detallada_perdidas']:
            r = self.tabla_per.rowCount(); self.tabla_per.insertRow(r)
            self.tabla_per.setItem(r, 0, QTableWidgetItem(p['prod'])); self.tabla_per.setItem(r, 1, QTableWidgetItem(str(p['cant']))); self.tabla_per.setItem(r, 2, QTableWidgetItem(p['motivo']))
        self.canvas.axes.cla(); cats = list(g_data.keys()); v_vals = [g_data[c]['ventas'] for c in cats]; p_vals = [g_data[c]['perdidas'] for c in cats]
        if cats:
            x = np.arange(len(cats)); w = 0.35
            self.canvas.axes.bar(x - w/2, v_vals, w, label='Ventas', color='#22C55E')
            self.canvas.axes.bar(x + w/2, p_vals, w, label='Pérdidas', color='#EF4444')
            self.canvas.axes.set_xticks(x); self.canvas.axes.set_xticklabels(cats); self.canvas.axes.legend()
        self.canvas.draw()

    def exportar_excel(self):
        idx = self.combo_per.currentIndex(); dias = 1 if idx == 0 else (30 if idx == 1 else 365)
        df = exportar_datos_excel(dias)
        if not df.empty:
            os.makedirs("reportes", exist_ok=True)
            fname = f"reportes/reporte_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            df.to_excel(fname, index=False); QMessageBox.information(self, "Éxito", f"Excel guardado en: {fname}")

    # --- CAJA ---
    def init_page_caja(self):
        self.page_caja = QWidget(); self.layout_caja = QVBoxLayout(self.page_caja)
        self.stack.addWidget(self.page_caja); self.actualizar_vista_caja()

    def actualizar_vista_caja(self):
        for i in reversed(range(self.layout_caja.count())): 
            widget = self.layout_caja.itemAt(i).widget()
            if widget: widget.deleteLater()
            else:
                l = self.layout_caja.itemAt(i).layout()
                if l:
                    for j in reversed(range(l.count())):
                        w = l.itemAt(j).widget()
                        if w: w.deleteLater()
                    l.deleteLater()
        caja_actual = estado_caja()
        
        if not caja_actual:
            lbl_tit = QLabel("<h1>🔴 CAJA CERRADA</h1>"); lbl_tit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.txt_monto_inicial = QLineEdit(); self.txt_monto_inicial.setPlaceholderText("Ingresar Cambio Inicial ($)...")
            self.txt_monto_inicial.setFixedWidth(350); self.txt_monto_inicial.setStyleSheet("padding: 15px; font-size: 16px;")
            btn_abrir = QPushButton("🔓 ABRIR CAJA"); btn_abrir.setObjectName("btnVenta"); btn_abrir.setFixedWidth(350); btn_abrir.clicked.connect(self.procesar_apertura)
            c1 = QHBoxLayout(); c1.addStretch(); c1.addWidget(self.txt_monto_inicial); c1.addStretch()
            c2 = QHBoxLayout(); c2.addStretch(); c2.addWidget(btn_abrir); c2.addStretch()
            self.layout_caja.addStretch(); self.layout_caja.addWidget(lbl_tit); self.layout_caja.addLayout(c1); self.layout_caja.addLayout(c2); self.layout_caja.addStretch()
        else:
            lbl_tit = QLabel("<h1>🟢 CAJA ABIERTA</h1>"); lbl_tit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vt = calcular_ingresos_turno_actual(); esperado = caja_actual.monto_inicial + vt
            info = QLabel(f"<b>Fondo Inicial:</b> ${caja_actual.monto_inicial:.2f}<br><b>Ingresos Efectivo:</b> ${vt:.2f}<br><b>TOTAL ESPERADO: <span style='color:#22C55E'>${esperado:.2f}</span></b>")
            info.setStyleSheet("font-size: 20px; line-height: 40px;"); info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.txt_monto_real = QLineEdit(); self.txt_monto_real.setPlaceholderText("¿Efectivo físico real?"); self.txt_monto_real.setFixedWidth(350); self.txt_monto_real.setStyleSheet("padding: 15px; font-size: 16px;")
            btn_cerrar = QPushButton("🔒 CERRAR TURNO"); btn_cerrar.setObjectName("btnEliminar"); btn_cerrar.setFixedWidth(350); btn_cerrar.clicked.connect(self.procesar_cierre)
            c1 = QHBoxLayout(); c1.addStretch(); c1.addWidget(self.txt_monto_real); c1.addStretch()
            c2 = QHBoxLayout(); c2.addStretch(); c2.addWidget(btn_cerrar); c2.addStretch()
            self.layout_caja.addStretch(); self.layout_caja.addWidget(lbl_tit); self.layout_caja.addWidget(info); self.layout_caja.addLayout(c1); self.layout_caja.addLayout(c2); self.layout_caja.addStretch()

    def procesar_apertura(self):
        try:
            ex, msj = abrir_caja(float(self.txt_monto_inicial.text() or "0"))
            if ex: self.actualizar_vista_caja()
            else: QMessageBox.warning(self, "Error", msj)
        except: QMessageBox.warning(self, "Error", "Monto inválido")

    def procesar_cierre(self):
        if not self.txt_monto_real.text(): QMessageBox.warning(self, "Atención", "Ingresa el dinero físico."); return
        try:
            ex, msj = cerrar_caja(float(self.txt_monto_real.text()))
            if ex: QMessageBox.information(self, "Cierre", msj); self.actualizar_vista_caja()
            else: QMessageBox.warning(self, "Error", msj)
        except: QMessageBox.warning(self, "Error", "Monto inválido")

    # --- AJUSTES ---
    def init_page_ajustes(self):
        page = QWidget(); layout = QVBoxLayout(page)
        gb_local = QGroupBox("🏛️ Datos Fiscales del Comercio"); gb_local.setStyleSheet("font-size: 16px; font-weight: bold;")
        l_local = QGridLayout(gb_local)
        self.txt_nom_loc = QLineEdit(); self.txt_cuit = QLineEdit(); self.txt_dir_loc = QLineEdit(); self.txt_tel_loc = QLineEdit()
        conf = obtener_configuracion()
        self.txt_nom_loc.setText(conf['nombre']); self.txt_cuit.setText(conf['cuit']); self.txt_dir_loc.setText(conf['direccion']); self.txt_tel_loc.setText(conf['telefono'])
        l_local.addWidget(QLabel("Nombre Fantasía:"), 0, 0); l_local.addWidget(self.txt_nom_loc, 0, 1)
        l_local.addWidget(QLabel("CUIT:"), 0, 2); l_local.addWidget(self.txt_cuit, 0, 3)
        l_local.addWidget(QLabel("Dirección:"), 1, 0); l_local.addWidget(self.txt_dir_loc, 1, 1)
        l_local.addWidget(QLabel("Teléfono:"), 1, 2); l_local.addWidget(self.txt_tel_loc, 1, 3)
        btn_guardar_local = QPushButton("💾 Guardar Cambios"); btn_guardar_local.setObjectName("btnVenta"); btn_guardar_local.clicked.connect(self.guardar_config_local)
        l_local.addWidget(btn_guardar_local, 2, 3)

        gb_emp = QGroupBox("👥 Gestión de Usuarios"); gb_emp.setStyleSheet("font-size: 16px; font-weight: bold;")
        l_emp = QVBoxLayout(gb_emp)
        h_btn_emp = QHBoxLayout()
        btn_nuevo_emp = QPushButton("+ Nuevo Usuario"); btn_nuevo_emp.setObjectName("btnVenta"); btn_nuevo_emp.clicked.connect(self.abrir_add_usuario)
        btn_borrar_emp = QPushButton("🗑️ Eliminar Seleccionado"); btn_borrar_emp.setObjectName("btnEliminar"); btn_borrar_emp.clicked.connect(self.borrar_usuario)
        h_btn_emp.addStretch(); h_btn_emp.addWidget(btn_borrar_emp); h_btn_emp.addWidget(btn_nuevo_emp)
        self.tabla_usuarios = QTableWidget(); self.tabla_usuarios.setColumnCount(3); self.tabla_usuarios.setHorizontalHeaderLabels(["ID", "Usuario", "Rol"])
        self.tabla_usuarios.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.tabla_usuarios.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows); self.tabla_usuarios.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        l_emp.addLayout(h_btn_emp); l_emp.addWidget(self.tabla_usuarios)
        layout.addWidget(QLabel("<h1>⚙️ Panel de Configuración</h1>")); layout.addWidget(gb_local); layout.addWidget(gb_emp); self.stack.addWidget(page)

    def guardar_config_local(self):
        ex, msj = guardar_configuracion(self.txt_nom_loc.text(), self.txt_cuit.text(), self.txt_dir_loc.text(), self.txt_tel_loc.text())
        if ex: QMessageBox.information(self, "Éxito", msj)
    def cargar_usuarios(self):
        self.tabla_usuarios.setRowCount(0)
        for u in obtener_usuarios():
            r = self.tabla_usuarios.rowCount(); self.tabla_usuarios.insertRow(r)
            self.tabla_usuarios.setItem(r, 0, QTableWidgetItem(str(u.id))); self.tabla_usuarios.setItem(r, 1, QTableWidgetItem(u.username)); self.tabla_usuarios.setItem(r, 2, QTableWidgetItem(u.rol))
    def abrir_add_usuario(self):
        if AddUserDialog(self).exec(): self.cargar_usuarios()
    def borrar_usuario(self):
        row = self.tabla_usuarios.currentRow()
        if row < 0: return
        ex, msj = eliminar_usuario(int(self.tabla_usuarios.item(row, 0).text()))
        if ex: QMessageBox.information(self, "Éxito", msj); self.cargar_usuarios()
        else: QMessageBox.warning(self, "Atención", msj)