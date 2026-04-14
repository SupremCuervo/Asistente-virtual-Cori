"""
Cori: escucha de voz + overlay + comandos básicos.

Motor google: micrófono + Internet (SpeechRecognition).
Motor vosk: micrófono + modelo descargado (sin Internet para el reconocimiento).

Ejecutar: python cori_app.py
"""

from __future__ import annotations

import subprocess
import sys
import webbrowser
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
	QAbstractItemView,
	QApplication,
	QFormLayout,
	QFrame,
	QHBoxLayout,
	QLabel,
	QLineEdit,
	QMainWindow,
	QMessageBox,
	QPushButton,
	QScrollArea,
	QTabWidget,
	QTableWidget,
	QTableWidgetItem,
	QTextBrowser,
	QVBoxLayout,
	QWidget,
)

from cori.comandos_voz import Comando, TipoComando, interpretar
from cori.config_cori import (
	cargar_config,
	guardar_personalizacion_completa,
	personalizacion_desde_config,
)
from cori.escucha import HiloEscucha
from cori.overlay import CoriOverlay
from cori.teclas_windows import (
	bloquear_pantalla_win_l,
	captura_recorte_win_shift_s,
	copiar_portapapeles_ctrl_c,
	deshacer_ctrl_z,
	explorador_archivos_win_e,
	minimizar_todo_win_d,
	pegar_portapapeles_ctrl_v,
	rehacer_ctrl_y,
	siguiente_ventana_alt_tab,
	volumen_bajar,
	volumen_silenciar,
	volumen_subir,
	youtube_play_pause_tecla_k,
)
from cori.tiempo_voz import texto_fecha_para_voz, texto_hora_para_voz
from cori.volumen_sistema_windows import volumen_establecer_porcentaje
from cori.voz_sistema import hablar
from cori.theme import estilo_global_qss


def _abrir_en_windows(comando_o_ruta: str) -> None:
	"""Ejecuta un comando del PATH o una ruta con asociación por defecto."""
	try:
		subprocess.Popen(
			["cmd", "/c", "start", "", comando_o_ruta],
			shell=False,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		)
	except OSError:
		subprocess.Popen(comando_o_ruta, shell=True)


def _cerrar_navegadores_windows(procesos: list[str]) -> None:
	if sys.platform != "win32":
		return
	flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
	for im in procesos:
		s = str(im).strip()
		if not s:
			continue
		subprocess.run(
			["taskkill", "/F", "/IM", s],
			capture_output=True,
			text=True,
			creationflags=flags,
		)


TEXTO_PRESENTACION = """
<body style="margin:12px; color:#1e1033; font-family:Segoe UI,sans-serif; font-size:14px; line-height:1.5;">
<h2 style="color:#6d28d9; margin-top:0;">¿Qué es Cori?</h2>
<p><b>Cori</b> es tu asistente por <b>voz</b> en Windows: habla y él abre programas, páginas web, sube o baja el volumen, simula teclas (copiar, pegar, captura…) y puede contestarte en voz si lo configuras.</p>

<h2 style="color:#6d28d9;">Cómo usarlo (muy simple)</h2>
<ol>
<li>Pulsa <b>Iniciar escucha</b> en la pestaña «Uso».</li>
<li>Di la palabra <b>Cori</b> en la misma frase que la orden, <i>o</i> primero «Cori» y, cuando veas la barra morada, di solo la orden.</li>
<li>Para dejar de escuchar el micrófono: <b>para de escuchar</b>.</li>
</ol>

<h2 style="color:#6d28d9;">Comandos que entiende (ejemplos)</h2>
<table border="0" cellpadding="6" cellspacing="0" style="border-collapse:collapse; width:100%; background:#faf5ff; border-radius:8px;">
<tr style="background:#ede9fe;"><td><b>Tema</b></td><td><b>Di algo como…</b></td></tr>
<tr><td>Música</td><td>«Cori, pon música» · «pon una canción»</td></tr>
<tr><td>Abrir algo</td><td>«abre Edge» · «abre Netflix» · «abre google» (lo añades en Personalizar)</td></tr>
<tr><td>Explorador Win+E</td><td>«atajo del explorador» · «explorador rápido»</td></tr>
<tr><td>Ajustes Windows</td><td>«abre configuración» · «abre los ajustes»</td></tr>
<tr><td>Copiar / pegar</td><td>«copia» · «pegar» · «control c» / «control v»</td></tr>
<tr><td>Deshacer / rehacer</td><td>«deshacer» · «rehacer» · «control z» / «control y»</td></tr>
<tr><td>Cambiar ventana</td><td>«cambia de ventana» · «siguiente ventana» · «alt tab»</td></tr>
<tr><td>Escritorio</td><td>«minimiza todo» · «mostrar escritorio»</td></tr>
<tr><td>Bloquear pantalla</td><td>«bloquea la pantalla» · «pantalla de bloqueo»</td></tr>
<tr><td>Captura</td><td>«captura de pantalla» (recorte Win+Shift+S)</td></tr>
<tr><td>Hora / fecha (voz)</td><td>«dime la hora» · «qué día es hoy» (necesita pyttsx3)</td></tr>
<tr><td>YouTube</td><td>«entra en video» · «pausa el vídeo» (tecla K con foco en el navegador)</td></tr>
<tr><td>Volumen</td><td>«volumen a 50» · «sube el volumen» · «silenciar el volumen»</td></tr>
<tr><td>Navegador</td><td>«cierra navegador»</td></tr>
<tr><td>Programador</td><td>«modo programador»</td></tr>
<tr><td>Saludos</td><td>«hola cori» · «gracias cori» · «adiós cori» (editables en Personalizar)</td></tr>
</table>

<h2 style="color:#6d28d9;">Pestaña «Personalizar»</h2>
<p>Ahí defines <b>sin escribir JSON</b>: mensajes, aplicaciones, frases extra para atajos, textos de hora/fecha y páginas web. Pulsa <b>Guardar</b> al terminar.</p>

<h2 style="color:#6d28d9;">Reconocimiento de voz</h2>
<p><b>Google:</b> necesita Internet. <b>Vosk:</b> sin Internet para escuchar, pero debes descargar un modelo y poner la ruta en <code>config.json</code>. La voz para leer hora o mensajes usa el PC (pyttsx3).</p>
</body>
"""

_TECLAS_FRASES_META: tuple[tuple[str, str, str], ...] = (
	("copia", "Copiar → Ctrl + C", "Frases extra, separadas por coma."),
	("pega", "Pegar → Ctrl + V", "Ej.: pega ya"),
	("minimiza_todo", "Escritorio → Win + D", "Ej.: fuera ventanas"),
	("captura", "Recorte → Win + Shift + S", "Ej.: recorte ya"),
	("hora", "Preguntar la hora (voz)", "Ej.: momento actual"),
	("fecha", "Preguntar la fecha (voz)", "Ej.: calendario de hoy"),
	("bloquear_pantalla", "Bloquear sesión → Win + L", "Ej.: bloquea la pantalla"),
	("deshacer", "Deshacer → Ctrl + Z", "Ej.: vuelve atrás"),
	("rehacer", "Rehacer → Ctrl + Y", "Ej.: otra vez"),
	("alt_tab", "Cambiar ventana → Alt + Tab", "Ej.: siguiente ventana"),
	("ajustes_windows", "Abrir Ajustes (frases extra)", "Ya incluye «abre configuración»…"),
	("explorador_win_e", "Explorador Win + E (frases extra)", "Ya incluye «atajo del explorador»…"),
)


class VentanaPrincipal(QMainWindow):
	def __init__(self) -> None:
		super().__init__()
		self._base = Path(__file__).resolve().parent
		self._config = cargar_config(self._base)
		self._hilo: HiloEscucha | None = None
		self.setWindowTitle("Cori — asistente por voz")
		self.setMinimumSize(540, 520)
		self._overlay = CoriOverlay()
		self._construir_ui()
		self._refrescar_editores_personalizacion()

	def _caja_seccion(self, titulo: str, subtitulo: str) -> tuple[QFrame, QVBoxLayout]:
		fr = QFrame()
		fr.setObjectName("seccion")
		ly = QVBoxLayout(fr)
		ly.setContentsMargins(14, 12, 14, 14)
		ly.setSpacing(8)
		tit = QLabel(f"<span style='font-size:15px; font-weight:700; color:#5b21b6;'>{titulo}</span>")
		tit.setWordWrap(True)
		sub = QLabel(f"<span style='color:#64748b; font-size:12px;'>{subtitulo}</span>")
		sub.setWordWrap(True)
		ly.addWidget(tit)
		ly.addWidget(sub)
		return fr, ly

	def _construir_ui(self) -> None:
		central = QWidget()
		self.setCentralWidget(central)
		layout = QVBoxLayout(central)
		layout.setSpacing(12)
		layout.setContentsMargins(20, 20, 20, 20)

		tabs = QTabWidget()

		tab_pres = QWidget()
		lay_pres = QVBoxLayout(tab_pres)
		lay_pres.setContentsMargins(0, 4, 0, 0)
		browser = QTextBrowser()
		browser.setOpenExternalLinks(True)
		browser.setMinimumHeight(420)
		browser.setHtml(TEXTO_PRESENTACION)
		lay_pres.addWidget(browser)
		tabs.addTab(tab_pres, "Presentación")

		tab_uso = QWidget()
		tab_uso_layout = QVBoxLayout(tab_uso)
		tab_uso_layout.setSpacing(14)
		tab_uso_layout.setContentsMargins(0, 8, 0, 0)

		titulo = QLabel("Cori")
		titulo.setObjectName("titulo")
		self._sub_motor = QLabel(self._texto_subtitulo_motor())
		self._sub_motor.setObjectName("subtitulo")
		self._sub_motor.setWordWrap(True)
		tab_uso_layout.addWidget(titulo)
		tab_uso_layout.addWidget(self._sub_motor)

		pasos = QLabel(
			"<b>Tres pasos:</b> (1) Pulsa el botón morado. (2) Di <b>Cori</b> y lo que quieras, o solo <b>Cori</b> "
			"y luego la orden cuando aparezca la barra. (3) La lista completa de frases está en la pestaña "
			"<b>Presentación</b>."
		)
		pasos.setWordWrap(True)
		tab_uso_layout.addWidget(pasos)

		self._estado = QLabel("Estado: en pausa")
		self._estado.setObjectName("subtitulo")
		tab_uso_layout.addWidget(self._estado)

		self._ultima = QLabel("Última frase: —")
		self._ultima.setWordWrap(True)
		self._ultima.setObjectName("subtitulo")
		tab_uso_layout.addWidget(self._ultima)

		fila = QHBoxLayout()
		self._btn_iniciar = QPushButton("Iniciar escucha")
		self._btn_iniciar.setObjectName("grande")
		self._btn_detener = QPushButton("Detener escucha")
		self._btn_detener.setObjectName("secundario")
		self._btn_detener.setEnabled(False)
		fila.addWidget(self._btn_iniciar)
		fila.addWidget(self._btn_detener)
		fila.addStretch()
		tab_uso_layout.addLayout(fila)

		self._btn_iniciar.clicked.connect(self._iniciar_escucha)
		self._btn_detener.clicked.connect(self._detener_escucha)

		tarjeta = QFrame()
		tarjeta.setObjectName("tarjeta")
		tl = QVBoxLayout(tarjeta)
		tl.setContentsMargins(12, 12, 12, 12)
		tl.addWidget(
			QLabel(
				"<b>Avanzado:</b> en la carpeta del proyecto, <code>config.json</code> guarda el motor de voz "
				"(<code>google</code> o <code>vosk</code>), modelo Vosk, música y modo programador. "
				"Lo demás se edita fácil en <b>Personalizar</b>."
			)
		)
		tab_uso_layout.addWidget(tarjeta)
		tab_uso_layout.addStretch()
		tabs.addTab(tab_uso, "Uso")

		tab_pers = QWidget()
		pl_outer = QVBoxLayout(tab_pers)
		pl_outer.setContentsMargins(0, 0, 0, 0)
		scroll = QScrollArea()
		scroll.setWidgetResizable(True)
		scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
		inner = QWidget()
		pl = QVBoxLayout(inner)
		pl.setSpacing(16)
		pl.setContentsMargins(0, 4, 4, 4)

		self._tab_mensajes = QTableWidget(0, 3)
		self._tab_mensajes.setHorizontalHeaderLabels(
			["Si dices (coma entre opciones)", "Cori responde", "Voz"]
		)
		self._tab_mensajes.horizontalHeader().setStretchLastSection(False)
		self._tab_mensajes.setColumnWidth(0, 210)
		self._tab_mensajes.setColumnWidth(1, 280)
		self._tab_mensajes.setColumnWidth(2, 42)
		self._tab_mensajes.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
		self._tab_mensajes.setAlternatingRowColors(True)
		self._tab_mensajes.setMinimumHeight(130)
		fx_m, lx_m = self._caja_seccion(
			"Mensajes",
			"Cada fila: varias formas de decirlo (separadas por coma) y la respuesta. "
			"Marca Voz para leer en alto. Puedes usar {nombre_pc}, {usuario}, {hora}, {fecha_larga}… "
			"Tras «Oye Cori» puedes usar frases cortas sin repetir Cori (ej. solo «hola»).",
		)
		lx_m.addWidget(self._tab_mensajes)
		lx_m.addLayout(self._fila_botones_tabla(self._tab_mensajes, es_mensajes=True))
		pl.addWidget(fx_m)

		self._tab_apps = QTableWidget(0, 2)
		self._tab_apps.setHorizontalHeaderLabels(["Cómo lo dirás (nombre)", "Comando o ruta"])
		self._tab_apps.horizontalHeader().setStretchLastSection(True)
		self._tab_apps.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
		self._tab_apps.setAlternatingRowColors(True)
		self._tab_apps.setMinimumHeight(120)
		fx_a, lx_a = self._caja_seccion(
			"Aplicaciones y juegos",
			"Izquierda: cómo lo dirás (ej. «bloc de notas»). Derecha: programa, notepad, ruta a .exe o .url. "
			"Ejemplo de voz: «Cori, abre bloc de notas».",
		)
		lx_a.addWidget(self._tab_apps)
		lx_a.addLayout(self._fila_botones_tabla(self._tab_apps, es_mensajes=False))
		pl.addWidget(fx_a)

		form_teclas = QFormLayout()
		form_teclas.setSpacing(10)
		self._edits_teclas = {}
		for clave, titulo, ayuda in _TECLAS_FRASES_META:
			lbl = QLabel(f"<b>{titulo}</b><br><span style='color:#64748b;font-size:11px;'>{ayuda}</span>")
			lbl.setWordWrap(True)
			ed = QLineEdit()
			ed.setPlaceholderText("Opcional: frase uno, frase dos")
			form_teclas.addRow(lbl, ed)
			self._edits_teclas[clave] = ed
		fx_t, lx_t = self._caja_seccion(
			"Atajos de teclado (frases extra)",
			"Cori ya entiende muchas frases por defecto. Aquí añades más sin código: una o varias por campo, "
			"separadas por coma. Referencia: Copiar Ctrl+C · Pegar Ctrl+V · Escritorio Win+D · Recorte Win+Shift+S · "
			"YouTube pausa tecla K (foco en el navegador).",
		)
		lx_t.addLayout(form_teclas)
		pl.addWidget(fx_t)

		self._ed_plant_hora = QLineEdit()
		self._ed_plant_hora.setPlaceholderText(
			"Ej.: Son las {hora} horas y {minutos} minutos en {nombre_pc}"
		)
		self._ed_plant_fecha = QLineEdit()
		self._ed_plant_fecha.setPlaceholderText("Ej.: En {nombre_pc}: {fecha_larga}")
		fx_h, lx_h = self._caja_seccion(
			"Hora y fecha (voz)",
			"Texto que dirá Cori al preguntar la hora o la fecha. Vacío = frase automática. "
			"Placeholders: {hora}, {minutos}, {nombre_pc}, {fecha_larga}, {hora_corta}…",
		)
		lx_h.addWidget(QLabel("<b>Plantilla — hora</b>"))
		lx_h.addWidget(self._ed_plant_hora)
		lx_h.addWidget(QLabel("<b>Plantilla — fecha</b>"))
		lx_h.addWidget(self._ed_plant_fecha)
		pl.addWidget(fx_h)

		self._tab_urls = QTableWidget(0, 2)
		self._tab_urls.setHorizontalHeaderLabels(["Nombre (lo que dices)", "Dirección https://…"])
		self._tab_urls.horizontalHeader().setStretchLastSection(True)
		self._tab_urls.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
		self._tab_urls.setAlternatingRowColors(True)
		self._tab_urls.setMinimumHeight(110)
		fx_u, lx_u = self._caja_seccion(
			"Páginas web",
			"Nombre corto (ej. «netflix») y la URL completa. Luego dices: «Cori, abre netflix».",
		)
		lx_u.addWidget(self._tab_urls)
		lx_u.addLayout(self._fila_botones_tabla(self._tab_urls, es_mensajes=False))
		pl.addWidget(fx_u)

		scroll.setWidget(inner)
		pl_outer.addWidget(scroll)

		fila_g = QHBoxLayout()
		btn_guardar = QPushButton("Guardar todo")
		btn_recargar = QPushButton("Recargar desde disco")
		btn_recargar.setObjectName("secundario")
		btn_guardar.clicked.connect(self._guardar_personalizacion)
		btn_recargar.clicked.connect(self._refrescar_editores_personalizacion)
		fila_g.addWidget(btn_guardar)
		fila_g.addWidget(btn_recargar)
		fila_g.addStretch()
		pl_outer.addLayout(fila_g)

		tabs.addTab(tab_pers, "Personalizar")
		layout.addWidget(tabs)

	def _fila_botones_tabla(self, tw: QTableWidget, es_mensajes: bool) -> QHBoxLayout:
		h = QHBoxLayout()
		ba = QPushButton("Añadir fila")
		br = QPushButton("Quitar fila seleccionada")
		if es_mensajes:
			ba.clicked.connect(lambda _=False, t=tw: self._anadir_fila_mensaje(t))
		else:
			ba.clicked.connect(lambda _=False, t=tw: self._anadir_fila_kv(t))
		br.clicked.connect(lambda _=False, t=tw: self._quitar_fila_tabla(t))
		h.addWidget(ba)
		h.addWidget(br)
		h.addStretch()
		return h

	def _quitar_fila_tabla(self, tw: QTableWidget) -> None:
		r = tw.currentRow()
		if r >= 0:
			tw.removeRow(r)

	def _anadir_fila_kv(self, tw: QTableWidget) -> None:
		r = tw.rowCount()
		tw.insertRow(r)
		tw.setItem(r, 0, QTableWidgetItem(""))
		tw.setItem(r, 1, QTableWidgetItem(""))

	def _anadir_fila_mensaje(self, tw: QTableWidget) -> None:
		r = tw.rowCount()
		tw.insertRow(r)
		tw.setItem(r, 0, QTableWidgetItem(""))
		tw.setItem(r, 1, QTableWidgetItem(""))
		ch = QTableWidgetItem()
		ch.setFlags(ch.flags() | Qt.ItemFlag.ItemIsUserCheckable)
		ch.setCheckState(Qt.CheckState.Checked)
		tw.setItem(r, 2, ch)

	def _llenar_tabla_kv(self, tw: QTableWidget, datos: dict[str, str]) -> None:
		tw.setRowCount(0)
		for k, v in datos.items():
			r = tw.rowCount()
			tw.insertRow(r)
			tw.setItem(r, 0, QTableWidgetItem(k))
			tw.setItem(r, 1, QTableWidgetItem(v))

	def _leer_tabla_kv(self, tw: QTableWidget) -> dict[str, str]:
		out: dict[str, str] = {}
		for r in range(tw.rowCount()):
			i0 = tw.item(r, 0)
			i1 = tw.item(r, 1)
			k = i0.text().strip() if i0 else ""
			v = i1.text().strip() if i1 else ""
			if k and v:
				out[k] = v
		return out

	def _llenar_tabla_mensajes(self, tw: QTableWidget, lista: list) -> None:
		tw.setRowCount(0)
		for item in lista:
			if not isinstance(item, dict):
				continue
			frases = item.get("frases") or item.get("cuando")
			texto = item.get("texto") or item.get("decir") or item.get("mensaje")
			if not isinstance(frases, list) or not texto:
				continue
			voz = item.get("voz", True)
			if isinstance(voz, str):
				voz = voz.strip().lower() in ("1", "true", "si", "sí", "yes")
			voz = bool(voz)
			r = tw.rowCount()
			tw.insertRow(r)
			tw.setItem(r, 0, QTableWidgetItem(", ".join(str(f) for f in frases)))
			tw.setItem(r, 1, QTableWidgetItem(str(texto).strip()))
			ch = QTableWidgetItem()
			ch.setFlags(ch.flags() | Qt.ItemFlag.ItemIsUserCheckable)
			ch.setCheckState(Qt.CheckState.Checked if voz else Qt.CheckState.Unchecked)
			tw.setItem(r, 2, ch)

	def _leer_tabla_mensajes(self, tw: QTableWidget) -> list[dict]:
		mv: list[dict] = []
		for r in range(tw.rowCount()):
			i0 = tw.item(r, 0)
			i1 = tw.item(r, 1)
			i2 = tw.item(r, 2)
			fs = i0.text().strip() if i0 else ""
			tx = i1.text().strip() if i1 else ""
			if not fs or not tx:
				continue
			frases = [x.strip() for x in fs.split(",") if x.strip()]
			if not frases:
				continue
			voz = i2.checkState() == Qt.CheckState.Checked if i2 else True
			mv.append({"frases": frases, "texto": tx, "voz": voz})
		return mv

	def _refrescar_editores_personalizacion(self) -> None:
		cfg = cargar_config(self._base)
		apps = cfg.get("aplicaciones")
		if not isinstance(apps, dict):
			apps = {}
		urls = cfg.get("urls")
		if not isinstance(urls, dict):
			urls = {}
		apps_s = {str(k): str(v) for k, v in apps.items()}
		urls_s = {str(k): str(v) for k, v in urls.items()}
		self._llenar_tabla_kv(self._tab_apps, apps_s)
		self._llenar_tabla_kv(self._tab_urls, urls_s)

		ft = cfg.get("frases_teclas")
		if not isinstance(ft, dict):
			ft = {}
		for clave, ed in self._edits_teclas.items():
			lst = ft.get(clave)
			if isinstance(lst, list) and lst:
				ed.setText(", ".join(str(x) for x in lst))
			else:
				ed.clear()

		self._ed_plant_hora.setText(str(cfg.get("plantilla_hora_voz") or ""))
		self._ed_plant_fecha.setText(str(cfg.get("plantilla_fecha_voz") or ""))

		mv = cfg.get("mensajes_voz")
		if not isinstance(mv, list):
			mv = []
		self._llenar_tabla_mensajes(self._tab_mensajes, mv)

	def _guardar_personalizacion(self) -> None:
		apps_str = self._leer_tabla_kv(self._tab_apps)
		urls_str = self._leer_tabla_kv(self._tab_urls)
		mv_limpio = self._leer_tabla_mensajes(self._tab_mensajes)
		ft_limpio: dict[str, list[str]] = {}
		for clave, ed in self._edits_teclas.items():
			s = ed.text().strip()
			if s:
				ft_limpio[clave] = [x.strip() for x in s.split(",") if x.strip()]
		ph = " ".join(self._ed_plant_hora.text().split())
		pf = " ".join(self._ed_plant_fecha.text().split())
		try:
			guardar_personalizacion_completa(
				self._base,
				apps_str,
				urls_str,
				ft_limpio,
				mv_limpio,
				ph,
				pf,
			)
		except Exception as e:
			QMessageBox.warning(self, "Guardar", str(e))
			return
		self._config = cargar_config(self._base)
		QMessageBox.information(
			self,
			"Guardado",
			"Se guardó la personalización (mensajes, apps, teclas, hora/fecha, URLs).",
		)

	def _texto_subtitulo_motor(self) -> str:
		self._config = cargar_config(self._base)
		m = str(self._config.get("motor_reconocimiento", "google")).strip().lower()
		if m == "vosk":
			return "Config: Vosk (reconocimiento local, sin Internet)"
		return "Config: Google Speech Recognition (requiere Internet)"

	def _iniciar_escucha(self) -> None:
		if self._hilo and self._hilo.isRunning():
			return
		self._config = cargar_config(self._base)
		self._sub_motor.setText(self._texto_subtitulo_motor())
		motor = str(self._config.get("motor_reconocimiento", "google")).strip().lower()
		if motor and motor not in ("google", "vosk"):
			QMessageBox.warning(
				self,
				"Configuración",
				f"motor_reconocimiento debe ser «google» o «vosk» (valor actual: «{motor}»).",
			)
			return
		if not motor:
			motor = "google"
		idioma = str(self._config.get("idioma_reconocimiento", "es-ES"))
		ruta_vosk = ""
		if motor == "vosk":
			raw = str(self._config.get("ruta_modelo_vosk", "")).strip()
			if not raw:
				QMessageBox.warning(
					self,
					"Modelo Vosk",
					"En config.json define ruta_modelo_vosk con la carpeta del modelo descomprimido "
					"(p. ej. models/vosk-model-small-es-0.42). Descarga desde alphacephei.com/vosk/models.",
				)
				return
			p = Path(raw)
			if not p.is_absolute():
				p = (self._base / p).resolve()
			else:
				p = p.resolve()
			if not p.is_dir():
				QMessageBox.warning(
					self,
					"Modelo Vosk",
					f"No existe la carpeta:\n{p}",
				)
				return
			ruta_vosk = str(p)
		mapa = self._config.get("aplicaciones")
		if not isinstance(mapa, dict):
			mapa = {}
		mapa_str = {str(k): str(v) for k, v in mapa.items()}
		urls = self._config.get("urls")
		if not isinstance(urls, dict):
			urls = {}
		mapa_urls_str = {str(k): str(v) for k, v in urls.items()}
		pers = personalizacion_desde_config(self._config)
		self._hilo = HiloEscucha(
			idioma=idioma,
			motor=motor,
			ruta_modelo_vosk=ruta_vosk,
			mapa_apps=mapa_str,
			mapa_urls=mapa_urls_str,
			personal=pers,
		)
		self._hilo.texto_recibido.connect(self._on_texto)
		self._hilo.despertar_detectado.connect(self._overlay.mostrar_escucha_activa)
		self._hilo.nivel_microfono.connect(self._overlay.set_nivel_microfono)
		self._hilo.escucha_sin_comando.connect(self._overlay.ocultar_escucha_activa)
		self._hilo.error_mic.connect(self._on_error_mic)
		self._hilo.finished.connect(self._hilo_terminado)
		self._hilo.start()
		self._estado.setText("Estado: escuchando…")
		self._btn_iniciar.setEnabled(False)
		self._btn_detener.setEnabled(True)
		self._overlay.mostrar_mensaje("Escucha activa", 2000)

	def _hilo_terminado(self) -> None:
		self._estado.setText("Estado: en pausa")
		self._btn_iniciar.setEnabled(True)
		self._btn_detener.setEnabled(False)

	def _detener_escucha(self) -> None:
		if self._hilo and self._hilo.isRunning():
			self._hilo.detener()
			self._hilo.wait(3000)
		self._hilo_terminado()

	def _on_error_mic(self, mensaje: str) -> None:
		QMessageBox.warning(self, "Micrófono / reconocimiento", mensaje)

	def _on_texto(self, texto: str, segunda_fase: bool) -> None:
		self._overlay.ocultar_escucha_activa()
		self._ultima.setText(f"Última frase: {texto}")
		self._config = cargar_config(self._base)
		mapa = self._config.get("aplicaciones")
		if not isinstance(mapa, dict):
			mapa = {}
		mapa_str = {str(k): str(v) for k, v in mapa.items()}
		urls = self._config.get("urls")
		if not isinstance(urls, dict):
			urls = {}
		mapa_urls_str = {str(k): str(v) for k, v in urls.items()}
		pers = personalizacion_desde_config(self._config)
		cmd = interpretar(
			texto,
			mapa_str,
			mapa_urls_str,
			pers,
			tras_activacion=segunda_fase,
		)
		self._ejecutar_comando(cmd, texto)

	def _ejecutar_comando(self, cmd: Comando, texto_original: str) -> None:
		if cmd.tipo == TipoComando.NINGUNO:
			return

		if cmd.tipo == TipoComando.DETENER_ESCUCHA:
			self._overlay.mostrar_mensaje("Deteniendo escucha…")
			self._detener_escucha()
			return

		if cmd.tipo == TipoComando.SOLO_ACTIVACION:
			self._overlay.mostrar_mensaje("Te escuché: Cori\n¿Qué necesitas?")
			return

		if cmd.tipo == TipoComando.MUSICA:
			url = str(self._config.get("url_musica", ""))
			if url:
				webbrowser.open(url)
			self._overlay.mostrar_mensaje("Reproduciendo música…")
			return

		if cmd.tipo == TipoComando.VOLUMEN_SUBIR:
			try:
				pasos = int(cmd.detalle) if cmd.detalle else 2
			except ValueError:
				pasos = 2
			volumen_subir(pasos)
			self._overlay.mostrar_mensaje(f"Volumen + ({pasos} pasos)")
			return

		if cmd.tipo == TipoComando.VOLUMEN_BAJAR:
			try:
				pasos = int(cmd.detalle) if cmd.detalle else 2
			except ValueError:
				pasos = 2
			volumen_bajar(pasos)
			self._overlay.mostrar_mensaje(f"Volumen − ({pasos} pasos)")
			return

		if cmd.tipo == TipoComando.VOLUMEN_SILENCIAR:
			volumen_silenciar()
			self._overlay.mostrar_mensaje("Silencio / mute")
			return

		if cmd.tipo == TipoComando.CERRAR_NAVEGADOR:
			procs = self._config.get("navegador_procesos_cerrar")
			if not isinstance(procs, list):
				procs = ["msedge.exe", "chrome.exe"]
			_cerrar_navegadores_windows([str(p) for p in procs])
			self._overlay.mostrar_mensaje("Cerrando navegador…")
			return

		if cmd.tipo == TipoComando.ABRIR_URL and cmd.detalle:
			urls_cfg = self._config.get("urls")
			if not isinstance(urls_cfg, dict):
				urls_cfg = {}
			clave = str(cmd.detalle)
			url = str(urls_cfg.get(clave, ""))
			if url:
				webbrowser.open(url)
				self._overlay.mostrar_mensaje(f"Abriendo: {clave}")
			else:
				self._overlay.mostrar_mensaje(f"No hay URL para «{clave}» en config")
			return

		if cmd.tipo == TipoComando.COPIA_PORTAPAPELES:
			copiar_portapapeles_ctrl_c()
			self._overlay.mostrar_mensaje("Copiar (Ctrl+C)")
			return

		if cmd.tipo == TipoComando.PEGA_PORTAPAPELES:
			pegar_portapapeles_ctrl_v()
			self._overlay.mostrar_mensaje("Pegar (Ctrl+V)")
			return

		if cmd.tipo == TipoComando.MINIMIZA_TODO:
			minimizar_todo_win_d()
			self._overlay.mostrar_mensaje("Mostrar escritorio (Win+D)")
			return

		if cmd.tipo == TipoComando.CAPTURA_PANTALLA:
			captura_recorte_win_shift_s()
			self._overlay.mostrar_mensaje("Recorte de pantalla (Win+Shift+S)")
			return

		if cmd.tipo == TipoComando.BLOQUEAR_PANTALLA:
			bloquear_pantalla_win_l()
			self._overlay.mostrar_mensaje("Bloqueando pantalla (Win+L)")
			return

		if cmd.tipo == TipoComando.DESHACER:
			deshacer_ctrl_z()
			self._overlay.mostrar_mensaje("Deshacer (Ctrl+Z)")
			return

		if cmd.tipo == TipoComando.REHACER:
			rehacer_ctrl_y()
			self._overlay.mostrar_mensaje("Rehacer (Ctrl+Y)")
			return

		if cmd.tipo == TipoComando.ALT_TAB_VENTANA:
			siguiente_ventana_alt_tab()
			self._overlay.mostrar_mensaje("Cambiar de ventana (Alt+Tab)")
			return

		if cmd.tipo == TipoComando.EXPLORADOR_WIN_E:
			explorador_archivos_win_e()
			self._overlay.mostrar_mensaje("Explorador de archivos (Win+E)")
			return

		if cmd.tipo == TipoComando.HABLAR_HORA:
			plant = str(cmd.detalle).strip() if cmd.detalle else None
			tx = texto_hora_para_voz(plant if plant else None)
			hablar(tx)
			self._overlay.mostrar_mensaje(tx)
			return

		if cmd.tipo == TipoComando.HABLAR_FECHA:
			plant = str(cmd.detalle).strip() if cmd.detalle else None
			tx = texto_fecha_para_voz(plant if plant else None)
			hablar(tx)
			self._overlay.mostrar_mensaje(tx)
			return

		if cmd.tipo == TipoComando.MENSAJE_VOZ and cmd.detalle:
			hablar(str(cmd.detalle))
			self._overlay.mostrar_mensaje(str(cmd.detalle))
			return

		if cmd.tipo == TipoComando.MENSAJE_SIN_VOZ and cmd.detalle:
			self._overlay.mostrar_mensaje(str(cmd.detalle))
			return

		if cmd.tipo == TipoComando.YOUTUBE_PLAY_PAUSE:
			youtube_play_pause_tecla_k()
			self._overlay.mostrar_mensaje("Play / pausa (tecla K)\n¿Foco en el navegador?")
			return

		if cmd.tipo == TipoComando.MODO_PROGRAMADOR:
			items = self._config.get("modo_programador")
			if not isinstance(items, list):
				items = ["msedge", "cursor"]
			for it in items:
				if isinstance(it, str) and it.strip():
					_abrir_en_windows(it.strip())
			self._overlay.mostrar_mensaje("Modo programador")
			return

		if cmd.tipo == TipoComando.VOLUMEN_ABSOLUTO and cmd.detalle:
			try:
				n = int(cmd.detalle)
			except ValueError:
				n = 50
			try:
				volumen_establecer_porcentaje(n)
				self._overlay.mostrar_mensaje(f"Volumen al {n} %")
			except ImportError:
				QMessageBox.warning(
					self,
					"Volumen",
					"Para «volumen a N» instala: pip install pycaw==20251023",
				)
			except OSError:
				self._overlay.mostrar_mensaje("Volumen a %: solo en Windows")
			except Exception as e:
				QMessageBox.warning(self, "Volumen", str(e))
			return

		if cmd.tipo == TipoComando.ABRIR_APP and cmd.detalle:
			_abrir_en_windows(cmd.detalle)
			self._overlay.mostrar_mensaje(f"Abriendo: {cmd.detalle}")
			return

		self._overlay.mostrar_mensaje(f"Entendido: {texto_original[:80]}…")


def main() -> None:
	app = QApplication(sys.argv)
	app.setStyle("Fusion")
	app.setStyleSheet(estilo_global_qss())
	w = VentanaPrincipal()
	w.show()
	sys.exit(app.exec())


if __name__ == "__main__":
	main()
