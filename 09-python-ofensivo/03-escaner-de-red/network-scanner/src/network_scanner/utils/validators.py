#!/usr/bin/env python3
"""Validadores del objetivo (target) ingresado por el usuario.

Un `target` puede ser una IP unica, un rango de IPs (ej: "10.0.0.1-50")
o una subred en notacion CIDR (ej: "10.0.0.0/24"). Este modulo detecta
que tipo de target es y valida que su formato sea correcto antes de
que `network_scanner.core.discovery` lo expanda en una lista de IPs.
"""

import ipaddress


def is_valid_ip(ip: str) -> bool:
    """Verifica si `ip` es una direccion IP (v4 o v6) valida.

    Args:
        ip: Cadena a validar como direccion IP.

    Returns:
        True si es una IP valida, False en caso contrario.
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_valid_ip_range(ip_range: str) -> bool:
    """Verifica si `ip_range` tiene el formato "<ip_base>-<host_final>".

    Solo se admite variar el ultimo octeto: la IP base debe ser valida y
    el host final debe ser un entero mayor al ultimo octeto de la IP base
    y no superar 255.

    Args:
        ip_range: Rango a validar, ej: "192.168.0.1-100".

    Returns:
        True si el rango es valido, False en caso contrario.
    """
    try:
        base_ip_str, end_host = ip_range.split("-")

        if not is_valid_ip(base_ip_str):
            return False

        start_host = int(str(base_ip_str).split(".")[-1])
        end_host = int(end_host)

        if start_host < end_host <= 255:
            return True

        return False
    except ValueError:
        # Falla si no hay exactamente un "-" para hacer split, o si
        # `end_host` no es convertible a entero.
        return False


def is_valid_subnet(subnet: str) -> bool:
    """Verifica si `subnet` es una subred valida en notacion CIDR.

    Args:
        subnet: Subred a validar, ej: "192.168.0.0/24".

    Returns:
        True si la subred es valida, False en caso contrario.
    """
    try:
        ipaddress.ip_network(subnet, strict=False)
        return True
    except ValueError:
        return False


def detect_target_type(target: str) -> str:
    """Determina el tipo de `target` en base a su formato, sin validarlo.

    Args:
        target: Cadena ingresada por el usuario (IP, rango o subred).

    Returns:
        "subnet" si contiene "/", "range" si contiene "-", o "ip" en
        cualquier otro caso.
    """
    if "/" in target:
        return "subnet"
    elif "-" in target:
        return "range"
    else:
        return "ip"


def validate_target(target: str) -> tuple[bool, str]:
    """Detecta el tipo de `target` y valida su formato correspondiente.

    Args:
        target: Cadena ingresada por el usuario (IP, rango o subred).

    Returns:
        Tupla `(es_valido, tipo)` donde `tipo` es "ip", "range", "subnet"
        o "Unknown" si no se pudo determinar.
    """
    t = detect_target_type(target)

    if t == "subnet":
        return (is_valid_subnet(target), "subnet")
    elif t == "ip":
        return (is_valid_ip(target), "ip")
    elif t == "range":
        return (is_valid_ip_range(target), "range")
    return (False, "Unknown")
