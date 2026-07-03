#!/usr/bin/env python3
"""Motor de descubrimiento de hosts (host discovery) mediante ICMP ping.

Este modulo se encarga de:
1. Expandir un objetivo (IP unica, rango o subred) en una lista de IPs.
2. Lanzar pings concurrentes contra esa lista para detectar hosts activos,
   mostrando el avance con una barra de progreso de Rich y un resumen final
   en forma de tabla.
"""

import ipaddress
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from network_scanner.utils.console import console

# Cantidad de hilos usados por el sweep. Un valor alto acelera el escaneo
# de subredes grandes, pero un numero excesivo puede saturar la red local
# o agotar los descriptores de archivo/procesos del sistema.
MAX_THREADS = 100


def host_discovery(target: str) -> bool:
    """Envia un unico ping ICMP a `target` y reporta si respondio.

    Se usa `subprocess.run` en lugar de una libreria de sockets crudos
    (como scapy) para no requerir privilegios de root, ya que el binario
    `ping` del sistema ya tiene el capability/setuid necesario.

    Args:
        target: Direccion IP (como string) a la que se le hara ping.

    Returns:
        True si el host respondio al ping dentro del timeout, False si no.
    """
    try:
        ping = subprocess.run(
            ["ping", "-c", "1", target],
            timeout=1,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return ping.returncode == 0
    except subprocess.TimeoutExpired:
        # Host caido, filtrado por firewall o simplemente sin respuesta ICMP
        # dentro del timeout: se trata igual que "no activo".
        return False


def ping_sweep(targets: list[str]) -> list[str]:
    """Hace ping a una lista de IPs en paralelo y muestra el progreso en vivo.

    Al ser una tarea I/O-bound (esperar respuesta de red), los hilos son
    mas eficientes que procesos y evitan el overhead de crear uno por IP.
    Se usa `as_completed` (en vez de `executor.map`) para poder actualizar
    la barra de progreso e imprimir cada host activo apenas se detecta,
    sin esperar a que termine todo el barrido.

    Args:
        targets: Lista de direcciones IP a escanear.

    Returns:
        Lista de IPs que respondieron al ping, ordenadas numericamente.
    """
    active_hosts: list[str] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Escaneando[/bold blue]"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task_id = progress.add_task("scan", total=len(targets))

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            future_to_target = {
                executor.submit(host_discovery, target): target for target in targets
            }

            for future in as_completed(future_to_target):
                target = future_to_target[future]

                if future.result():
                    active_hosts.append(target)
                    # `progress.console.print` (y no `print`/`console.print`
                    # directo) es necesario para no corromper el render en
                    # vivo de la barra de progreso.
                    progress.console.print(f"[bold green][+][/bold green] Host activo: {target}")

                progress.advance(task_id)

    active_hosts.sort(key=ipaddress.ip_address)
    _print_summary(active_hosts, len(targets))

    return active_hosts


def _print_summary(active_hosts: list[str], total_scanned: int) -> None:
    """Imprime la tabla resumen de hosts activos al finalizar el escaneo.

    Args:
        active_hosts: IPs que respondieron al ping, ya ordenadas.
        total_scanned: Cantidad total de IPs que se intentaron escanear.
    """
    console.print()

    if not active_hosts:
        console.print("[yellow]No se encontraron hosts activos.[/yellow]")
        return

    table = Table(title="Resumen del escaneo")
    table.add_column("#", justify="right", style="dim")
    table.add_column("IP", style="bold green")

    for i, host in enumerate(active_hosts, start=1):
        table.add_row(str(i), host)

    console.print(table)
    console.print(f"[dim]{len(active_hosts)}/{total_scanned} hosts activos.[/dim]")


def unpack_ip_range(target: str) -> list[str]:
    """Expande un rango tipo "192.168.0.1-100" a la lista de IPs que contiene.

    Se asume que el rango solo varia el ultimo octeto (host) y que los
    primeros tres octetos son fijos, tal como valida `is_valid_ip_range`.

    Args:
        target: Rango de IPs en formato "<ip_inicial>-<host_final>".

    Returns:
        Lista de IPs, desde la IP inicial hasta el host final (inclusive).
    """
    # 1. Separamos la IP base y el numero final (ej: "192.200.1.1" y "100")
    base_ip_str, end_host_str = target.split("-")

    # 2. Partimos la IP base para sacar los primeros 3 octetos y el inicio
    parts = base_ip_str.split(".")
    base_prefix = ".".join(parts[:3])  # Queda: "192.200.1"
    start_host = int(parts[3])  # Queda: 1
    end_host = int(end_host_str)  # Queda: 100

    # 3. ¡La magia de la list comprehension con f-strings!
    targets = [f"{base_prefix}.{i}" for i in range(start_host, end_host + 1)]

    return targets


def unpack_ip_subnet(subnet: str) -> list[str]:
    """Expande una subred en CIDR (ej: "192.168.0.0/24") a sus IPs de host.

    Usa `ipaddress.ip_network(...).hosts()`, que ya excluye automaticamente
    la direccion de red y de broadcast de la subred.

    Args:
        subnet: Subred en notacion CIDR (ej: "192.168.0.0/24").

    Returns:
        Lista de IPs de host validas dentro de la subred.
    """
    network = ipaddress.ip_network(subnet, strict=False)
    targets = [str(ip) for ip in network.hosts()]

    return targets
