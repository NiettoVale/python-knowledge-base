#!/usr/bin/env python3


import ipaddress


def is_valid_ip(ip: str):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_valid_ip_range(ip_range: str):
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
        return False


def is_valid_subnet(subnet: str):
    try:
        ipaddress.ip_network(subnet, strict=False)
        return True
    except ValueError:
        return False


def detect_target_type(target: str):
    if "/" in target:
        return "subnet"
    elif "-" in target:
        return "range"
    else:
        return "ip"


def validate_target(target: str):
    t = detect_target_type(target)

    if t == "subnet":
        return (is_valid_subnet(target), "subnet")
    elif t == "ip":
        return (is_valid_ip(target), "ip")
    elif t == "range":
        return (is_valid_ip_range(target), "range")
    return (False, "Unknown")
