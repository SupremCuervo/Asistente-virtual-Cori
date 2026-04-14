"""
Volumen maestro de Windows por porcentaje (0–100), vía Core Audio (pycaw).
"""

from __future__ import annotations

import sys


def volumen_establecer_porcentaje(porciento: int) -> None:
	"""
	Fija el volumen del dispositivo de salida predeterminado.
	Requiere: pip install pycaw (y dependencias comtypes, psutil).
	"""
	if sys.platform != "win32":
		raise OSError("volumen_establecer_porcentaje solo está disponible en Windows")
	p = max(0, min(100, int(porciento)))
	try:
		from pycaw.pycaw import AudioUtilities
	except ImportError as e:
		raise ImportError(
			"Instala pycaw: pip install pycaw==20251023"
		) from e
	dispositivo = AudioUtilities.GetSpeakers()
	vol = dispositivo.EndpointVolume
	vol.SetMasterVolumeLevelScalar(p / 100.0, None)
	try:
		vol.SetMute(0, None)
	except Exception:
		pass
