# src/ui/main_window.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from .add_product_dialog import AddProductDialog
from src.database.controller import *

# Imports para el gráfico
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
        self.setWindowTitle("FlowGestion")
        self.resize(1200, 850)
        
        main_widget = QWidget(); self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget); layout.setContentsMargins(0,0,0,0)

        # Sidebar
        sidebar = QFrame(); sidebar.setObjectName("Sidebar")
        s_layout = QVBoxLayout(sidebar); s_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        title = QLabel("FlowGestion"); title.setStyleSheet("color: white; font-size: 22px; font-weight: bold; margin: 20px;")
        
        btns = [("🛒 Ventas", 0), ("📦 Stock", 1), ("📊 Reportes", 2)]
        self.nav_btns = []
        s_layout.addWidget(title)
        for text, index in btns:
            b = QPushButton(text); b.clicked.connect(lambda ch, i=index: self.cambiar_pagina(i))
            s_layout.addWidget(b); self.nav_btns.append(b)

        self.stack = QStackedWidget(); self.stack.setObjectName("MainContent")
        self.init_page_ventas(); self.init_page_inventario(); self.init_page_reportes()
        layout.addWidget(sidebar); layout.addWidget(self.stack)

    def cambiar_pagina(self, i):
        self.stack.setCurrentIndex(i)
        if i == 2: self.cargar_reportes()

    # --- VENTAS ---
    def init_page_ventas(self):
        page = QWidget(); layout = QVBoxLayout(page)
        self.txt_scan = QLineEdit(); self.txt_scan.setPlaceholderText("Escanear...")
        self.txt_scan.returnPressed.connect(self.agregar_carrito)
        
        self.tabla_cart = QTableWidget(); self.tabla_cart.setColumnCount(5)
        self.tabla_cart.setHorizontalHeaderLabels(["ID", "Producto", "Precio", "Cant.", "Subtotal"])
        self.tabla_cart.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_cart.cellChanged.connect(self.recalc_fila)

        footer = QHBoxLayout()
        self.btn_del = QPushButton("🗑️ Quitar"); self.btn_del.setObjectName("btnEliminar"); self.btn_del.clicked.connect(self.borrar_item)
        self.lbl_tot = QLabel("Total: $ 0.00"); self.lbl_tot.setStyleSheet("font-size: 28px; font-weight: bold;")
        btn_pay = QPushButton("💳 COBRAR"); btn_pay.setObjectName("btnVenta"); btn_pay.clicked.connect(self.cobrar)
        
        footer.addWidget(self.btn_del); footer.addStretch(); footer.addWidget(self.lbl_tot); footer.addWidget(btn_pay)
        layout.addWidget(QLabel("<h1>Caja Registradora</h1>")); layout.addWidget(self.txt_scan); layout.addWidget(self.tabla_cart); layout.addLayout(footer)
        self.stack.addWidget(page)

    def agregar_carrito(self):
        prods = buscar_productos(self.txt_scan.text())
        if not prods or prods[0].stock_actual <= 0: return
        p = prods[0]; r = self.tabla_cart.rowCount(); self.tabla_cart.insertRow(r)
        self.tabla_cart.blockSignals(True)
        items = [str(p.id), p.nombre, str(p.precio_venta), "1", str(p.precio_venta)]
        for i, v in enumerate(items): self.tabla_cart.setItem(r, i, QTableWidgetItem(v))
        self.tabla_cart.blockSignals(False); self.txt_scan.clear(); self.recalc_total()

    def recalc_fila(self, r, c):
        if c == 3:
            self.tabla_cart.blockSignals(True)
            try:
                sub = int(self.tabla_cart.item(r, 3).text()) * float(self.tabla_cart.item(r, 2).text())
                self.tabla_cart.setItem(r, 4, QTableWidgetItem(f"{sub:.2f}"))
            except: pass
            self.tabla_cart.blockSignals(False); self.recalc_total()

    def recalc_total(self):
        t = sum(float(self.tabla_cart.item(r, 4).text()) for r in range(self.tabla_cart.rowCount()))
        self.lbl_tot.setText(f"Total: $ {t:.2f}")

    def borrar_item(self):
        if self.tabla_cart.currentRow() >= 0: self.tabla_cart.removeRow(self.tabla_cart.currentRow()); self.recalc_total()

    def cobrar(self):
        if self.tabla_cart.rowCount() == 0: return
        items = []
        for r in range(self.tabla_cart.rowCount()):
            items.append({'id': int(self.tabla_cart.item(r, 0).text()), 'cant': int(self.tabla_cart.item(r, 3).text()), 'precio': float(self.tabla_cart.item(r, 2).text())})
        if registrar_venta_completa(float(self.lbl_tot.text().replace("Total: $ ", "")), items):
            QMessageBox.information(self, "Éxito", "Venta cobrada"); self.tabla_cart.setRowCount(0); self.recalc_total(); self.actualizar_tabla()

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
        layout.addLayout(h); layout.addWidget(self.t_inv)
        self.stack.addWidget(page); self.actualizar_tabla()

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
            diag.txt_codigo.setText(self.t_inv.item(row,1).text())
            diag.txt_nombre.setText(self.t_inv.item(row,2).text())
            diag.txt_costo.setText(self.t_inv.item(row,3).text())
            diag.txt_venta.setText(self.t_inv.item(row,4).text())
            diag.txt_stock.setText(self.t_inv.item(row,5).text())
            diag.txt_cat.setText(self.t_inv.item(row,6).text())
            if diag.exec(): self.actualizar_tabla()

    def abrir_perdida(self):
        row = self.t_inv.currentRow()
        if row < 0: return
        p_id = int(self.t_inv.item(row, 0).text())
        cant, ok = QInputDialog.getInt(self, "Pérdida", f"Cantidad de {self.t_inv.item(row, 2).text()}:")
        if ok:
            mot, ok_m = QInputDialog.getText(self, "Motivo", "Razón:")
            if ok_m: registrar_perdida(p_id, cant, mot); self.actualizar_tabla()

    # --- REPORTES AVANZADOS ---
    def init_page_reportes(self):
        page = QWidget(); layout = QVBoxLayout(page)
        
        # Filtro de tiempo
        self.combo_per = QComboBox(); self.combo_per.addItems(["Hoy", "30 días", "Año"])
        self.combo_per.currentIndexChanged.connect(self.cargar_reportes)
        
        # Resumen de Etiquetas
        self.rep_data = QLabel("Cargando..."); self.rep_data.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B;")
        
        # Área del Gráfico
        self.canvas = MplCanvas(self, width=5, height=3, dpi=100)
        
        # Tabla de Detalles de Pérdidas
        self.tabla_perdidas = QTableWidget(); self.tabla_perdidas.setColumnCount(3)
        self.tabla_perdidas.setHorizontalHeaderLabels(["Producto", "Cantidad", "Motivo"])
        self.tabla_perdidas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_perdidas.setFixedHeight(150)

        layout.addWidget(QLabel("<h1>📊 Análisis de Negocio</h1>"))
        layout.addWidget(self.combo_per)
        layout.addWidget(self.rep_data)
        layout.addWidget(QLabel("<h3>📦 Ventas por Categoría</h3>"))
        layout.addWidget(self.canvas)
        layout.addWidget(QLabel("<h3>⚠️ Historial de Pérdidas</h3>"))
        layout.addWidget(self.tabla_perdidas)
        
        self.stack.addWidget(page)

    def cargar_reportes(self):
        idx = self.combo_per.currentIndex()
        dias = 1 if idx == 0 else (30 if idx == 1 else 365)
        
        # 1. Obtener datos del controlador
        res = obtener_reporte_periodo(dias)
        grafico_data = obtener_ventas_por_categoria(dias)
        
        # 2. Actualizar Etiquetas
        self.rep_data.setText(
            f"💰 Ingresos: $ {res['ingresos']:.2f}   |   📈 Ganancia Neta: $ {res['ganancia']:.2f}\n"
            f"🛒 Operaciones: {res['operaciones']}   |   📉 Pérdidas en $: $ {res['perdidas_total_val']:.2f}"
        )
        
        # 3. Actualizar Tabla de Pérdidas
        self.tabla_perdidas.setRowCount(0)
        for p in res['lista_detallada_perdidas']:
            r = self.tabla_perdidas.rowCount(); self.tabla_perdidas.insertRow(r)
            self.tabla_perdidas.setItem(r, 0, QTableWidgetItem(p['prod']))
            self.tabla_perdidas.setItem(r, 1, QTableWidgetItem(str(p['cant'])))
            self.tabla_perdidas.setItem(r, 2, QTableWidgetItem(p['motivo']))

        # 4. Actualizar Gráfico
        self.canvas.axes.cla() # Limpiar gráfico anterior
        categorias = [x[0] for x in grafico_data]
        valores = [x[1] for x in grafico_data]
        
        if categorias:
            self.canvas.axes.bar(categorias, valores, color='#22C55E')
            self.canvas.axes.set_ylabel('Ventas ($)')
            self.canvas.axes.set_title('Ingresos por Categoría')
        else:
            self.canvas.axes.text(0.5, 0.5, 'Sin datos para mostrar', ha='center', va='center')
        
        self.canvas.draw()