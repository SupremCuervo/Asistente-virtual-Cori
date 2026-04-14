"""
Vista previa del tema morado + negro (configuración simulada).
Ejecutar: python demo_tema.py
"""

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
	QApplication,
	QFrame,
	QHBoxLayout,
	QLabel,
	QLineEdit,
	QMainWindow,
	QPushButton,
	QVBoxLayout,
	QWidget,
)

from cori.theme import estilo_global_qss


class VentanaDemo(QMainWindow):
	def __init__(self) -> None:
		super().__init__()
		self.setWindowTitle("Cori — tema morado / negro")
		self.setMinimumSize(420, 320)
		self._construir_ui()

	def _construir_ui(self) -> None:
		central = QWidget()
		self.setCentralWidget(central)
		layout = QVBoxLayout(central)
		layout.setSpacing(16)
		layout.setContentsMargins(24, 24, 24, 24)

		titulo = QLabel("Configuración Cori")
		titulo.setObjectName("titulo")
		sub = QLabel("Accesos directos y opciones (demo visual)")
		sub.setObjectName("subtitulo")
		layout.addWidget(titulo)
		layout.addWidget(sub)

		tarjeta = QFrame()
		tarjeta.setObjectName("tarjeta")
		tarjeta_layout = QVBoxLayout(tarjeta)
		tarjeta_layout.setContentsMargins(16, 16, 16, 16)
		tarjeta_layout.addWidget(QLabel("Comando de voz de prueba"))
		tarjeta_layout.addWidget(QLineEdit("Hey Cori, reproducir música"))
		fila = QHBoxLayout()
		btn_ok = QPushButton("Guardar")
		btn_cancel = QPushButton("Cancelar")
		btn_cancel.setObjectName("secundario")
		fila.addStretch()
		fila.addWidget(btn_cancel)
		fila.addWidget(btn_ok)
		tarjeta_layout.addLayout(fila)
		layout.addWidget(tarjeta)
		layout.addStretch()


def main() -> None:
	app = QApplication(sys.argv)
	app.setStyle("Fusion")
	app.setStyleSheet(estilo_global_qss())
	w = VentanaDemo()
	w.show()
	sys.exit(app.exec())


if __name__ == "__main__":
	main()
