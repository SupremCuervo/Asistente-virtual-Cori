"""
Overlay compacto morado/negro (usa el mismo widget que la app principal).
Ejecutar: python demo_overlay.py
"""

import sys

from PyQt6.QtWidgets import QApplication

from cori.overlay import CoriOverlay


def main() -> None:
	app = QApplication(sys.argv)
	app.setStyle("Fusion")
	w = CoriOverlay()
	w.mostrar_mensaje("Te escuché: Hey Cori", duracion_ms=8000)
	sys.exit(app.exec())


if __name__ == "__main__":
	main()
