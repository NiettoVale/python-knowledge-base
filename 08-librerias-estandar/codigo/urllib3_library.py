#!/usr/bin/env python3
import base64
import json
import time

import urllib3

# Silenciar advertencias de InsecureRequestWarning (para cuando verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─────────────────────────────────────────────────────────────────────
# REGLA PRINCIPAL: reutilizar SIEMPRE el mismo PoolManager.
# Crear uno nuevo por solicitud elimina el beneficio del connection pooling.
# ─────────────────────────────────────────────────────────────────────
http = urllib3.PoolManager(
    num_pools=10,  # pools simultáneos máximos (uno por host distinto)
    maxsize=5,  # conexiones simultáneas máximas por pool
)

WIDTH = 65


def section(title):
    print(f"\n{'═' * WIDTH}")
    print(f" {title}")
    print(f"{'═' * WIDTH}")


def sub(title):
    print(f"\n  ── {title}")


# ═════════════════════════════════════════════════════════════
# 1. GET BÁSICO Y OBJETO HTTPResponse
# ═════════════════════════════════════════════════════════════
section("1. GET BÁSICO Y OBJETO HTTPResponse")

# request() devuelve un HTTPResponse con status, headers y data (bytes)
response = http.request("GET", "https://httpbin.org/get")

sub("Información de la respuesta")
print(f"  Código de estado  : {response.status}")
print(f"  Razón             : {response.reason}")
print(f"  Tamaño del body   : {len(response.data):,} bytes")
print(f"  Content-Type      : {response.headers.get('Content-Type')}")
print(f"  Server            : {response.headers.get('Server')}")

# response.data siempre devuelve bytes; hay que decodificar manualmente
body_text = response.data.decode("utf-8")
print(f"\n  Primeros 100 chars del body: {body_text[:100]}")

# urllib3 no tiene .json() como requests → parsear con json.loads()
body_json = json.loads(response.data)
print(f"  URL detectada por httpbin  : {body_json.get('url')}")

sub("Iterar sobre todas las cabeceras de la respuesta")
for header_name, header_value in response.headers.items():
    print(f"  {header_name:<35}: {header_value}")


# ═════════════════════════════════════════════════════════════
# 2. GET CON QUERY STRING (fields=)
# ═════════════════════════════════════════════════════════════
section("2. GET CON PARÁMETROS DE QUERY STRING")

# En GET, fields= codifica los parámetros automáticamente en la URL
# (a diferencia de POST, donde fields= genera multipart/form-data)
response = http.request(
    "GET",
    "https://httpbin.org/get",
    fields={
        "host": "192.168.1.10",
        "port": "443",
        "protocol": "https",
    },
)

body = json.loads(response.data)
sub("Parámetros recibidos por el servidor")
for key, value in body.get("args", {}).items():
    print(f"  {key}: {value}")


# ═════════════════════════════════════════════════════════════
# 3. POST: formulario vs JSON
# ═════════════════════════════════════════════════════════════
section("3. POST — FORMULARIO vs JSON")

sub("3a. POST con datos de formulario (fields= → multipart)")
# fields= en POST genera multipart/form-data, no application/json
response_form = http.request(
    "POST",
    "https://httpbin.org/post",
    fields={
        "username": "admin",
        "action": "login",
        "origin": "192.168.1.10",
    },
)
body_form = json.loads(response_form.data)
print(f"  Content-Type enviado  : {response_form.headers.get('Content-Type', 'N/A')}")
print(f"  Datos recibidos       : {body_form.get('form')}")

sub("3b. POST con JSON (body= + Content-Type manual)")
# urllib3 no tiene json= como requests; hay que serializar y poner el header manualmente
payload = {
    "target": "192.168.1.10",
    "ports": [22, 80, 443, 8443],
    "scan_type": "stealth",
    "timeout": 3,
}
response_json = http.request(
    "POST",
    "https://httpbin.org/post",
    body=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)
body_json_resp = json.loads(response_json.data)
print("  Content-Type enviado  : application/json")
print(f"  JSON recibido por srv : {body_json_resp.get('json')}")


# ═════════════════════════════════════════════════════════════
# 4. CABECERAS PERSONALIZADAS
# ═════════════════════════════════════════════════════════════
section("4. CABECERAS PERSONALIZADAS — FINGERPRINTING")

# Enviar cabeceras personalizadas para simular un navegador específico
# o para añadir tokens de autenticación / claves de API
custom_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/html;q=0.9",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "X-Custom-Tool": "urllib3-demo/1.0",
    "X-Forwarded-For": "10.0.0.1",  # intento de bypass de IP filtering
}

response = http.request("GET", "https://httpbin.org/headers", headers=custom_headers)
received = json.loads(response.data).get("headers", {})

sub("Cabeceras recibidas por el servidor")
for h, v in received.items():
    print(f"  {h:<30}: {v}")


# ═════════════════════════════════════════════════════════════
# 5. TIMEOUT DIFERENCIADO
# ═════════════════════════════════════════════════════════════
section("5. TIMEOUT DIFERENCIADO (connect vs read)")

# urllib3.Timeout separa el tiempo de conexión del tiempo de lectura,
# lo que resulta crítico en herramientas de escaneo:
# - connect corto: no perder tiempo en hosts inactivos
# - read más largo: dar tiempo a hosts lentos en responder
scan_timeout = urllib3.Timeout(
    connect=2.0,  # máximo 2s para establecer la conexión TCP
    read=5.0,  # máximo 5s esperando el body tras conectar
)

http_scan = urllib3.PoolManager(timeout=scan_timeout)

# Simular escaneo de múltiples hosts con timeout controlado
targets = [
    "https://httpbin.org/delay/0",  # responde rápido
    "https://httpbin.org/delay/1",  # responde en 1s (dentro del timeout)
    "https://httpbin.org/delay/10",  # excede el timeout de lectura
]

sub("Resultados de escaneo con timeout de 5s de lectura")
for target in targets:
    start = time.perf_counter()
    try:
        r = http_scan.request("GET", target, timeout=urllib3.Timeout(read=3.0))
        elapsed = time.perf_counter() - start
        print(f"  [OK]      {r.status} — {target:<40} ({elapsed:.2f}s)")
    except urllib3.exceptions.ReadTimeoutError:
        elapsed = time.perf_counter() - start
        print(f"  [TIMEOUT] ReadTimeout — {target:<40} ({elapsed:.2f}s)")
    except urllib3.exceptions.MaxRetryError as e:
        elapsed = time.perf_counter() - start
        print(f"  [ERROR]   {type(e.reason).__name__} — {target:<40} ({elapsed:.2f}s)")


# ═════════════════════════════════════════════════════════════
# 6. REINTENTOS CON urllib3.Retry
# ═════════════════════════════════════════════════════════════
section("6. REINTENTOS AUTOMÁTICOS CON urllib3.Retry")

# Configuración de reintentos con retroceso exponencial:
# El tiempo de espera entre reintentos crece exponencialmente:
# backoff_factor=0.3 → 0.3s, 0.6s, 1.2s, 2.4s...
retry_config = urllib3.Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],  # reintentar ante estos códigos
    backoff_factor=0.3,
    allowed_methods={"GET", "HEAD"},
    raise_on_status=False,  # no lanzar excepción tras agotar reintentos
)

http_retry = urllib3.PoolManager(
    retries=retry_config,
    timeout=urllib3.Timeout(connect=3, read=5),
)

sub("Solicitud con reintentos ante error 503")
response = http_retry.request("GET", "https://httpbin.org/status/503")
print(f"  Status final tras reintentos: {response.status}")

sub("Solicitud exitosa con reintentos configurados")
response = http_retry.request("GET", "https://httpbin.org/status/200")
print(f"  Status: {response.status} — solicitud completada sin necesidad de reintentar")


# ═════════════════════════════════════════════════════════════
# 7. STREAMING: descargar sin cargar todo en memoria
# ═════════════════════════════════════════════════════════════
section("7. STREAMING DE RESPUESTAS")

# preload_content=False: el body no se descarga hasta que se accede a él.
# Fundamental para archivos grandes (wordlists, dumps, capturas PCAP).
response = http.request(
    "GET",
    "https://httpbin.org/bytes/50000",  # ~50 KB de datos aleatorios
    preload_content=False,
)

sub("Descarga en fragmentos de 4 KB")
total_chunks = 0
total_bytes = 0

for chunk in response.stream(amt=4096):
    if chunk:
        total_chunks += 1
        total_bytes += len(chunk)

# IMPORTANTE: liberar la conexión de vuelta al pool tras el streaming
response.release_conn()

print(f"  Fragmentos recibidos : {total_chunks}")
print(f"  Total descargado     : {total_bytes:,} bytes")
print("  Conexión liberada al pool: sí (release_conn() llamado)")


# ═════════════════════════════════════════════════════════════
# 8. SSL: distintos modos de verificación
# ═════════════════════════════════════════════════════════════
section("8. VERIFICACIÓN SSL")

sub("8a. Verificación SSL habilitada (comportamiento por defecto)")
http_secure = urllib3.PoolManager(cert_reqs="CERT_REQUIRED")
try:
    r = http_secure.request("GET", "https://httpbin.org/get")
    print(f"  Solicitud segura completada: {r.status}")
except urllib3.exceptions.SSLError as e:
    print(f"  [!] Error SSL: {e}")

sub("8b. Sin verificación SSL (para laboratorios / Burp Suite)")
# Útil en entornos de pentesting con certificados autofirmados.
# NUNCA usar en producción sin una razón justificada.
http_no_ssl = urllib3.PoolManager(cert_reqs="CERT_NONE")
r = http_no_ssl.request("GET", "https://httpbin.org/get")
print(f"  Solicitud sin verificar SSL: {r.status}")
print("  (InsecureRequestWarning silenciado al inicio del script)")


# ═════════════════════════════════════════════════════════════
# 9. AUTENTICACIÓN HTTP BASIC (manual con Base64)
# ═════════════════════════════════════════════════════════════
section("9. AUTENTICACIÓN HTTP BASIC")

# urllib3 no tiene auth= como requests: hay que construir el header manualmente.
# El esquema Basic codifica "usuario:contraseña" en Base64.
username = "admin"
password = "S3cr3t!"
raw_credentials = f"{username}:{password}"
encoded_credentials = base64.b64encode(raw_credentials.encode("utf-8")).decode("ascii")

auth_headers = {"Authorization": f"Basic {encoded_credentials}"}

response = http.request(
    "GET", f"https://httpbin.org/basic-auth/{username}/{password}", headers=auth_headers
)

sub("Resultado de la autenticación")
print(f"  Header enviado : Authorization: Basic {encoded_credentials}")
print(
    f"  Código recibido: {response.status} {'(autenticación exitosa)' if response.status == 200 else '(fallo)'}"
)
if response.status == 200:
    body = json.loads(response.data)
    print(f"  Autenticado    : {body.get('authenticated')}")
    print(f"  Usuario        : {body.get('user')}")


# ═════════════════════════════════════════════════════════════
# 10. MANEJO COMPLETO DE EXCEPCIONES
# ═════════════════════════════════════════════════════════════
section("10. MANEJO COMPLETO DE EXCEPCIONES")

http_strict = urllib3.PoolManager(
    timeout=urllib3.Timeout(connect=2.0, read=3.0),
    retries=urllib3.Retry(total=1),
)

test_cases = [
    ("URL válida", "https://httpbin.org/status/200"),
    ("Host inexistente", "https://host-que-no-existe-abc123.local"),
    ("Timeout forzado", "https://httpbin.org/delay/10"),
    ("Error 404", "https://httpbin.org/status/404"),
    ("Error 500", "https://httpbin.org/status/500"),
]

sub("Resultados por escenario")
for label, url in test_cases:
    try:
        r = http_strict.request(
            "GET", url, timeout=urllib3.Timeout(connect=2.0, read=2.0)
        )
        print(f"  [HTTP {r.status}]   {label:<25} → {url}")

    except urllib3.exceptions.ConnectTimeoutError:
        print(f"  [ConnTimeout]  {label:<25} → No se estableció la conexión a tiempo")

    except urllib3.exceptions.ReadTimeoutError:
        print(f"  [ReadTimeout]  {label:<25} → Servidor no respondió a tiempo")

    except urllib3.exceptions.MaxRetryError as e:
        reason = type(e.reason).__name__ if e.reason else "desconocida"
        print(f"  [MaxRetry]     {label:<25} → Reintentos agotados ({reason})")

    except urllib3.exceptions.SSLError as e:
        print(f"  [SSL Error]    {label:<25} → {e}")

    except urllib3.exceptions.HTTPError as e:
        print(f"  [HTTPError]    {label:<25} → {e}")


# ═════════════════════════════════════════════════════════════
# 11. HTTPSConnectionPool: pool dedicado a un único host
# ═════════════════════════════════════════════════════════════
section("11. HTTPSConnectionPool — POOL DEDICADO A UN HOST")

# HTTPSConnectionPool es útil cuando todas las solicitudes van al mismo host
# y se quiere el máximo control sobre ese pool concreto.
pool = urllib3.HTTPSConnectionPool(
    host="httpbin.org",
    port=443,
    maxsize=3,
    timeout=urllib3.Timeout(connect=3, read=5),
    retries=urllib3.Retry(total=2),
)

endpoints = ["/get", "/headers", "/ip", "/user-agent"]

sub("Múltiples solicitudes al mismo host reutilizando el pool")
for endpoint in endpoints:
    try:
        # Solo se pasa el PATH, no el host (ya está en el pool)
        r = pool.request("GET", endpoint)
        body = json.loads(r.data)
        print(f"  [{r.status}] {endpoint:<15} → {len(r.data):,} bytes recibidos")
    except urllib3.exceptions.MaxRetryError as e:
        print(f"  [ERROR] {endpoint} → {e}")

pool.close()
print(f"\n  Pool cerrado. Conexiones reutilizadas para {len(endpoints)} solicitudes.")

print(f"\n{'═' * WIDTH}\n")
