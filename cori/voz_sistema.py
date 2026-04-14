"""
Síntesis de voz (TTS) en segundo plano para no bloquear la interfaz.
"""

from __future__ import annotations

import threading


def hablar(texto: str) -> None:
	"""Lee el texto en voz alta (hilo daemon). Requiere pyttsx3."""
	if not texto or not str(texto).strip():
		return

	def _run() -> None:
		try:
			import pyttsx3
		except ImportError:
			return
		try:
			motor = pyttsx3.init()
			for v in motor.getProperty("voices") or []:
				nombre = (getattr(v, "name", None) or "").lower()
				if "spanish" in nombre or "español" in nombre or "es-" in nombre:
					motor.setProperty("voice", v.id)
					break
			motor.setProperty("rate", 172)
			motor.say(str(texto).strip())
			motor.runAndWait()
		except Exception:
			pass

	threading.Thread(target=_run, daemon=True).start()
