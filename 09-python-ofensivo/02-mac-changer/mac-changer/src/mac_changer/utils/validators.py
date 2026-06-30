#!/usr/bin/env python3

import re


def is_valid_mac(mac: str) -> bool:
    """Valida que una dirección MAC tenga el formato XX:XX:XX:XX:XX:XX.

    Args:
        mac: Dirección MAC a validar.

    Returns:
        True si el formato es válido, False en caso contrario.
    """
    return bool(re.match(r"^([a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2}$", mac))


def is_valid_interface(interface: str) -> bool:
    """Valida que el nombre de la interfaz de red sea un identificador conocido.

    Acepta interfaces clásicas (eth, wlan) y nombres predictables de systemd
    (ens, eno, enp, wlp), así como la interfaz de loopback (lo).

    Args:
        interface: Nombre de la interfaz de red a validar.

    Returns:
        True si el nombre es reconocido, False en caso contrario.
    """
    pattern = r"^(eth\d+|ens\d+|eno\d+|enp\d+s\d+(\w+)?|wlan\d+|wlp\d+s\d+(\w+)?|lo)$"
    return bool(re.match(pattern, interface))
