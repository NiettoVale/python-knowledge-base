#!/usr/bin/env python3

import typer

from network_scanner.utils import validate_target

app = typer.Typer()


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
            print(f"[+] La IP ({target}) es valida.")
        elif type == "range":
            print(f"[+] El rango ingresado ({target}) es valido.")
        elif type == "subnet":
            print(f"[+] La Subnet ingresada ({target}) es valida.")
    else:
        print("[!] No se pudo determinar que ingreso.")


if __name__ == "__main__":
    app()
