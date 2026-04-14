"""
Carga de configuración desde JSON (no versionado: config.json junto al proyecto).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ruta_config(base: Path | None = None) -> Path:
	raiz = base or Path(__file__).resolve().parent.parent
	return raiz / "config.json"


def cargar_config(base: Path | None = None) -> dict[str, Any]:
	ruta = ruta_config(base)
	por_defecto: dict[str, Any] = {
		"motor_reconocimiento": "google",
		"ruta_modelo_vosk": "",
		"idioma_reconocimiento": "es-ES",
		"url_musica": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
		"aplicaciones": {
			"bloc de notas": "notepad",
			"notas": "notepad",
			"calculadora": "calc",
			"explorador": "explorer",
			"archivos": "explorer",
			"los archivos": "explorer",
			"mis archivos": "explorer",
			"chrome": "chrome",
			"google chrome": "chrome",
			"navegador": "msedge",
			"internet": "msedge",
			"edge": "msedge",
			"microsoft edge": "msedge",
			"firefox": "firefox",
			"visual studio": "devenv",
			"studio": "devenv",
			"visual": "devenv",
			"cursor": "cursor",
			"curso": "cursor",
			"discord": "discord",
			"teams": "ms-teams",
			"whatsapp": "whatsapp",
		},
		"urls": {
			"youtube": "https://www.youtube.com/",
			"video": "https://www.youtube.com/",
			"google": "https://www.google.com/",
			"wikipedia": "https://es.wikipedia.org/",
			"netflix": "https://www.netflix.com/",
			"twitch": "https://www.twitch.tv/",
		},
		"modo_programador": [
			"devenv",
			"cursor",
			"msedge",
		],
		"navegador_procesos_cerrar": [
			"msedge.exe",
			"chrome.exe",
		],
		"frases_teclas": {},
		"plantilla_hora_voz": "",
		"plantilla_fecha_voz": "",
		"mensajes_voz": [
			{
				"frases": [
					"hola cori",
					"buenas cori",
					"buenos días cori",
					"buenos dias cori",
				],
				"texto": "Hola. Te hablo desde el equipo {nombre_pc}.",
				"voz": True,
			},
			{
				"frases": ["gracias cori", "muchas gracias cori", "te lo agradezco cori"],
				"texto": "De nada. Un placer ayudarte en {nombre_pc}.",
				"voz": True,
			},
			{
				"frases": ["adiós cori", "adios cori", "hasta luego cori", "nos vemos cori"],
				"texto": "Hasta luego. Cuando quieras, aquí estaré.",
				"voz": True,
			},
		],
	}
	if not ruta.is_file():
		return por_defecto
	with ruta.open(encoding="utf-8") as f:
		usuario = json.load(f)
	if isinstance(usuario.get("aplicaciones"), dict):
		por_defecto["aplicaciones"].update(usuario["aplicaciones"])
	if isinstance(usuario.get("urls"), dict):
		base_urls = por_defecto.setdefault("urls", {})
		base_urls.update(usuario["urls"])
	if isinstance(usuario.get("modo_programador"), list):
		por_defecto["modo_programador"] = list(usuario["modo_programador"])
	if isinstance(usuario.get("navegador_procesos_cerrar"), list):
		por_defecto["navegador_procesos_cerrar"] = list(usuario["navegador_procesos_cerrar"])
	for clave in ("motor_reconocimiento", "ruta_modelo_vosk", "idioma_reconocimiento", "url_musica"):
		if clave in usuario and usuario[clave] is not None and usuario[clave] != "":
			por_defecto[clave] = usuario[clave]
	if isinstance(usuario.get("frases_teclas"), dict):
		base_ft = por_defecto.setdefault("frases_teclas", {})
		for k, v in usuario["frases_teclas"].items():
			if isinstance(v, list):
				base_ft[str(k)] = list(v)
	if isinstance(usuario.get("mensajes_voz"), list):
		por_defecto["mensajes_voz"] = list(usuario["mensajes_voz"])
	for clave in ("plantilla_hora_voz", "plantilla_fecha_voz"):
		if clave in usuario and isinstance(usuario[clave], str):
			por_defecto[clave] = usuario[clave]
	return por_defecto


def personalizacion_desde_config(cfg: dict) -> dict:
	"""Bloque pasado a interpretar / fase_escucha_inicial (frases y plantillas)."""
	ft = cfg.get("frases_teclas")
	if not isinstance(ft, dict):
		ft = {}
	mv = cfg.get("mensajes_voz")
	if not isinstance(mv, list):
		mv = []
	return {
		"frases_teclas": dict(ft),
		"mensajes_voz": list(mv),
		"plantilla_hora_voz": str(cfg.get("plantilla_hora_voz") or "").strip(),
		"plantilla_fecha_voz": str(cfg.get("plantilla_fecha_voz") or "").strip(),
	}


def guardar_apps_y_urls(
	base: Path | None,
	aplicaciones: dict[str, str],
	urls: dict[str, str],
) -> None:
	"""Compatibilidad: solo apps y urls (no borra frases ni mensajes)."""
	cfg = cargar_config(base)
	cfg["aplicaciones"] = dict(aplicaciones)
	cfg["urls"] = dict(urls)
	_escribir_config(base, cfg)


def _escribir_config(base: Path | None, cfg: dict[str, Any]) -> None:
	ruta = ruta_config(base)
	with ruta.open("w", encoding="utf-8") as f:
		json.dump(cfg, f, indent="\t", ensure_ascii=False)
		f.write("\n")


def guardar_personalizacion_completa(
	base: Path | None,
	aplicaciones: dict[str, str],
	urls: dict[str, str],
	frases_teclas: dict[str, list[str]],
	mensajes_voz: list[dict[str, Any]],
	plantilla_hora_voz: str,
	plantilla_fecha_voz: str,
) -> None:
	cfg = cargar_config(base)
	cfg["aplicaciones"] = dict(aplicaciones)
	cfg["urls"] = dict(urls)
	cfg["frases_teclas"] = dict(frases_teclas)
	cfg["mensajes_voz"] = list(mensajes_voz)
	cfg["plantilla_hora_voz"] = str(plantilla_hora_voz or "")
	cfg["plantilla_fecha_voz"] = str(plantilla_fecha_voz or "")
	_escribir_config(base, cfg)
