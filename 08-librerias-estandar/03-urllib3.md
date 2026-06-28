# La Biblioteca `urllib3` en Python

## Introducción y Relación con `requests`

`urllib3` es la biblioteca de bajo nivel sobre la que se construye `requests`. Cuando se instala `requests` mediante `pip`, `urllib3` se instala automáticamente como su dependencia principal, ya que es `urllib3` quien realmente gestiona las conexiones de red, los pools de conexiones, los reintentos, la verificación SSL y el streaming. `requests` actúa como una capa de abstracción que simplifica la API de `urllib3` haciéndola más amigable.

Esto plantea una pregunta legítima: si `requests` ya es tan cómoda de usar, ¿por qué aprender `urllib3`? La respuesta está en el control y el rendimiento. `urllib3` expone directamente las tuercas y tornillos del protocolo HTTP que `requests` oculta deliberadamente: la gestión manual del pool de conexiones, el control granular de los reintentos, el acceso directo al raw socket de la conexión, o la capacidad de integrar un cliente HTTP personalizado en una herramienta más grande donde `requests` introduciría una dependencia innecesaria. En ciberseguridad, este nivel de control resulta valioso al desarrollar scanners, proxies, o herramientas que interactúan con servicios HTTP no estándar.

```bash
pip3 install urllib3
```

## Pool de Conexiones: el Concepto Central de `urllib3`

El concepto más importante de `urllib3` y que lo diferencia de otras alternativas más simples es el **pool de conexiones** (*connection pool*). En lugar de abrir y cerrar una nueva conexión TCP por cada solicitud HTTP, `urllib3` mantiene un conjunto de conexiones ya establecidas y listas para ser reutilizadas, evitando repetir el overhead del handshake TCP (y del handshake TLS en HTTPS) en cada solicitud.

Hay dos tipos principales de gestores de pool:

**`urllib3.PoolManager`**: el punto de entrada más habitual. Gestiona automáticamente múltiples pools, uno por cada host distinto al que se realicen solicitudes. Es el equivalente a una `Session` de `requests`, pero a nivel más bajo.

**`urllib3.HTTPConnectionPool`** / **`urllib3.HTTPSConnectionPool`**: representan un pool de conexiones a un único host específico. Se usan cuando todas las solicitudes van al mismo host y se quiere el máximo control sobre la configuración de ese pool concreto.

```python
import urllib3

# ── PoolManager: gestiona múltiples hosts automáticamente ────────────
http = urllib3.PoolManager(
    num_pools=10,       # número máximo de pools distintos (uno por host)
    maxsize=5,          # conexiones simultáneas máximas por pool
    timeout=urllib3.Timeout(connect=3.0, read=10.0),
    retries=urllib3.Retry(total=3),
)

# Se pueden hacer solicitudes a distintos hosts y urllib3 reutiliza
# automáticamente las conexiones existentes cuando el host coincide
response1 = http.request("GET", "https://httpbin.org/get")
response2 = http.request("GET", "https://httpbin.org/ip")    # reutiliza la conexión
response3 = http.request("GET", "https://jsonplaceholder.typicode.com/users")  # nuevo pool

# ── HTTPConnectionPool: pool dedicado a un único host ─────────────────
pool = urllib3.HTTPConnectionPool(
    host="192.168.1.10",
    port=80,
    maxsize=5,
    timeout=3.0,
)
response = pool.request("GET", "/api/v1/hosts")
pool.close()
```

## Realizando Solicitudes

La interfaz principal de `urllib3` es el método `request()` del pool, que acepta el método HTTP, la URL (o solo el path si se usa un `ConnectionPool`) y una serie de argumentos opcionales.

```python
import urllib3
import json

http = urllib3.PoolManager()

# ── GET básico ────────────────────────────────────────────────────────
response = http.request("GET", "https://httpbin.org/get")
print(f"Status: {response.status}")         # código HTTP numérico
print(f"Data  : {response.data[:100]}")     # bytes del body

# ── GET con parámetros de query string ────────────────────────────────
response = http.request(
    "GET",
    "https://httpbin.org/get",
    fields={"key": "api_key", "query": "apache port:80", "page": "1"}
    # fields en GET → se codifican automáticamente como query string
)
print(f"URL con params: {response.geturl()}")

# ── POST con datos de formulario ──────────────────────────────────────
response = http.request(
    "POST",
    "https://httpbin.org/post",
    fields={"username": "admin", "password": "S3cr3t!"}
    # fields en POST → multipart/form-data por defecto
)
print(f"POST status: {response.status}")

# ── POST con cuerpo JSON ──────────────────────────────────────────────
payload = {"target": "192.168.1.10", "ports": [22, 80, 443]}
response = http.request(
    "POST",
    "https://httpbin.org/post",
    body=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
print(f"JSON POST status: {response.status}")

# ── Otros métodos HTTP ────────────────────────────────────────────────
response_put    = http.request("PUT",    "https://httpbin.org/put",    body=b"{}")
response_delete = http.request("DELETE", "https://httpbin.org/delete")
response_head   = http.request("HEAD",   "https://httpbin.org/get")
```

## El Objeto `HTTPResponse`

El objeto devuelto por `request()` es un `urllib3.response.HTTPResponse`, que contiene toda la información de la respuesta.

```python
import urllib3
import json as json_module

http = urllib3.PoolManager()
response = http.request("GET", "https://httpbin.org/get")

# ── Código de estado y razón ──────────────────────────────────────────
print(f"Status     : {response.status}")     # 200
print(f"Razón      : {response.reason}")     # OK (puede ser None en algunos servidores)

# ── Cabeceras ─────────────────────────────────────────────────────────
# Las cabeceras son un objeto HTTPHeaderDict (insensible a mayúsculas)
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Server      : {response.headers.get('server')}")   # insensible a mayúsculas

print("Todas las cabeceras:")
for header, value in response.headers.items():
    print(f"  {header}: {value}")

# ── Body como bytes ───────────────────────────────────────────────────
raw_bytes = response.data   # bytes completos del body
print(f"Tamaño (bytes): {len(raw_bytes)}")

# ── Decodificar a texto ───────────────────────────────────────────────
text = response.data.decode("utf-8")
print(f"Body (texto): {text[:100]}")

# ── Parsear como JSON ─────────────────────────────────────────────────
# urllib3 no tiene .json() como requests; hay que parsearlo manualmente
data = json_module.loads(response.data)
print(f"JSON parseado: {data.get('url')}")
```

## Cabeceras Personalizadas

```python
import urllib3

http = urllib3.PoolManager()

# Cabeceras personalizadas: se pasan como diccionario al argumento headers
headers = {
    "User-Agent"    : "MiHerramienta/1.0 (urllib3; Python)",
    "Authorization" : "Bearer eyJhbGciOiJIUzI1NiJ9...",
    "X-Api-Key"     : "mi_clave_de_api",
    "Accept"        : "application/json",
    "X-Forwarded-For": "127.0.0.1",
}

response = http.request("GET", "https://httpbin.org/headers", headers=headers)
data = __import__("json").loads(response.data)
print("Cabeceras recibidas por el servidor:")
for h, v in data["headers"].items():
    print(f"  {h}: {v}")

# Cabeceras a nivel de PoolManager: se aplican a TODAS las solicitudes
http_with_defaults = urllib3.PoolManager(
    headers={
        "User-Agent": "GlobalAgent/1.0",
        "Accept"    : "application/json",
    }
)
```

## Timeout: Control Granular del Tiempo de Espera

`urllib3` distingue entre el **timeout de conexión** (tiempo máximo para establecer la conexión TCP, antes de que llegue el primer byte) y el **timeout de lectura** (tiempo máximo de espera entre bytes consecutivos una vez iniciada la descarga). Esta distinción es más precisa que el único valor que acepta `requests`, y resulta especialmente relevante en herramientas de escaneo donde se espera que muchos hosts no respondan.

```python
import urllib3

# ── Timeout único: aplica por igual a conexión y lectura ─────────────
http_simple = urllib3.PoolManager(timeout=3.0)

# ── Timeout diferenciado con urllib3.Timeout ─────────────────────────
timeout_config = urllib3.Timeout(
    connect=2.0,    # máximo 2 segundos para establecer la conexión TCP
    read=8.0        # máximo 8 segundos esperando bytes del body
)
http = urllib3.PoolManager(timeout=timeout_config)

# ── Timeout por solicitud individual (sobreescribe el del pool) ───────
try:
    response = http.request("GET", "https://httpbin.org/delay/10",
                            timeout=urllib3.Timeout(total=3.0))
except urllib3.exceptions.TimeoutError:
    print("[!] La solicitud excedió el tiempo de espera")

# ── Sin timeout (desaconsejado en producción) ─────────────────────────
http_no_timeout = urllib3.PoolManager(timeout=urllib3.Timeout.DEFAULT_TIMEOUT)
```

## Reintentos Automáticos con `urllib3.Retry`

El sistema de reintentos de `urllib3` es considerablemente más sofisticado que el de `requests` y permite un control muy granular sobre cuándo y cómo se deben reintentar las solicitudes fallidas.

```python
import urllib3

# ── Configuración básica de reintentos ───────────────────────────────
retry_simple = urllib3.Retry(total=3)   # máximo 3 intentos en total

# ── Configuración avanzada de reintentos ─────────────────────────────
retry_config = urllib3.Retry(
    total=5,             # número total máximo de reintentos

    # Reintentos por categoría de fallo
    connect=3,           # reintentos ante fallos de conexión (host no alcanzable)
    read=3,              # reintentos ante fallos de lectura (timeout durante el body)
    status=2,            # reintentos ante respuestas con códigos de error HTTP

    # Códigos de estado que deben provocar un reintento
    status_forcelist=[500, 502, 503, 504],

    # Retroceso exponencial: esperar entre reintentos
    # tiempo_de_espera = backoff_factor * (2 ^ (intento - 1))
    # Con backoff_factor=0.5: 0.5s, 1s, 2s, 4s...
    backoff_factor=0.5,

    # Métodos que pueden reintentarse (por defecto: HEAD, GET, OPTIONS, TRACE)
    # POST no se reintenta por defecto porque no siempre es idempotente
    allowed_methods={"GET", "HEAD", "OPTIONS"},

    # Manejar redirecciones también como parte del reintento
    raise_on_status=False,   # no lanzar excepción tras agotar reintentos
)

http = urllib3.PoolManager(retries=retry_config)

try:
    response = http.request("GET", "https://httpbin.org/status/503")
    print(f"Status final tras reintentos: {response.status}")
except urllib3.exceptions.MaxRetryError as error:
    print(f"[!] Se agotaron los reintentos: {error.reason}")

# ── Deshabilitar reintentos completamente ─────────────────────────────
http_no_retry = urllib3.PoolManager(retries=False)
```

## Manejo de SSL/TLS

`urllib3` ofrece un control muy detallado sobre la verificación de certificados SSL/TLS, incluyendo la posibilidad de especificar CAs personalizadas, certificados de cliente para autenticación mutua, y la versión mínima de TLS aceptada.

```python
import urllib3
import ssl

# ── Verificación SSL habilitada (comportamiento por defecto) ──────────
http_secure = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",   # exigir certificado válido del servidor
    ca_certs=urllib3.util.ssl_.DEFAULT_CERTS,   # usar los CAs del sistema
)

# ── Deshabilitar verificación SSL ─────────────────────────────────────
# Necesario en laboratorios con certificados autofirmados o Burp Suite
# Siempre acompañar con disable_warnings() para no contaminar la salida
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http_no_verify = urllib3.PoolManager(cert_reqs="CERT_NONE")
response = http_no_verify.request("GET", "https://192.168.1.10")

# ── CA Bundle personalizado ───────────────────────────────────────────
# Útil en entornos corporativos con CA interna propia
http_custom_ca = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",
    ca_certs="/etc/ssl/certs/empresa-ca.pem"
)

# ── Autenticación mutua con certificado de cliente ────────────────────
http_client_cert = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",
    cert_file="/path/to/client.pem",
    key_file="/path/to/client.key",
)

# ── Versión mínima de TLS (rechazar TLS 1.0 y 1.1) ───────────────────
context = ssl.create_default_context()
context.minimum_version = ssl.TLSVersion.TLSv1_2   # solo TLS 1.2+
http_tls12 = urllib3.PoolManager(ssl_context=context)

# ── HTTPSConnectionPool para un único host con configuración SSL ──────
https_pool = urllib3.HTTPSConnectionPool(
    host="api.empresa.com",
    port=443,
    cert_reqs="CERT_REQUIRED",
    ca_certs=urllib3.util.ssl_.DEFAULT_CERTS,
    maxsize=5,
)
```

## Streaming de Respuestas

Para descargar archivos grandes o procesar respuestas de gran tamaño sin cargar todo el contenido en memoria, `urllib3` soporta el modo streaming mediante `preload_content=False`. En este modo, el body no se descarga hasta que se lee explícitamente, y puede leerse por fragmentos.

```python
import urllib3

http = urllib3.PoolManager()

# preload_content=False: el body NO se descarga automáticamente
response = http.request(
    "GET",
    "https://httpbin.org/bytes/100000",
    preload_content=False
)

# Leer el body en fragmentos de N bytes para no cargarlo completo en memoria
total_bytes = 0
with open("/tmp/descarga.bin", "wb") as f:
    for chunk in response.stream(amt=4096):   # amt: bytes por fragmento
        f.write(chunk)
        total_bytes += len(chunk)

# Importante: liberar la conexión de vuelta al pool tras leer en streaming
response.release_conn()
print(f"Descargados {total_bytes:,} bytes")

# ── Leer el body completo manualmente tras preload_content=False ──────
response = http.request("GET", "https://httpbin.org/get", preload_content=False)
data = response.read()   # lee todo el body de una vez (como si fuera preload_content=True)
response.release_conn()
print(f"Body completo: {len(data)} bytes")
```

## Proxies

`urllib3` puede enrutar el tráfico a través de proxies HTTP/HTTPS mediante `urllib3.ProxyManager`, el equivalente a `PoolManager` pero a través de un proxy.

```python
import urllib3

# ── Proxy HTTP/HTTPS (Burp Suite, Squid, etc.) ────────────────────────
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxy = urllib3.ProxyManager(
    proxy_url="http://127.0.0.1:8080",    # Burp Suite escucha aquí por defecto
    proxy_headers={"User-Agent": "urllib3-proxy-test"},
    cert_reqs="CERT_NONE",     # Burp usa un certificado autofirmado
    timeout=urllib3.Timeout(connect=5, read=10),
)

try:
    response = proxy.request("GET", "https://httpbin.org/get")
    print(f"Via proxy: {response.status}")
except urllib3.exceptions.ProxyError as error:
    print(f"[!] Error de proxy: {error}")

# ── Proxy con autenticación básica ────────────────────────────────────
import base64

credentials = "usuario:contraseña"
encoded_auth = base64.b64encode(credentials.encode("utf-8")).decode("ascii")
authenticated_proxy = urllib3.ProxyManager(
    proxy_url="http://proxy.empresa.com:3128",
    proxy_headers={"Proxy-Authorization": f"Basic {encoded_auth}"},
)
```

## Manejo de Excepciones

`urllib3` define su propia jerarquía de excepciones, todas bajo `urllib3.exceptions`.

```python
import urllib3

http = urllib3.PoolManager(timeout=3.0, retries=urllib3.Retry(total=2))

def safe_request(url, method="GET", **kwargs):
    """Realiza una solicitud con manejo completo de excepciones de urllib3."""
    try:
        response = http.request(method, url, **kwargs)
        return response

    except urllib3.exceptions.ConnectTimeoutError:
        # No se pudo establecer la conexión TCP en el tiempo especificado
        print(f"[!] ConnectTimeout: {url} no respondió al intento de conexión")

    except urllib3.exceptions.ReadTimeoutError:
        # La conexión se estableció pero no llegaron datos en el tiempo especificado
        print(f"[!] ReadTimeout: {url} no envió datos a tiempo")

    except urllib3.exceptions.NameResolutionError:
        # No se pudo resolver el nombre de host (DNS fallido)
        print(f"[!] DNS Error: no se pudo resolver el hostname de {url}")

    except urllib3.exceptions.NewConnectionError:
        # No se pudo crear una nueva conexión (host inactivo, puerto cerrado)
        print(f"[!] ConnectionError: no se pudo conectar a {url}")

    except urllib3.exceptions.SSLError as error:
        # Error de SSL/TLS: certificado inválido, versión no soportada, etc.
        print(f"[!] SSL Error en {url}: {error}")

    except urllib3.exceptions.MaxRetryError as error:
        # Se agotaron todos los reintentos sin éxito
        print(f"[!] MaxRetryError: se agotaron los reintentos para {url}")
        print(f"    Razón del último fallo: {error.reason}")

    except urllib3.exceptions.ProxyError as error:
        # Error al comunicarse con el proxy
        print(f"[!] ProxyError: {error}")

    except urllib3.exceptions.ProtocolError as error:
        # El servidor respondió con datos que violan el protocolo HTTP
        print(f"[!] ProtocolError en {url}: {error}")

    except urllib3.exceptions.HTTPError as error:
        # Superclase de todos los errores de urllib3
        print(f"[!] HTTPError inesperado en {url}: {error}")

    return None

# Jerarquía de excepciones de urllib3:
# urllib3.exceptions.HTTPError
#   ├── RequestError
#   │     ├── PoolError
#   │     │     └── MaxRetryError
#   │     ├── TimeoutError
#   │     │     ├── ConnectTimeoutError
#   │     │     └── ReadTimeoutError
#   │     ├── ConnectionError
#   │     │     ├── NewConnectionError
#   │     │     ├── NameResolutionError
#   │     │     └── ProxyError
#   │     └── SSLError
#   └── ProtocolError
```

## Autenticación

```python
import urllib3
import base64

http = urllib3.PoolManager()

# ── Autenticación HTTP Basic ──────────────────────────────────────────
# urllib3 no tiene un argumento auth= como requests: hay que construir
# el header manualmente codificando las credenciales en Base64
credentials = f"admin:S3cr3t!"
encoded = base64.b64encode(credentials.encode("utf-8")).decode("ascii")

response = http.request(
    "GET",
    "https://httpbin.org/basic-auth/admin/S3cr3t!",
    headers={"Authorization": f"Basic {encoded}"}
)
print(f"Basic Auth: {response.status}")   # 200 si las credenciales son correctas

# ── Autenticación con Bearer Token (JWT, OAuth2) ──────────────────────
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
response = http.request(
    "GET",
    "https://api.ejemplo.com/v1/users",
    headers={"Authorization": f"Bearer {api_token}"}
)

# ── Autenticación con API Key como header ─────────────────────────────
response = http.request(
    "GET",
    "https://api.shodan.io/shodan/host/8.8.8.8",
    fields={"key": "MI_API_KEY"},   # como query param
    headers={"X-API-Key": "MI_API_KEY"}   # o como header
)
```

## `urllib3` vs `requests`: ¿Cuándo Usar Cada Uno?

La elección entre `urllib3` y `requests` depende del nivel de control que se necesite y del contexto en el que se usa:

**Usar `requests` cuando:**
- El objetivo es interactuar con APIs REST o servicios web de forma rápida y legible.
- Se necesita una interfaz amigable con soporte nativo para JSON, sesiones, autenticación y cookies.
- La herramienta forma parte de un proyecto más grande donde la legibilidad es prioritaria.
- No hay restricciones de dependencias.

**Usar `urllib3` directamente cuando:**
- Se necesita un control granular sobre el pool de conexiones y los reintentos.
- Se está construyendo una librería o herramienta propia que no debe depender de `requests`.
- Se requiere un rendimiento máximo con el mínimo overhead posible.
- Se necesita acceder a funcionalidades de bajo nivel que `requests` no expone directamente.
- Se trabaja con protocolos HTTP no estándar o con formatos de respuesta inusuales.
- Se está haciendo un proxy inverso, un scanner de alta velocidad, o un cliente HTTP embebido en un sistema mayor.

```python
# Comparativa de sintaxis equivalente
import requests
import urllib3
import json

# La misma solicitud POST con JSON en ambas bibliotecas:

# Con requests (más conciso):
r = requests.post("https://httpbin.org/post",
                  json={"key": "value"},
                  headers={"Authorization": "Bearer token"})
data_requests = r.json()

# Con urllib3 (más explícito, más control):
http = urllib3.PoolManager()
r = http.request("POST",
                 "https://httpbin.org/post",
                 body=json.dumps({"key": "value"}).encode("utf-8"),
                 headers={"Content-Type": "application/json",
                          "Authorization": "Bearer token"})
data_urllib3 = json.loads(r.data.decode("utf-8"))
```

## Buenas Prácticas

La buena práctica más importante con `urllib3` es **reutilizar siempre el mismo `PoolManager`** en lugar de crear uno nuevo para cada solicitud. Cada instancia de `PoolManager` mantiene su propio pool de conexiones, y crear una nueva instancia por solicitud elimina por completo la ventaja del pooling, degradando el rendimiento a un nivel incluso peor que el de una conexión TCP nueva por solicitud.

Al trabajar con streaming (`preload_content=False`), siempre llamar a `response.release_conn()` tras terminar de leer el body, para devolver la conexión al pool y permitir su reutilización. Si no se libera la conexión, el pool puede agotarse bajo carga, bloqueando las solicitudes posteriores hasta que alguna conexión sea liberada.

Configurar siempre un `Timeout` diferenciado con `urllib3.Timeout(connect=..., read=...)` en lugar de un único valor numérico, especialmente en herramientas de escaneo donde es habitual que muchos hosts tarden en responder o directamente no respondan: el timeout de conexión suele debería ser bajo (2-3 segundos) para no perder tiempo en hosts inactivos, mientras que el timeout de lectura puede ser más generoso para hosts que responden lentamente.

Finalmente, cuando se desactiva la verificación SSL con `cert_reqs="CERT_NONE"`, llamar siempre a `urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)` antes de realizar solicitudes, para evitar que los warnings de SSL contaminen la salida de la herramienta.