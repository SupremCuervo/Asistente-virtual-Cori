"""
Interfaz clara: fondo blanco con acentos morados (ventana principal y overlay).
"""

# Fondos
COLOR_FONDO = "#ffffff"
COLOR_SUPERFICIE = "#faf5ff"
COLOR_SUPERFICIE_ELEVADA = "#f3e8ff"
COLOR_BORDE = "#e9d5ff"
COLOR_FILA_ALTERNA = "#fdfaff"

# Morados
COLOR_PRIMARIO = "#6d28d9"
COLOR_PRIMARIO_HOVER = "#7c3aed"
COLOR_PRIMARIO_PRESSED = "#5b21b6"
COLOR_ACENTO_SUAVE = "#ede9fe"

# Texto
COLOR_TEXTO = "#1e1033"
COLOR_TEXTO_SECUNDARIO = "#64748b"
COLOR_TITULO_SECCION = "#5b21b6"

# Estados
COLOR_EXITO = "#059669"
COLOR_AVISO = "#d97706"
COLOR_ERROR = "#dc2626"


def estilo_global_qss() -> str:
	return f"""
		QWidget {{
			background-color: {COLOR_FONDO};
			color: {COLOR_TEXTO};
			font-family: "Segoe UI", "Inter", sans-serif;
			font-size: 13px;
		}}
		QMainWindow, QDialog {{
			background-color: {COLOR_FONDO};
		}}
		QTabWidget::pane {{
			border: 1px solid {COLOR_BORDE};
			border-radius: 10px;
			background-color: {COLOR_FONDO};
			top: -1px;
			padding: 8px;
		}}
		QTabBar::tab {{
			background-color: {COLOR_SUPERFICIE_ELEVADA};
			color: {COLOR_PRIMARIO_PRESSED};
			border: 1px solid {COLOR_BORDE};
			border-bottom: none;
			border-top-left-radius: 8px;
			border-top-right-radius: 8px;
			padding: 10px 18px;
			margin-right: 3px;
			font-weight: 500;
		}}
		QTabBar::tab:selected {{
			background-color: {COLOR_FONDO};
			color: {COLOR_PRIMARIO};
			font-weight: 700;
			border-bottom: 2px solid {COLOR_PRIMARIO};
		}}
		QTabBar::tab:hover:!selected {{
			background-color: {COLOR_ACENTO_SUAVE};
		}}
		QFrame#tarjeta, QFrame#seccion {{
			background-color: {COLOR_SUPERFICIE};
			border: 1px solid {COLOR_BORDE};
			border-radius: 12px;
		}}
		QLabel#titulo {{
			color: {COLOR_PRIMARIO};
			font-size: 22px;
			font-weight: 700;
		}}
		QLabel#subtitulo {{
			color: {COLOR_TEXTO_SECUNDARIO};
			font-size: 12px;
		}}
		QPushButton {{
			background-color: {COLOR_PRIMARIO};
			color: #ffffff;
			border: none;
			border-radius: 10px;
			padding: 11px 22px;
			font-weight: 600;
			min-height: 20px;
		}}
		QPushButton:hover {{
			background-color: {COLOR_PRIMARIO_HOVER};
		}}
		QPushButton:pressed {{
			background-color: {COLOR_PRIMARIO_PRESSED};
		}}
		QPushButton#secundario {{
			background-color: {COLOR_SUPERFICIE_ELEVADA};
			color: {COLOR_PRIMARIO_PRESSED};
			border: 1px solid {COLOR_BORDE};
		}}
		QPushButton#secundario:hover {{
			background-color: {COLOR_ACENTO_SUAVE};
			border-color: {COLOR_PRIMARIO};
		}}
		QPushButton#grande {{
			font-size: 15px;
			padding: 14px 28px;
		}}
		QLineEdit, QComboBox {{
			background-color: {COLOR_FONDO};
			border: 1px solid {COLOR_BORDE};
			border-radius: 8px;
			padding: 9px 12px;
			color: {COLOR_TEXTO};
		}}
		QLineEdit:focus, QComboBox:focus {{
			border: 2px solid {COLOR_PRIMARIO};
		}}
		QTextEdit, QTextBrowser {{
			background-color: {COLOR_SUPERFICIE};
			border: 1px solid {COLOR_BORDE};
			border-radius: 10px;
			padding: 12px;
			color: {COLOR_TEXTO};
		}}
		QTextBrowser a {{
			color: {COLOR_PRIMARIO};
		}}
		QScrollArea {{
			border: none;
			background-color: transparent;
		}}
		QTableWidget {{
			background-color: {COLOR_FONDO};
			alternate-background-color: {COLOR_FILA_ALTERNA};
			border: 1px solid {COLOR_BORDE};
			border-radius: 8px;
			gridline-color: {COLOR_BORDE};
			color: {COLOR_TEXTO};
		}}
		QTableWidget::item:selected {{
			background-color: {COLOR_ACENTO_SUAVE};
			color: {COLOR_TEXTO};
		}}
		QHeaderView::section {{
			background-color: {COLOR_SUPERFICIE_ELEVADA};
			color: {COLOR_PRIMARIO_PRESSED};
			padding: 8px 10px;
			border: none;
			border-bottom: 2px solid {COLOR_PRIMARIO};
			font-weight: 600;
		}}
		QScrollBar:vertical {{
			background: {COLOR_SUPERFICIE};
			width: 11px;
			border-radius: 5px;
		}}
		QScrollBar::handle:vertical {{
			background: {COLOR_PRIMARIO};
			min-height: 28px;
			border-radius: 5px;
		}}
		QScrollBar::handle:vertical:hover {{
			background: {COLOR_PRIMARIO_HOVER};
		}}
	"""


def estilo_overlay_qss() -> str:
	"""Toast y escucha: cristal claro con borde morado."""
	return f"""
		QWidget {{
			background-color: rgba(255, 255, 255, 235);
			color: {COLOR_TEXTO};
			font-family: "Segoe UI", sans-serif;
			font-size: 14px;
		}}
		QLabel#mensaje {{
			color: {COLOR_PRIMARIO_PRESSED};
			font-weight: 600;
			font-size: 15px;
		}}
		QFrame#marco {{
			border: 2px solid {COLOR_PRIMARIO};
			border-radius: 14px;
			background-color: rgba(250, 245, 255, 245);
		}}
		QProgressBar#nivel_mic {{
			border: 1px solid {COLOR_BORDE};
			border-radius: 5px;
			background-color: {COLOR_SUPERFICIE};
		}}
		QProgressBar#nivel_mic::chunk {{
			background-color: {COLOR_PRIMARIO};
			border-radius: 4px;
		}}
	"""
