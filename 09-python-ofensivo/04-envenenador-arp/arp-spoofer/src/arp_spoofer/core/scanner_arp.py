#!/usr/bin/env python3


from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import srp


def scan(ip: str) -> list[dict[str, str]]:
    arp_packet = ARP(pdst=ip)
    broadcast_packet = Ether(dst="ff:ff:ff:ff:ff:ff")

    # Operador de composicion, permite unir capas, protocolos, etc.
    arp_packet = broadcast_packet / arp_packet

    # Enviamos la solicitud ARP
    answered, _ = srp(arp_packet, verbose=False, timeout=2)

    devices = [
        {"ip": received.psrc, "mac": received.hwsrc} for _, received in answered
    ]

    return devices
