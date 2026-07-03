#!/usr/bin/env python3
"""Motor de descubrimiento de hosts (host discovery) mediante ICMP ping.

Este modulo se encarga de:
1. Expandir un objetivo (IP unica, rango o subred) en una lista de IPs.
2. Lanzar pings concurrentes contra esa lista para detectar hosts activos.
"""

import ipaddress
import subprocess
from concurrent.futures import ThreadPoolExecutor

# Cantidad de hilos usados por el sweep. Un valor alto acelera el escaneo
# de subredes grandes, pero un numero excesivo puede saturar la red local
# o agotar los descriptores de archivo/procesos del sistema.
MAX_THREADS = 100


def host_discovery(target: str) -> None:
    """Envia un unico ping ICMP a `target` e imprime el resultado si responde.

    Args:
        target: Direccion IP (como string) a la que se le hara ping.
    """
    try:
        ping = subprocess.run(
            ["ping", "-c", "1", target], timeout=1, stdout=subprocess.DEVNULL
        )

        if ping.returncode == 0:
            print(f"\n[+] El host {target} esta activo.")
    except subprocess.TimeoutExpired:
        # Host caido, filtrado por firewall o simplemente sin respuesta ICMP
        # dentro del timeout: se ignora en silencio para no ensuciar la salida.
        pass


def ping_sweep(targets: list[str]) -> None:
    """Hace ping a una lista de IPs en paralelo usando un pool de hilos.

    Args:
        targets: Lista de direcciones IP a escanear.
    """
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(host_discovery, targets)


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
