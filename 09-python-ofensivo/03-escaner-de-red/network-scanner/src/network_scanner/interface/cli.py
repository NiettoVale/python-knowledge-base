#!/usr/bin/env python3
"""Interfaz de linea de comandos (CLI) del network-scanner.

Punto de entrada del programa: recibe el target por argumento, lo valida,
lo expande en una lista de IPs segun su tipo y dispara el ping sweep.
"""

import signal

import typer
from rich.panel import Panel

from network_scanner.core import ping_sweep, unpack_ip_range, unpack_ip_subnet
from network_scanner.utils import console, def_handler, validate_target

app = typer.Typer()
signal.signal(signal.SIGINT, def_handler)


@app.command()
def main(
    target: str = typer.Option(
        ...,
        "--target",
        "-t",
        help=(
            "IP o rango de IPs a escanear.\n\n"
            "Formatos:\n"
            "  - IP única: 192.168.0.1\n"
            "  - Rango: 192.168.0.1-100\n"
        ),
    ),
) -> None:
    """Escanea un target de red (IP, rango o subred) mediante ping sweep."""

    console.print(
        Panel(
            "[bold cyan]Network Scanner[/bold cyan] — Escaner de hosts activos.",
            border_style="cyan",
            expand=False,
        )
    )

    is_valid, type = validate_target(target)

    if is_valid:
        if type == "ip":
            ping_sweep([target])
        elif type == "range":
            targets = unpack_ip_range(target)
            ping_sweep(targets)
        elif type == "subnet":
            targets = unpack_ip_subnet(target)
            ping_sweep(targets)
    else:
        console.print("[bold red][!] No se pudo determinar que ingreso.[/bold red]")


if __name__ == "__main__":
    app()
