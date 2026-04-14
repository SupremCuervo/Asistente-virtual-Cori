"""
Captura de micrófono con VAD simple: nivel en tiempo real y fin al detectar silencio.
"""

from __future__ import annotations

import math
import struct
import sys
import time
from typing import Callable, Optional

try:
	import audioop
except ImportError:
	audioop = None

try:
	import pyaudio
except ImportError:
	pyaudio = None


def _rms_int16(data: bytes) -> float:
	if len(data) < 2:
		return 0.0
	if audioop is not None:
		return float(audioop.rms(data, 2))
	n = len(data) // 2
	if n == 0:
		return 0.0
	s = 0.0
	for i in range(0, len(data), 2):
		v = struct.unpack_from("<h", data, i)[0]
		s += v * v
	return math.sqrt(s / n)


def _nivel_0_100(rms: float) -> int:
	# Escala heurística: rms típico silencio <200, voz fuerte >3000
	return max(0, min(100, int(math.sqrt(max(rms, 0.0) / 80.0) * 18)))


def grabar_hasta_silencio(
	sample_rate: int = 16000,
	chunk_samples: int = 480,
	silencio_ms: int = 550,
	espera_habla_ms: int = 10000,
	max_grabacion_ms: int = 14000,
	nivel_callback: Optional[Callable[[int], None]] = None,
) -> Optional[bytes]:
	"""
	Abre el micrófono, calibra ruido base, espera voz, graba hasta silencio sostenido.
	Devuelve PCM 16-bit mono little-endian o None si error / timeout sin hablar.
	"""
	if pyaudio is None:
		return None
	pa = pyaudio.PyAudio()
	stream = None
	try:
		stream = pa.open(
			format=pyaudio.paInt16,
			channels=1,
			rate=sample_rate,
			input=True,
			frames_per_buffer=chunk_samples,
		)
	except Exception:
		pa.terminate()
		return None

	chunk_ms = (chunk_samples / float(sample_rate)) * 1000.0
	cal: list[float] = []
	t0 = time.monotonic()

	try:
		while time.monotonic() - t0 < 0.45:
			data = stream.read(chunk_samples, exception_on_overflow=False)
			r = _rms_int16(data)
			cal.append(r)
			if nivel_callback:
				nivel_callback(_nivel_0_100(r))

		ambient = sum(cal) / max(len(cal), 1)
		threshold = max(ambient * 2.6, 420.0)

		t_espera = time.monotonic()
		while time.monotonic() - t_espera < espera_habla_ms / 1000.0:
			data = stream.read(chunk_samples, exception_on_overflow=False)
			r = _rms_int16(data)
			if nivel_callback:
				nivel_callback(_nivel_0_100(r))
			if r >= threshold:
				bloques = [data]
				sil_ms = 0.0
				t_grab = time.monotonic()
				while time.monotonic() - t_grab < max_grabacion_ms / 1000.0:
					data = stream.read(chunk_samples, exception_on_overflow=False)
					r = _rms_int16(data)
					if nivel_callback:
						nivel_callback(_nivel_0_100(r))
					bloques.append(data)
					if r < threshold * 0.72:
						sil_ms += chunk_ms
						if sil_ms >= silencio_ms:
							return b"".join(bloques)
					else:
						sil_ms = 0.0
				return b"".join(bloques)
		return None
	finally:
		if stream is not None:
			try:
				stream.stop_stream()
				stream.close()
			except Exception:
				pass
		pa.terminate()
