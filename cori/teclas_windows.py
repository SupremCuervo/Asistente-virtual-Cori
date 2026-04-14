"""
Simula las teclas de volumen del teclado (solo Windows).
"""

from __future__ import annotations

import ctypes
import sys

VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
# Tecla K: en YouTube (foco en el navegador) alterna reproducir / pausar
VK_K = 0x4B
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_LWIN = 0x5B
VK_C = 0x43
VK_V = 0x56
VK_D = 0x44
VK_S = 0x53
VK_Z = 0x5A
VK_Y = 0x59
VK_L = 0x4C
VK_E = 0x45
VK_MENU = 0x12
VK_TAB = 0x09
KEYEVENTF_KEYUP = 0x0002


def _pulsar_tecla(codigo_vk: int) -> None:
	if sys.platform != "win32":
		return
	user32 = ctypes.windll.user32
	user32.keybd_event(codigo_vk, 0, 0, 0)
	user32.keybd_event(codigo_vk, 0, KEYEVENTF_KEYUP, 0)


def volumen_subir(pasos: int = 2) -> None:
	n = max(1, min(int(pasos), 15))
	for _ in range(n):
		_pulsar_tecla(VK_VOLUME_UP)


def volumen_bajar(pasos: int = 2) -> None:
	n = max(1, min(int(pasos), 15))
	for _ in range(n):
		_pulsar_tecla(VK_VOLUME_DOWN)


def volumen_silenciar() -> None:
	_pulsar_tecla(VK_VOLUME_MUTE)


def _ctrl_tecla(vk_tecla: int) -> None:
	if sys.platform != "win32":
		return
	user32 = ctypes.windll.user32
	user32.keybd_event(VK_CONTROL, 0, 0, 0)
	user32.keybd_event(vk_tecla, 0, 0, 0)
	user32.keybd_event(vk_tecla, 0, KEYEVENTF_KEYUP, 0)
	user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


def copiar_portapapeles_ctrl_c() -> None:
	_ctrl_tecla(VK_C)


def pegar_portapapeles_ctrl_v() -> None:
	_ctrl_tecla(VK_V)


def minimizar_todo_win_d() -> None:
	"""Win + D (mostrar escritorio / minimizar todo)."""
	if sys.platform != "win32":
		return
	user32 = ctypes.windll.user32
	user32.keybd_event(VK_LWIN, 0, 0, 0)
	user32.keybd_event(VK_D, 0, 0, 0)
	user32.keybd_event(VK_D, 0, KEYEVENTF_KEYUP, 0)
	user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)


def captura_recorte_win_shift_s() -> None:
	"""Win + Shift + S (recorte de pantalla en Windows 10+)."""
	if sys.platform != "win32":
		return
	user32 = ctypes.windll.user32
	user32.keybd_event(VK_LWIN, 0, 0, 0)
	user32.keybd_event(VK_SHIFT, 0, 0, 0)
	user32.keybd_event(VK_S, 0, 0, 0)
	user32.keybd_event(VK_S, 0, KEYEVENTF_KEYUP, 0)
	user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)
	user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)


def deshacer_ctrl_z() -> None:
	_ctrl_tecla(VK_Z)


def rehacer_ctrl_y() -> None:
	_ctrl_tecla(VK_Y)


def bloquear_pantalla_win_l() -> None:
	"""Win + L (bloquear sesión / pantalla de bloqueo)."""
	if sys.platform != "win32":
		return
	user32 = ctypes.windll.user32
	user32.keybd_event(VK_LWIN, 0, 0, 0)
	user32.keybd_event(VK_L, 0, 0, 0)
	user32.keybd_event(VK_L, 0, KEYEVENTF_KEYUP, 0)
	user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)


def explorador_archivos_win_e() -> None:
	"""Win + E (Explorador de archivos)."""
	if sys.platform != "win32":
		return
	user32 = ctypes.windll.user32
	user32.keybd_event(VK_LWIN, 0, 0, 0)
	user32.keybd_event(VK_E, 0, 0, 0)
	user32.keybd_event(VK_E, 0, KEYEVENTF_KEYUP, 0)
	user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)


def siguiente_ventana_alt_tab() -> None:
	"""Alt + Tab una vez (cambiar de ventana)."""
	if sys.platform != "win32":
		return
	user32 = ctypes.windll.user32
	user32.keybd_event(VK_MENU, 0, 0, 0)
	user32.keybd_event(VK_TAB, 0, 0, 0)
	user32.keybd_event(VK_TAB, 0, KEYEVENTF_KEYUP, 0)
	user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)


def youtube_play_pause_tecla_k() -> None:
	"""
	Envía una pulsación de «K» (atajo de YouTube para play/pausa).
	Solo funciona si el foco está en la ventana del navegador con el vídeo.
	"""
	_pulsar_tecla(VK_K)
