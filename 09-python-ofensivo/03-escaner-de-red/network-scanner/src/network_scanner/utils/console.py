#!/usr/bin/env python3
"""Consola de Rich compartida por todo el proyecto.

Se centraliza una unica instancia para que todos los modulos (CLI, core,
manejo de señales) escriban a la misma consola y no pisen la salida en
vivo de un `Progress`/`Live` activo con `print()` normales.
"""

from rich.console import Console

console = Console()
