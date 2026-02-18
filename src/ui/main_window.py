import datetime
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from .add_product_dialog import AddProductDialog
from src.database.controller import *
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlowGestion"); self.resize(1200, 850)
        main_widget = QWidget(); self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget); layout.setContentsMargins(0,0,0,0)
        sidebar = QFrame(); sidebar.setObjectName("Sidebar")
        s_layout = QVBoxLayout(sidebar); s_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        title = QLabel("FlowGestion"); title.setStyleSheet("color: white; font-size: 22px; font-weight: bold; margin: 20px;")
        s_layout.addWidget(title)
        btns = [("🛒 Ventas", 0), ("📦 Stock", 1), ("📊 Reportes", 2)]
        for text, index in btns:
            b = QPushButton(text); b.clicked.connect(lambda ch, i=index: self.cambiar_pagina(i))
            s_layout.addWidget(b)
        self.stack = QStackedWidget(); self.stack.setObjectName("MainContent")
        self.init_page_ventas(); self.init_page_inventario(); self.init_page_reportes()
        layout.addWidget(sidebar); layout.addWidget(self.stack)

    def cambiar_pagina(self, i):
        self.stack.setCurrentIndex(i)
        if i == 2: self.cargar_reportes()

    def init_page_ventas(self):
        page = QWidget(); layout = QVBoxLayout(page)
        self.txt_scan = QLineEdit(); self.txt_scan.setPlaceholderText("Escanear código..."); self.txt_scan.returnPressed.connect(self.agregar_carrito)
        self.tabla_cart = QTableWidget(); self.tabla_cart.setColumnCount(5)
        self.tabla_cart.setHorizontalHeaderLabels(["ID", "Producto", "Precio", "Cant.", "Subtotal"])
        self.tabla_cart.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_cart.cellChanged.connect(self.recalc_fila)
        footer = QHBoxLayout()
        self.btn_del = QPushButton("🗑️ Quitar"); self.btn_del.setObjectName("btnEliminar"); self.btn_del.clicked.connect(self.borrar_item)
        self.lbl_tot = QLabel("Total: $ 0.00"); self.lbl_tot.setStyleSheet("font-size: 28px; font-weight: bold;")
        btn_pay = QPushButton("💳 COBRAR Y TICKET"); btn_pay.setObjectName("btnVenta"); btn_pay.clicked.connect(self.cobrar)
        footer.addWidget(self.btn_del); footer.addStretch(); footer.addWidget(self.lbl_tot); footer.addWidget(btn_pay)
        layout.addWidget(QLabel("<h1>Caja Registradora</h1>")); layout.addWidget(self.txt_scan); layout.addWidget(self.tabla_cart); layout.addLayout(footer)
        self.stack.addWidget(page)

    def agregar_carrito(self):
        prods = buscar_productos(self.txt_scan.text())
        if not prods or prods[0].stock_actual <= 0: return
        p = prods[0]; r = self.tabla_cart.rowCount(); self.tabla_cart.insertRow(r)
        self.tabla_cart.blockSignals(True)
        items = [str(p.id), p.nombre, str(p.precio_venta), "1", str(p.precio_venta)]
        for i, v in enumerate(items):
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
        t = sum(float(self.tabla_cart.item(r, 4).text()) for r in range(self.tabla_cart.rowCount()))
        self.lbl_tot.setText(f"Total: $ {t:.2f}")

    def borrar_item(self):
        if self.tabla_cart.currentRow() >= 0: self.tabla_cart.removeRow(self.tabla_cart.currentRow()); self.recalc_total()

    def cobrar(self):
        if self.tabla_cart.rowCount() == 0: return
        items = []
        ticket = "--- FLOWGESTION TICKET ---\n" + f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n--------------------------\n"
        for r in range(self.tabla_cart.rowCount()):
            p_id, nom = int(self.tabla_cart.item(r, 0).text()), self.tabla_cart.item(r, 1).text()
            pre, can = float(self.tabla_cart.item(r, 2).text()), int(self.tabla_cart.item(r, 3).text())
            sub = self.tabla_cart.item(r, 4).text()
            items.append({'id': p_id, 'cant': can, 'precio': pre}); ticket += f"{nom} x{can}: ${sub}\n"
        ticket += f"--------------------------\n{self.lbl_tot.text()}\nGracias por su compra!"
        if registrar_venta_completa(float(self.lbl_tot.text().replace("Total: $ ", "")), items):
            filename = f"ticket_{datetime.datetime.now().timestamp()}.txt"
            with open(filename, "w") as f: f.write(ticket)
            QMessageBox.information(self, "Éxito", f"Venta cobrada. Ticket: {filename}")
            self.tabla_cart.setRowCount(0); self.recalc_total(); self.actualizar_tabla()

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
        prods = obtener_todos_los_productos(); self.t_inv.setRowCount(0)
        for p in prods:
            r = self.t_inv.rowCount(); self.t_inv.insertRow(r)
            d = [str(p.id), p.codigo_barras, p.nombre, str(p.precio_costo), str(p.precio_venta), str(p.stock_actual), p.categoria]
            for i, v in enumerate(d): self.t_inv.setItem(r, i, QTableWidgetItem(v))

    def abrir_new(self):
        if AddProductDialog(self).exec(): self.actualizar_tabla()

    def abrir_edit(self):
        row = self.t_inv.currentRow()
        if row >= 0:
            diag = AddProductDialog(self, int(self.t_inv.item(row,0).text()))
            fields = [diag.txt_codigo, diag.txt_nombre, diag.txt_costo, diag.txt_venta, diag.txt_stock, diag.txt_cat]
            for i, field in enumerate(fields): field.setText(self.t_inv.item(row, i+1).text().replace("$ ", ""))
            if diag.exec(): self.actualizar_tabla()

    def abrir_perdida(self):
        row = self.t_inv.currentRow()
        if row < 0: return
        p_id = int(self.t_inv.item(row, 0).text())
        cant, ok = QInputDialog.getInt(self, "Pérdida", f"Cantidad de {self.t_inv.item(row, 2).text()}:")
        if ok:
            mot, ok_m = QInputDialog.getText(self, "Motivo", "Razón:")
            if ok_m: registrar_perdida(p_id, cant, mot); self.actualizar_tabla()

    def init_page_reportes(self):
        page = QWidget(); layout = QVBoxLayout(page)
        header = QHBoxLayout()
        self.combo_per = QComboBox(); self.combo_per.addItems(["Hoy", "30 días", "Año"]); self.combo_per.currentIndexChanged.connect(self.cargar_reportes)
        btn_excel = QPushButton("📁 Excel"); btn_excel.clicked.connect(self.exportar_excel)
        header.addWidget(self.combo_per); header.addStretch(); header.addWidget(btn_excel)
        self.rep_data = QLabel("Resumen..."); self.rep_data.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B;")
        self.canvas = MplCanvas(self, width=5, height=3)
        self.tabla_per = QTableWidget(); self.tabla_per.setColumnCount(3); self.tabla_per.setHorizontalHeaderLabels(["Producto", "Cant", "Motivo"])
        self.tabla_per.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.tabla_per.setFixedHeight(150)
        layout.addWidget(QLabel("<h1>📊 Análisis de Negocio</h1>")); layout.addLayout(header); layout.addWidget(self.rep_data)
        layout.addWidget(QLabel("<h3>Ventas (Verde) vs Pérdidas (Rojo)</h3>")); layout.addWidget(self.canvas)
        layout.addWidget(QLabel("<h3>⚠️ Historial de Pérdidas</h3>")); layout.addWidget(self.tabla_per); self.stack.addWidget(page)

    def cargar_reportes(self):
        idx = self.combo_per.currentIndex()
        dias = 1 if idx == 0 else (30 if idx == 1 else 365)
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
        idx = self.combo_per.currentIndex()
        dias = 1 if idx == 0 else (30 if idx == 1 else 365)
        df = exportar_datos_excel(dias)
        if not df.empty:
            fname = f"reporte_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            df.to_excel(fname, index=False); QMessageBox.information(self, "Éxito", f"Excel guardado: {fname}")