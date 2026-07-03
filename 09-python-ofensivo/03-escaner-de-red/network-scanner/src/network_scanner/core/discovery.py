#!/usr/bin/env python3

import ipaddress
import subprocess
from concurrent.futures import ThreadPoolExecutor


def host_discovery(target):
    try:
        ping = subprocess.run(
            ["ping", "-c", "1", target], timeout=1, stdout=subprocess.DEVNULL
        )

        if ping.returncode == 0:
            print(f"\n[+] El host {target} esta activo.")
    except subprocess.TimeoutExpired:
        pass


def ping_sweep(targets: list):
    max_threads = 100
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        executor.map(host_discovery, targets)


def unpack_ip_range(target: str) -> list:
    # 1. Separamos la IP base y el número final (ej: "192.200.1.1" y "100")
    base_ip_str, end_host_str = target.split("-")

    # 2. Partimos la IP base para sacar los primeros 3 octetos y el inicio
    parts = base_ip_str.split(".")
    base_prefix = ".".join(parts[:3])  # Queda: "192.200.1"
    start_host = int(parts[3])  # Queda: 1
    end_host = int(end_host_str)  # Queda: 100

    # 3. ¡La magia de la list comprehension con f-strings!
    targets = [f"{base_prefix}.{i}" for i in range(start_host, end_host + 1)]

    return targets


def unpack_ip_subnet(subnet: str) -> list:
    network = ipaddress.ip_network(subnet, strict=False)
    targets = [str(ip) for ip in network.hosts()]

    return targets
