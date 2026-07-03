#!/usr/bin/env python3
"""Manejo de señales del sistema operativo para el CLI."""

import os
from types import FrameType


def def_handler(sig: int, frame: FrameType | None) -> None:
    """Handler de SIGINT (Ctrl+C) que corta el programa de forma inmediata.

    Se usa `os._exit(1)` en lugar de `sys.exit()` porque el escaneo corre
    con un `ThreadPoolExecutor`: `sys.exit()` solo lanza `SystemExit` en el
    hilo principal y esperaria a que los hilos trabajadores terminen sus
    pings pendientes, retrasando la salida. `os._exit` termina el proceso
    de inmediato sin flushear buffers ni ejecutar cleanup.

    Args:
        sig: Numero de la señal recibida (siempre `SIGINT` en este caso).
        frame: Frame de ejecucion actual al momento de la interrupcion.
    """
    print("\n[!] Saliendo del programa...\n")
    os._exit(1)
