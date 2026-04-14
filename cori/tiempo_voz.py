"""
Textos en español para hora y fecha (TTS).
"""

from __future__ import annotations

from datetime import datetime

_DIAS = (
	"lunes",
	"martes",
	"miércoles",
	"jueves",
	"viernes",
	"sábado",
	"domingo",
)
_MESES = (
	"enero",
	"febrero",
	"marzo",
	"abril",
	"mayo",
	"junio",
	"julio",
	"agosto",
	"septiembre",
	"octubre",
	"noviembre",
	"diciembre",
)


def texto_fecha_larga_desde_datetime(ahora: datetime) -> str:
	dia = _DIAS[ahora.weekday()]
	mes = _MESES[ahora.month - 1]
	return f"Hoy es {dia}, {ahora.day} de {mes} de {ahora.year}"


def texto_hora_para_voz(plantilla: str | None = None) -> str:
	ahora = datetime.now()
	if plantilla and str(plantilla).strip():
		from cori.placeholders_voz import contexto_completo, expandir_placeholders

		ctx = contexto_completo(ahora)
		ctx["hora"] = str(ahora.hour)
		ctx["minutos"] = str(ahora.minute)
		ctx["minuto"] = str(ahora.minute)
		return expandir_placeholders(str(plantilla).strip(), ctx).strip() or (
			f"Son las {ahora.hour} horas, {ahora.minute} minutos"
		)
	return f"Son las {ahora.hour} horas, {ahora.minute} minutos"


def texto_fecha_para_voz(plantilla: str | None = None) -> str:
	ahora = datetime.now()
	if plantilla and str(plantilla).strip():
		from cori.placeholders_voz import contexto_completo, expandir_placeholders

		ctx = contexto_completo(ahora)
		ctx["fecha_larga"] = texto_fecha_larga_desde_datetime(ahora)
		out = expandir_placeholders(str(plantilla).strip(), ctx).strip()
		return out or texto_fecha_larga_desde_datetime(ahora)
	return texto_fecha_larga_desde_datetime(ahora)
