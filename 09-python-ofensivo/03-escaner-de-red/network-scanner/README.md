# network-scanner

Escaner de red simple escrito en Python que descubre hosts activos en una
red local mediante **ping sweep** (ICMP), usando un pool de hilos para
escanear muchas IPs en paralelo.

Soporta tres formatos de target:

- **IP unica**: `192.168.0.1`
- **Rango de IPs**: `192.168.0.1-100` (varia solo el ultimo octeto)
- **Subred CIDR**: `192.168.0.0/24`

## Instalación

```bash
pip install -e .
```

Para desarrollo (incluye `pytest`):

```bash
pip install -e ".[dev]"
```

## Ejecución

```bash
network-scanner --target 192.168.0.1
network-scanner --target 192.168.0.1-100
network-scanner --target 192.168.0.0/24
```

También podés usar el alias corto `-t`, y ver la ayuda con:

```bash
network-scanner --help
```

Presionar `Ctrl+C` en cualquier momento corta el escaneo de forma inmediata.

## Como funciona

1. `network_scanner.utils.validators` detecta y valida el tipo de target
   ingresado (`ip`, `range` o `subnet`).
2. `network_scanner.core.discovery` expande ese target en una lista de IPs
   (`unpack_ip_range` / `unpack_ip_subnet`) y le hace ping a cada una en
   paralelo con `ping_sweep`, imprimiendo los hosts que respondan.

## Tests

```bash
pytest
```
