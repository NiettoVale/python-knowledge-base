#!/usr/bin/env python3

import typer
from rich.table import Table

from arp_spoofer.core import scan
from arp_spoofer.utils import console

app = typer.Typer()


@app.command()
def main(
    target: str = typer.Option(
        ..., "-t", "--target", help="Host / Rango de IP a escanear"
    )
):
    with console.status(f"Escaneando {target}..."):
        devices = scan(target)

    if not devices:
        console.print(f"[yellow]No se encontraron dispositivos en {target}[/yellow]")
        raise typer.Exit()

    table = Table(title=f"Dispositivos encontrados en {target}")
    table.add_column("IP", style="cyan")
    table.add_column("MAC", style="magenta")

    for device in devices:
        table.add_row(device["ip"], device["mac"])

    console.print(table)


if __name__ == "__main__":
    app()
