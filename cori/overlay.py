"""
Ventana flotante de feedback (tema claro morado) y modo «Escuchando» con barra de nivel.
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QFrame, QLabel, QProgressBar, QVBoxLayout, QWidget

from cori.theme import estilo_overlay_qss


class CoriOverlay(QWidget):
	def __init__(self) -> None:
		super().__init__()
		self.setStyleSheet(estilo_overlay_qss())
		self.setWindowFlags(
			Qt.WindowType.FramelessWindowHint
			| Qt.WindowType.WindowStaysOnTopHint
			| Qt.WindowType.Tool
		)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
		self.setMinimumWidth(280)
		self.setMaximumWidth(440)
		self._modo_escucha = False
		self._timer = QTimer(self)
		self._timer.setSingleShot(True)
		self._timer.timeout.connect(self._al_expirar_toast)
		self._etiqueta = QLabel()
		self._etiqueta.setObjectName("mensaje")
		self._etiqueta.setWordWrap(True)
		self._etiqueta.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self._barra = QProgressBar()
		self._barra.setObjectName("nivel_mic")
		self._barra.setRange(0, 100)
		self._barra.setValue(0)
		self._barra.setTextVisible(False)
		self._barra.setFixedHeight(8)
		self._barra.setVisible(False)
		outer = QVBoxLayout(self)
		outer.setContentsMargins(8, 8, 8, 8)
		marco = QFrame()
		marco.setObjectName("marco")
		inner = QVBoxLayout(marco)
		inner.setContentsMargins(16, 12, 16, 12)
		inner.setSpacing(10)
		inner.addWidget(self._etiqueta)
		inner.addWidget(self._barra)
		outer.addWidget(marco)

	def _al_expirar_toast(self) -> None:
		if not self._modo_escucha:
			self.hide()

	def mostrar_escucha_activa(self) -> None:
		"""Tras «Cori»: se queda visible con barra de entrada hasta ocultar_escucha_activa."""
		self._timer.stop()
		self._modo_escucha = True
		self._etiqueta.setText("Escuchando…\n(suelta de hablar cuando termines)")
		self._barra.setVisible(True)
		self._barra.setValue(0)
		self.adjustSize()
		self._posicionar()
		self.show()
		self.raise_()
		self.activateWindow()

	def set_nivel_microfono(self, nivel: int) -> None:
		self._barra.setValue(max(0, min(100, int(nivel))))

	def ocultar_escucha_activa(self) -> None:
		if not self._modo_escucha:
			return
		self._modo_escucha = False
		self._barra.setVisible(False)
		self._barra.setValue(0)
		self.hide()

	def mostrar_mensaje(self, texto: str, duracion_ms: int = 2800) -> None:
		self.ocultar_escucha_activa()
		self._etiqueta.setText(texto)
		self.adjustSize()
		self._posicionar()
		self.show()
		self.raise_()
		self.activateWindow()
		self._timer.start(duracion_ms)

	def _posicionar(self) -> None:
		app = QApplication.instance()
		screen = app.primaryScreen() if app else None
		if not screen:
			return
		geo = screen.availableGeometry()
		x = geo.right() - self.width() - 16
		y = geo.bottom() - self.height() - 16
		self.move(max(geo.left(), x), max(geo.top(), y))
