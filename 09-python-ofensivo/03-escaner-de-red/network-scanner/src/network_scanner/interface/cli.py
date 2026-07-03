#!/usr/bin/env python3

import signal

import typer

from network_scanner.core import ping_sweep, unpack_ip_range, unpack_ip_subnet
from network_scanner.utils import def_handler, validate_target

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
):
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
        print("[!] No se pudo determinar que ingreso.")


if __name__ == "__main__":
    app()
