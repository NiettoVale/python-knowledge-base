#!/usr/bin/env python3

import typer
from rich.console import Console
from rich.panel import Panel

from mac_changer.core import change_mac_address

app = typer.Typer(help="Herramienta que permite cambiar la MAC del dispositivo.")
console = Console()


@app.command()
def main(
    interface: str = typer.Option(
        ..., "-i", "--interface", help="Nombre de la interfaz de red"
    ),
    mac: str = typer.Option(
        ..., "-m", "--mac", help="Nueva dirección MAC para la interfaz de red"
    ),
):
    console.print(
        Panel(
            "[bold cyan]MAC Changer[/bold cyan] — Modificador de dirección MAC",
            border_style="cyan",
            expand=False,
        )
    )
    change_mac_address(interface, mac)


if __name__ == "__main__":
    app()
