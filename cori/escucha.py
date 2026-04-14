"""
Hilo de escucha: Google o Vosk.
1) Primera frase: «Cori» + opcionalmente la orden entera.
2) Si solo activación: ventana + barra de nivel + grabación hasta silencio → segunda frase (sin exigir «Cori»).
"""

from __future__ import annotations

import io
import json
import threading
import wave

import speech_recognition as sr
from PyQt6.QtCore import QThread, pyqtSignal

from cori.comandos_voz import fase_escucha_inicial
from cori.vad_grabar import grabar_hasta_silencio


def _transcribir_vosk(modelo, audio: sr.AudioData) -> str | None:
	"""Convierte un AudioData a texto con un modelo Vosk ya cargado."""
	try:
		from vosk import KaldiRecognizer
	except ImportError:
		return None

	wav_bytes = audio.get_wav_data(convert_rate=16000, convert_width=2)
	wf = wave.open(io.BytesIO(wav_bytes), "rb")
	if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
		return None
	rec = KaldiRecognizer(modelo, wf.getframerate())
	while True:
		data = wf.readframes(4000)
		if len(data) == 0:
			break
		rec.AcceptWaveform(data)
	res = json.loads(rec.FinalResult())
	texto = (res.get("text") or "").strip()
	return texto or None


class HiloEscucha(QThread):
	"""texto, es_segunda_fase (True = ya hubo «Cori», la orden puede ir sin nombre)."""

	texto_recibido = pyqtSignal(str, bool)
	despertar_detectado = pyqtSignal()
	nivel_microfono = pyqtSignal(int)
	escucha_sin_comando = pyqtSignal()
	error_mic = pyqtSignal(str)

	def __init__(
		self,
		idioma: str = "es-ES",
		motor: str = "google",
		ruta_modelo_vosk: str = "",
		mapa_apps: dict[str, str] | None = None,
		mapa_urls: dict[str, str] | None = None,
		personal: dict | None = None,
	) -> None:
		super().__init__()
		self._idioma = idioma
		self._motor = (motor or "google").strip().lower()
		self._ruta_modelo_vosk = ruta_modelo_vosk
		self._mapa_apps = dict(mapa_apps) if mapa_apps else {}
		self._mapa_urls = dict(mapa_urls) if mapa_urls else {}
		self._personal = dict(personal) if personal else {}
		self._correr = threading.Event()
		self._correr.set()
		self._rate_vad = 16000

	def detener(self) -> None:
		self._correr.clear()

	def _reconocer_audio(self, reconocedor: sr.Recognizer, audio: sr.AudioData) -> str | None:
		if self._motor == "vosk" and self._modelo_vosk is not None:
			try:
				return _transcribir_vosk(self._modelo_vosk, audio)
			except Exception as e:
				self.error_mic.emit(f"Vosk: {e}")
				return None
		try:
			return reconocedor.recognize_google(audio, language=self._idioma)
		except sr.UnknownValueError:
			return None
		except sr.RequestError as e:
			self.error_mic.emit(f"Error del servicio de reconocimiento: {e}")
			return None

	def run(self) -> None:
		try:
			reconocedor = sr.Recognizer()
			microfono = sr.Microphone()
		except OSError as e:
			self.error_mic.emit(f"No hay micrófono disponible: {e}")
			return

		modelo_vosk = None
		if self._motor == "vosk":
			if not self._ruta_modelo_vosk:
				self.error_mic.emit(
					"Modo Vosk: define ruta_modelo_vosk en config.json (carpeta del modelo descomprimido)."
				)
				return
			try:
				from vosk import Model
			except ImportError:
				self.error_mic.emit(
					"Falta el paquete vosk. Ejecuta: pip install vosk==0.3.45"
				)
				return
			try:
				modelo_vosk = Model(self._ruta_modelo_vosk)
			except Exception as e:
				self.error_mic.emit(f"No se pudo cargar el modelo Vosk: {e}")
				return

		self._modelo_vosk = modelo_vosk

		try:
			with microfono as fuente:
				reconocedor.adjust_for_ambient_noise(fuente, duration=0.6)
		except Exception as e:
			self.error_mic.emit(f"No se pudo calibrar el micrófono: {e}")
			return

		while self._correr.is_set():
			try:
				with microfono as fuente:
					audio = reconocedor.listen(
						fuente,
						timeout=6,
						phrase_time_limit=7,
					)
			except sr.WaitTimeoutError:
				continue
			except Exception as e:
				if self._correr.is_set():
					self.error_mic.emit(str(e))
				continue

			if not self._correr.is_set():
				break

			texto = self._reconocer_audio(reconocedor, audio)
			if not texto or not self._correr.is_set():
				continue

			fase = fase_escucha_inicial(
				texto,
				self._mapa_apps,
				self._mapa_urls,
				self._personal,
			)
			if fase == "ignorar":
				continue
			if fase == "ejecutar_ya":
				self.texto_recibido.emit(texto.strip(), False)
				continue

			self.despertar_detectado.emit()
			if not self._correr.is_set():
				break

			raw = grabar_hasta_silencio(
				sample_rate=self._rate_vad,
				nivel_callback=lambda n: self.nivel_microfono.emit(int(n)),
			)
			if not self._correr.is_set():
				break
			if not raw:
				self.escucha_sin_comando.emit()
				continue

			audio_cmd = sr.AudioData(raw, self._rate_vad, 2)
			texto2 = self._reconocer_audio(reconocedor, audio_cmd)
			if not texto2 or not texto2.strip():
				self.escucha_sin_comando.emit()
				continue
			if self._correr.is_set():
				self.texto_recibido.emit(texto2.strip(), True)
