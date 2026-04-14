"""
Interpretación de frases en español tras la palabra de activación (Cori).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional

from cori.placeholders_voz import contexto_completo, expandir_placeholders


class TipoComando(Enum):
	NINGUNO = auto()
	SOLO_ACTIVACION = auto()
	MUSICA = auto()
	ABRIR_APP = auto()
	DETENER_ESCUCHA = auto()
	VOLUMEN_SUBIR = auto()
	VOLUMEN_BAJAR = auto()
	VOLUMEN_SILENCIAR = auto()
	VOLUMEN_ABSOLUTO = auto()
	CERRAR_NAVEGADOR = auto()
	ABRIR_URL = auto()
	MODO_PROGRAMADOR = auto()
	YOUTUBE_PLAY_PAUSE = auto()
	COPIA_PORTAPAPELES = auto()
	PEGA_PORTAPAPELES = auto()
	MINIMIZA_TODO = auto()
	CAPTURA_PANTALLA = auto()
	HABLAR_HORA = auto()
	HABLAR_FECHA = auto()
	MENSAJE_VOZ = auto()
	MENSAJE_SIN_VOZ = auto()
	BLOQUEAR_PANTALLA = auto()
	DESHACER = auto()
	REHACER = auto()
	ALT_TAB_VENTANA = auto()
	EXPLORADOR_WIN_E = auto()


@dataclass(frozen=True)
class Comando:
	tipo: TipoComando
	detalle: Optional[str] = None


_VARIANTES_CORI = ("cori", "kori", "corey")
_MUSICA = (
	"música",
	"musica",
	"reproducir música",
	"reproducir musica",
	"pon música",
	"pon musica",
	"ponme música",
	"ponme musica",
	"pone música",
	"pone musica",
	"pon una canción",
	"pon una cancion",
	"pon canción",
	"pon cancion",
	"toca música",
	"toca musica",
)
_DETENER = (
	"para de escuchar",
	"parar de escuchar",
	"detén la escucha",
	"deten la escucha",
	"deja de escuchar",
	"silencio cori",
	"cierra el micrófono",
	"cierra el microfono",
)
_SUBIR_VOLUMEN = (
	"sube mucho el volumen",
	"sube el volumen",
	"subir el volumen",
	"sube volumen",
	"subir volumen",
	"más volumen",
	"mas volumen",
	"súbele al volumen",
	"súbele el volumen",
	"subele al volumen",
	"subele el volumen",
	"aumenta el volumen",
	"aumenta volumen",
	"súbele",
	"subele",
	"sube un poco el volumen",
)
_BAJAR_VOLUMEN = (
	"baja mucho el volumen",
	"baja el volumen",
	"bajar el volumen",
	"baja volumen",
	"bajar volumen",
	"menos volumen",
	"bájale al volumen",
	"bájale el volumen",
	"bajale al volumen",
	"bajale el volumen",
	"reduce el volumen",
	"reduce volumen",
	"baja un poco el volumen",
)
_SILENCIAR_VOLUMEN = (
	"silencia el volumen",
	"silenciar el volumen",
	"silenciar volumen",
	"silencia el audio",
	"silenciar el audio",
	"pon en mute",
	"pon mute",
	"activa el mute",
	"silenciar sonido",
	"quita el sonido",
)
_CERRAR_NAVEGADOR = (
	"cierra el navegador",
	"cierra navegador",
	"cerrar el navegador",
	"cerrar navegador",
	"cierra chrome",
	"cerrar chrome",
	"cierra edge",
	"cerrar edge",
)
_VIDEO_ENTRAR = (
	"entra en video",
	"entrar en video",
	"entra a video",
	"entrar a video",
	"modo video",
	"abre youtube",
	"abrir youtube",
	"entra a youtube",
	"entra en youtube",
)
_MODO_PROGRAMADOR = (
	"modo programador",
	"modo desarrollador",
)
_MINIMIZA_TODO = (
	"minimiza todo",
	"minimizar todo",
	"mostrar escritorio",
	"esconder ventanas",
	"minimiza las ventanas",
	"minimizar las ventanas",
)
_CAPTURA_PANTALLA = (
	"captura de pantalla",
	"captura pantalla",
	"recorte de pantalla",
	"haz una captura",
	"haz captura",
	"hacer captura",
	"screenshot",
)
_HORA_VOZ = (
	"dime la hora",
	"dime qué hora es",
	"dime que hora es",
	"qué hora es",
	"que hora es",
	"la hora por favor",
	"qué hora tenemos",
	"que hora tenemos",
)
_FECHA_VOZ = (
	"qué día es hoy",
	"que dia es hoy",
	"qué fecha es",
	"que fecha es",
	"dime la fecha",
	"dime qué día es",
	"dime que dia es",
	"qué día es",
	"que dia es",
)
_COPIA_VOZ = (
	"copiar",
	"control c",
	"ctrl c",
	"haz copia",
	"copia esto",
)
_PEGA_VOZ = (
	"pegar",
	"control v",
	"ctrl v",
	"pega esto",
	"pégalo",
	"pegalo",
)
_BLOQUEAR_PANTALLA = (
	"bloquea la pantalla",
	"bloquear pantalla",
	"bloquea el equipo",
	"pantalla de bloqueo",
	"bloqueo de pantalla",
	"bloquear el equipo",
)
_DESHACER = (
	"deshacer",
	"deshaz",
	"control z",
	"ctrl z",
	"vuelve atrás",
	"vuelve atras",
	"vuélveme atrás",
	"volveme atras",
)
_REHACER = (
	"rehacer",
	"rehaz",
	"control y",
	"ctrl y",
)
_ALT_TAB_VENTANA = (
	"cambia de ventana",
	"siguiente ventana",
	"otra ventana",
	"pasar de ventana",
	"alt tab",
	"alternar ventana",
	"ventana siguiente",
)
_AJUSTES_WINDOWS = (
	"abre configuración",
	"abrir configuración",
	"abre los ajustes",
	"abrir los ajustes",
	"abre ajustes",
	"abrir ajustes",
	"configuración de windows",
	"configuracion de windows",
	"abre ajustes de windows",
)
_WIN_E_EXPLORADOR = (
	"atajo del explorador",
	"explorador en atajo",
	"atajo explorador",
	"atajo de archivos",
	"explorador rápido",
	"explorador rapido",
	"abre explorador de archivos",
)
_YOUTUBE_PLAY_PAUSE = (
	"pausa el vídeo",
	"pausa el video",
	"pausar el vídeo",
	"pausar el video",
	"pausa vídeo",
	"pausa video",
	"pausar vídeo",
	"pausar video",
	"detén el vídeo",
	"deten el vídeo",
	"detén el video",
	"deten el video",
	"para el vídeo",
	"para el video",
	"reproduce el vídeo",
	"reproduce el video",
	"reproducir el vídeo",
	"reproducir el video",
	"continúa el vídeo",
	"continua el vídeo",
	"continúa el video",
	"continua el video",
	"play vídeo",
	"play video",
	"dale play al vídeo",
	"dale play al video",
)
_ABRIR_PREFIJOS = ("abrir ", "abre ", "abreme ", "abre la ", "abre el ", "abrir la ", "abrir el ", "abrir mi ", "abre mi ")


def _contiene_cori(texto: str) -> bool:
	t = texto.lower()
	return any(v in t for v in _VARIANTES_CORI)


def _normalizar(texto: str) -> str:
	return " ".join(texto.lower().strip().split())


def _contiene_alguna(frase_norm: str, frases: tuple[str, ...]) -> bool:
	for f in sorted(frases, key=len, reverse=True):
		if f in frase_norm:
			return True
	return False


def _tupla_frases_teclas(
	clave: str,
	base: tuple[str, ...],
	frases_teclas_cfg: dict[str, Any],
) -> tuple[str, ...]:
	raw = frases_teclas_cfg.get(clave)
	if not isinstance(raw, list):
		return base
	ex = tuple(_normalizar(str(x)) for x in raw if isinstance(x, str) and str(x).strip())
	return base + ex


def _quiere_copiar(frase_norm: str, frases_copia: tuple[str, ...]) -> bool:
	if _contiene_alguna(frase_norm, frases_copia):
		return True
	if re.search(r"\bcopia\b", frase_norm) and "fotocopia" not in frase_norm:
		return True
	return False


def _quiere_pegar(frase_norm: str, frases_pega: tuple[str, ...]) -> bool:
	if _contiene_alguna(frase_norm, frases_pega):
		return True
	if re.search(r"\bpega\b", frase_norm):
		return True
	return False


def _lista_mensajes_parseados(raw: list[Any] | None) -> list[tuple[str, str, bool]]:
	"""Tuplas (frase_normalizada, plantilla_texto, con_voz), ordenadas por frase más larga."""
	res: list[tuple[str, str, bool]] = []
	for item in raw or []:
		if not isinstance(item, dict):
			continue
		frases = item.get("frases") or item.get("cuando")
		texto = item.get("texto") or item.get("decir") or item.get("mensaje")
		if not isinstance(frases, list) or not texto or not str(texto).strip():
			continue
		voz = item.get("voz", True)
		if isinstance(voz, str):
			voz = voz.strip().lower() in ("1", "true", "si", "sí", "yes")
		voz = bool(voz)
		for f in frases:
			if not isinstance(f, str) or not f.strip():
				continue
			res.append((_normalizar(f), str(texto).strip(), voz))
	res.sort(key=lambda x: -len(x[0]))
	return res


def _match_mensaje_personal(t: str, lista: list[tuple[str, str, bool]]) -> Optional[tuple[str, bool]]:
	for fraz, plantilla, con_voz in lista:
		if fraz in t:
			ctx = contexto_completo()
			tx = expandir_placeholders(plantilla, ctx).strip()
			if tx:
				return (tx, con_voz)
	return None


def _pasos_subir_volumen(frase_norm: str) -> int:
	if "mucho" in frase_norm or "bastante" in frase_norm:
		return 6
	if "un poco" in frase_norm or "poquito" in frase_norm:
		return 1
	return 2


def _pasos_bajar_volumen(frase_norm: str) -> int:
	if "mucho" in frase_norm or "bastante" in frase_norm:
		return 6
	if "un poco" in frase_norm or "poquito" in frase_norm:
		return 1
	return 2


def _porcentaje_volumen_desde_frase(t: str) -> Optional[int]:
	"""
	Detecta «volumen a 60», «pon el volumen al 25 por ciento», etc.
	Debe ir antes de subir/bajar relativos si la frase lleva número explícito.
	"""
	patrones = (
		r"(?:pon(?:me|er)?\s+)?(?:el\s+)?volumen\s+(?:a|al|en|de)\s*(\d{1,3})(?:\s*(?:por\s*ciento|%|porciento))?\b",
		r"volumen\s+(?:a|al|en|de)\s*(\d{1,3})(?:\s*(?:por\s*ciento|%|porciento))?\b",
		r"volumen\s+(\d{1,3})\s*(?:por\s*ciento|%|porciento)\b",
	)
	for patron in patrones:
		m = re.search(patron, t)
		if m:
			n = int(m.group(1))
			return max(0, min(100, n))
	return None


def interpretar(
	frase: str,
	mapa_apps: dict[str, str],
	mapa_urls: dict[str, str] | None = None,
	personal: dict[str, Any] | None = None,
	tras_activacion: bool = False,
) -> Comando:
	"""
	Si tras_activacion es True (ya dijiste «Cori» antes), la orden no tiene que llevar «Cori».
	"""
	if not frase or not str(frase).strip():
		return Comando(TipoComando.NINGUNO)
	if not tras_activacion and not _contiene_cori(frase):
		return Comando(TipoComando.NINGUNO)

	urls = dict(mapa_urls) if mapa_urls else {}
	p = personal or {}
	ft_cfg = p.get("frases_teclas")
	if not isinstance(ft_cfg, dict):
		ft_cfg = {}
	fr_copia = _tupla_frases_teclas("copia", _COPIA_VOZ, ft_cfg)
	fr_pega = _tupla_frases_teclas("pega", _PEGA_VOZ, ft_cfg)
	fr_min = _tupla_frases_teclas("minimiza_todo", _MINIMIZA_TODO, ft_cfg)
	fr_cap = _tupla_frases_teclas("captura", _CAPTURA_PANTALLA, ft_cfg)
	fr_hora = _tupla_frases_teclas("hora", _HORA_VOZ, ft_cfg)
	fr_fecha = _tupla_frases_teclas("fecha", _FECHA_VOZ, ft_cfg)
	fr_bloq = _tupla_frases_teclas("bloquear_pantalla", _BLOQUEAR_PANTALLA, ft_cfg)
	fr_desh = _tupla_frases_teclas("deshacer", _DESHACER, ft_cfg)
	fr_reh = _tupla_frases_teclas("rehacer", _REHACER, ft_cfg)
	fr_alt = _tupla_frases_teclas("alt_tab", _ALT_TAB_VENTANA, ft_cfg)
	fr_ajustes = _tupla_frases_teclas("ajustes_windows", _AJUSTES_WINDOWS, ft_cfg)
	fr_win_e = _tupla_frases_teclas("explorador_win_e", _WIN_E_EXPLORADOR, ft_cfg)
	plant_hora = str(p.get("plantilla_hora_voz") or "").strip() or None
	plant_fecha = str(p.get("plantilla_fecha_voz") or "").strip() or None
	mensajes_lista = _lista_mensajes_parseados(
		p.get("mensajes_voz") if isinstance(p.get("mensajes_voz"), list) else []
	)

	t = _normalizar(frase)

	for d in _DETENER:
		if d in t:
			return Comando(TipoComando.DETENER_ESCUCHA)

	msg = _match_mensaje_personal(t, mensajes_lista)
	if msg is not None:
		tx, con_voz = msg
		if con_voz:
			return Comando(TipoComando.MENSAJE_VOZ, detalle=tx)
		return Comando(TipoComando.MENSAJE_SIN_VOZ, detalle=tx)

	if _contiene_alguna(t, _SILENCIAR_VOLUMEN):
		return Comando(TipoComando.VOLUMEN_SILENCIAR)

	pct = _porcentaje_volumen_desde_frase(t)
	if pct is not None:
		return Comando(TipoComando.VOLUMEN_ABSOLUTO, detalle=str(pct))

	if _contiene_alguna(t, _SUBIR_VOLUMEN):
		return Comando(
			TipoComando.VOLUMEN_SUBIR,
			detalle=str(_pasos_subir_volumen(t)),
		)

	if _contiene_alguna(t, _BAJAR_VOLUMEN):
		return Comando(
			TipoComando.VOLUMEN_BAJAR,
			detalle=str(_pasos_bajar_volumen(t)),
		)

	for m in _MUSICA:
		if m in t:
			return Comando(TipoComando.MUSICA)

	if _contiene_alguna(t, _YOUTUBE_PLAY_PAUSE):
		return Comando(TipoComando.YOUTUBE_PLAY_PAUSE)

	if _contiene_alguna(t, _CERRAR_NAVEGADOR):
		return Comando(TipoComando.CERRAR_NAVEGADOR)

	if _contiene_alguna(t, fr_ajustes):
		return Comando(TipoComando.ABRIR_APP, detalle="ms-settings:")

	if _contiene_alguna(t, fr_win_e):
		return Comando(TipoComando.EXPLORADOR_WIN_E)

	if _contiene_alguna(t, fr_bloq):
		return Comando(TipoComando.BLOQUEAR_PANTALLA)

	if _contiene_alguna(t, fr_desh):
		return Comando(TipoComando.DESHACER)

	if _contiene_alguna(t, fr_reh):
		return Comando(TipoComando.REHACER)

	if _contiene_alguna(t, fr_alt):
		return Comando(TipoComando.ALT_TAB_VENTANA)

	if _quiere_copiar(t, fr_copia):
		return Comando(TipoComando.COPIA_PORTAPAPELES)

	if _quiere_pegar(t, fr_pega):
		return Comando(TipoComando.PEGA_PORTAPAPELES)

	if _contiene_alguna(t, fr_min):
		return Comando(TipoComando.MINIMIZA_TODO)

	if _contiene_alguna(t, fr_cap):
		return Comando(TipoComando.CAPTURA_PANTALLA)

	if _contiene_alguna(t, fr_hora):
		return Comando(TipoComando.HABLAR_HORA, detalle=plant_hora)

	if _contiene_alguna(t, fr_fecha):
		return Comando(TipoComando.HABLAR_FECHA, detalle=plant_fecha)

	if _contiene_alguna(t, _MODO_PROGRAMADOR):
		return Comando(TipoComando.MODO_PROGRAMADOR)

	if _contiene_alguna(t, _VIDEO_ENTRAR):
		return Comando(TipoComando.ABRIR_URL, detalle="youtube")

	for prefijo in _ABRIR_PREFIJOS:
		if prefijo in t:
			idx = t.find(prefijo) + len(prefijo)
			resto = t[idx:].strip()
			if not resto:
				break
			app_cmd = _resolver_app(resto, mapa_apps)
			if app_cmd:
				return Comando(TipoComando.ABRIR_APP, detalle=app_cmd)
			clave_url = _resolver_clave_url(resto, urls)
			if clave_url:
				return Comando(TipoComando.ABRIR_URL, detalle=clave_url)
			return Comando(TipoComando.ABRIR_APP, detalle=resto)

	if tras_activacion:
		return Comando(TipoComando.NINGUNO)
	return Comando(TipoComando.SOLO_ACTIVACION)


def fase_escucha_inicial(
	texto: str,
	mapa_apps: dict[str, str],
	mapa_urls: dict[str, str] | None = None,
	personal: dict[str, Any] | None = None,
) -> str:
	"""
	Tras reconocer la primera frase: «ejecutar_ya» = orden completa de una vez;
	«pedir_comando» = solo activación, hace falta segunda frase; «ignorar» = nada.
	"""
	if not texto or not texto.strip():
		return "ignorar"
	cmd = interpretar(
		texto.strip(),
		mapa_apps,
		mapa_urls,
		personal,
		tras_activacion=False,
	)
	if cmd.tipo == TipoComando.NINGUNO:
		return "ignorar"
	if cmd.tipo == TipoComando.SOLO_ACTIVACION:
		return "pedir_comando"
	return "ejecutar_ya"


def _resolver_app(nombre_usuario: str, mapa_apps: dict[str, str]) -> Optional[str]:
	n = _normalizar(nombre_usuario)
	for etiqueta, comando in mapa_apps.items():
		if _normalizar(etiqueta) == n or _normalizar(etiqueta) in n or n in _normalizar(etiqueta):
			return comando
	return None


def _resolver_clave_url(nombre_usuario: str, mapa_urls: dict[str, str]) -> Optional[str]:
	"""Devuelve la clave del mapa urls (p. ej. «netflix») si coincide con lo dicho."""
	n = _normalizar(nombre_usuario)
	for etiqueta in mapa_urls:
		en = _normalizar(etiqueta)
		if en == n or en in n or n in en:
			return etiqueta
	return None
