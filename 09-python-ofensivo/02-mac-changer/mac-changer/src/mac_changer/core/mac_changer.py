#!/usr/bin/env python3

from rich.console import Console
from mac_changer.utils import is_valid_interface, is_valid_mac

console = Console()


def change_mac_address(interface: str, mac_address: str) -> None:
    """Valida la interfaz y la MAC, y muestra el resultado por pantalla.

    Args:
        interface: Nombre de la interfaz de red.
        mac_address: Nueva dirección MAC a asignar.
    """
    errors = []

    if not is_valid_interface(interface):
        errors.append(f"Interfaz inválida: {interface}")

    if not is_valid_mac(mac_address):
        errors.append(f"MAC inválida: {mac_address}")

    if errors:
        for error in errors:
            console.print(f"[bold red][-][/bold red] {error}")
        return

    console.print(f"[bold green][+][/bold green] Interfaz válida: [cyan]{interface}[/cyan]")
    console.print(f"[bold green][+][/bold green] MAC válida: [cyan]{mac_address}[/cyan]")
