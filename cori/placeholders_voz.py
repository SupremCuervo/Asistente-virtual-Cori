"""
Placeholders para textos de voz y plantillas ({nombre_pc}, {hora}, …).
"""

from __future__ import annotations

import getpass
import os
import platform
from datetime import datetime

from cori.tiempo_voz import texto_fecha_larga_desde_datetime


def _nombre_equipo() -> str:
	return (os.environ.get("COMPUTERNAME") or platform.node() or "equipo").strip() or "equipo"


def contexto_completo(ahora: datetime | None = None) -> dict[str, str]:
	"""Claves útiles en plantillas y mensajes."""
	dt = ahora or datetime.now()
	fecha_larga = texto_fecha_larga_desde_datetime(dt)
	npc = _nombre_equipo()
	usu = getpass.getuser() or "usuario"
	return {
		"nombre_pc": npc,
		"nombre_equipo": npc,
		"equipo": npc,
		"usuario": usu,
		"hora": str(dt.hour),
		"minutos": str(dt.minute),
		"minuto": str(dt.minute),
		"segundos": str(dt.second),
		"segundo": str(dt.second),
		"hora_corta": dt.strftime("%H:%M"),
		"fecha_larga": fecha_larga,
	}


def expandir_placeholders(plantilla: str, ctx: dict[str, str] | None = None) -> str:
	if not plantilla or not str(plantilla).strip():
		return ""
	base = contexto_completo() if ctx is None else {**contexto_completo(), **ctx}
	out = str(plantilla)
	for clave, valor in base.items():
		out = out.replace("{" + clave + "}", str(valor))
	return out
