# La Biblioteca `requests` en Python: HTTP for Humans

## Introducción

`requests` es la biblioteca más popular del ecosistema Python para realizar solicitudes HTTP. Fue creada por Kenneth Reitz en 2011 bajo el lema *"HTTP for Humans"*, y su éxito radica precisamente en su diseño: hace que las operaciones HTTP que con `urllib` (la biblioteca incorporada de Python) requerirían varias líneas de código repetitivo y propenso a errores, puedan realizarse en una sola línea clara y legible.

En ciberseguridad, `requests` es prácticamente omnipresente: se usa para interactuar con APIs de herramientas (Shodan, VirusTotal, Burp, Metasploit), para fuzzing de endpoints web, para probar vulnerabilidades en APIs REST, para automatizar login en aplicaciones web, para enviar payloads a servicios HTTP durante tests de penetración, y para consumir datos de fuentes de threat intelligence. Instalar y dominar `requests` es uno de los primeros pasos prácticos en el desarrollo de herramientas de seguridad con Python.

```bash
pip3 install requests
```

## Métodos HTTP Fundamentales

HTTP define un conjunto de **métodos** (también llamados verbos) que indican la acción que se desea realizar sobre un recurso. `requests` expone cada uno de ellos como una función del módulo con el mismo nombre.

```python
import requests

BASE_URL = "https://httpbin.org"   # servicio de prueba de solicitudes HTTP

# GET: obtener un recurso (el más común)
response = requests.get(f"{BASE_URL}/get")

# POST: enviar datos para crear un recurso
response = requests.post(f"{BASE_URL}/post", json={"key": "value"})

# PUT: reemplazar completamente un recurso existente
response = requests.put(f"{BASE_URL}/put", json={"key": "updated_value"})

# PATCH: modificar parcialmente un recurso existente
response = requests.patch(f"{BASE_URL}/patch", json={"field": "new_value"})

# DELETE: eliminar un recurso
response = requests.delete(f"{BASE_URL}/delete")

# HEAD: igual que GET pero solo devuelve los headers, sin el body
# Útil para comprobar si un recurso existe y obtener sus metadatos sin descargarlo
response = requests.head(f"{BASE_URL}/get")

# OPTIONS: consultar qué métodos HTTP acepta un endpoint
response = requests.options(f"{BASE_URL}/get")
print(f"Métodos permitidos: {response.headers.get('Allow')}")
```

## El Objeto `Response`

Cada llamada a un método de `requests` devuelve un objeto `Response` que encapsula toda la información de la respuesta HTTP del servidor. Conocer sus atributos y métodos es tan importante como conocer cómo enviar la solicitud.

```python
import requests

response = requests.get("https://httpbin.org/get")

# ── Código de estado HTTP ─────────────────────────────────────────────
print(f"Código de estado    : {response.status_code}")    # 200, 404, 500, etc.
print(f"Motivo              : {response.reason}")          # OK, Not Found, etc.

# Verificación rápida de éxito (2xx = True, cualquier otro = False)
print(f"¿Petición exitosa?  : {response.ok}")   # True si 200 <= status < 400

# ── Cabeceras de la respuesta ─────────────────────────────────────────
print(f"\nTipo de contenido   : {response.headers.get('Content-Type')}")
print(f"Servidor            : {response.headers.get('Server')}")
print(f"Todas las cabeceras :")
for header, value in response.headers.items():
    print(f"  {header}: {value}")

# ── Contenido de la respuesta ─────────────────────────────────────────
# Como bytes crudos (modo binario)
raw_bytes = response.content
print(f"\nTamaño (bytes)      : {len(raw_bytes)}")

# Como cadena de texto (decodificada automáticamente)
text_content = response.text
print(f"Primeros 100 chars  : {text_content[:100]}")

# Como objeto Python si la respuesta es JSON
json_data = response.json()
print(f"JSON parseado       : {json_data.get('url')}")

# ── URL final (tras posibles redirecciones) ───────────────────────────
print(f"\nURL final           : {response.url}")

# ── Codificación detectada ────────────────────────────────────────────
print(f"Codificación        : {response.encoding}")

# ── Tiempo de respuesta ───────────────────────────────────────────────
print(f"Tiempo de respuesta : {response.elapsed.total_seconds():.3f}s")

# ── Historial de redirecciones ────────────────────────────────────────
if response.history:
    print(f"Redirecciones       : {len(response.history)}")
    for r in response.history:
        print(f"  {r.status_code} → {r.url}")
```

### `raise_for_status()`: Propagación Automática de Errores HTTP

El método `raise_for_status()` lanza una excepción `requests.exceptions.HTTPError` si el código de estado de la respuesta indica un error (4xx para errores del cliente, 5xx para errores del servidor). Es el patrón más limpio para validar el éxito de una solicitud sin tener que comprobar manualmente el código de estado.

```python
import requests

try:
    response = requests.get("https://httpbin.org/status/404")
    response.raise_for_status()   # lanza HTTPError si status >= 400
    print("Solicitud exitosa")
except requests.exceptions.HTTPError as error:
    print(f"Error HTTP: {error}")            # 404 Client Error: NOT FOUND
    print(f"Código: {error.response.status_code}")
```

## Parámetros de Solicitud

### Parámetros de Query String (`params`)

Los parámetros de URL (query string) se pasan como diccionario al argumento `params`. `requests` se encarga automáticamente de codificarlos y añadirlos a la URL.

```python
import requests

# En lugar de construir manualmente la URL:
# https://api.shodan.io/shodan/host/search?key=TOKEN&query=apache&page=1

params = {
    "key"   : "TU_API_KEY_SHODAN",
    "query" : "apache port:80",
    "page"  : 1,
    "facets": "country,org",
}
response = requests.get("https://api.shodan.io/shodan/host/search", params=params)
print(f"URL generada: {response.url}")
# https://api.shodan.io/shodan/host/search?key=TU_API_KEY_SHODAN&query=apache+port%3A80&page=1&facets=country%2Corg
```

### Cuerpo de la Solicitud: `data`, `json` y `files`

Para métodos que envían un cuerpo (POST, PUT, PATCH), `requests` ofrece tres argumentos principales según el formato de los datos:

```python
import requests

# ── data: datos de formulario (application/x-www-form-urlencoded) ─────
# El formato habitual de un formulario HTML estándar
response = requests.post("https://httpbin.org/post", data={
    "username": "admin",
    "password": "S3cr3t!"
})

# ── json: datos en formato JSON (application/json) ────────────────────
# Lo que espera la mayoría de las APIs REST modernas
response = requests.post("https://httpbin.org/post", json={
    "target": "192.168.1.10",
    "ports": [22, 80, 443],
    "scan_type": "full"
})
print(f"Content-Type enviado: {response.request.headers['Content-Type']}")
# application/json

# ── files: carga de archivos (multipart/form-data) ────────────────────
with open("/tmp/reporte.txt", "w") as f:
    f.write("Reporte de prueba")

with open("/tmp/reporte.txt", "rb") as f:
    response = requests.post("https://httpbin.org/post", files={
        "report": ("reporte.txt", f, "text/plain")
        # tupla: (nombre_archivo, objeto_archivo, content_type)
    })
```

### Cabeceras Personalizadas (`headers`)

Manipular las cabeceras de la solicitud es fundamental en ciberseguridad: para suplantar un User-Agent, enviar tokens de autenticación, especificar el tipo de contenido esperado, o simular el comportamiento de un navegador específico.

```python
import requests

# Cabeceras más comunes en herramientas de seguridad
headers = {
    "User-Agent"    : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Authorization" : "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "X-Api-Key"     : "mi_clave_de_api",
    "Accept"        : "application/json",
    "Referer"       : "https://empresa.com/login",
    "X-Forwarded-For": "127.0.0.1",   # intento de bypass de IP filtering
}

response = requests.get("https://httpbin.org/headers", headers=headers)
print(response.json())

# Inspeccionar las cabeceras que realmente se enviaron
print("\nCabeceras enviadas en la solicitud:")
for h, v in response.request.headers.items():
    print(f"  {h}: {v}")
```

## Autenticación

`requests` soporta de forma nativa los esquemas de autenticación más comunes, sin necesidad de construir manualmente los headers de autorización.

```python
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

# ── Autenticación HTTP Basic (usuario:contraseña en Base64) ──────────
response = requests.get(
    "https://httpbin.org/basic-auth/admin/S3cr3t",
    auth=HTTPBasicAuth("admin", "S3cr3t")
)
# Forma alternativa (equivalente, más concisa):
response = requests.get(
    "https://httpbin.org/basic-auth/admin/S3cr3t",
    auth=("admin", "S3cr3t")
)
print(f"Basic Auth: {response.status_code}")   # 200 si las credenciales son correctas

# ── Autenticación HTTP Digest (más segura que Basic) ─────────────────
response = requests.get(
    "https://httpbin.org/digest-auth/auth/admin/S3cr3t",
    auth=HTTPDigestAuth("admin", "S3cr3t")
)
print(f"Digest Auth: {response.status_code}")

# ── Autenticación con Token en header ─────────────────────────────────
# El patrón más habitual en APIs REST modernas (JWT, API keys)
api_token = "mi_token_secreto"
response = requests.get(
    "https://api.ejemplo.com/v1/hosts",
    headers={"Authorization": f"Bearer {api_token}"}
)

# ── Autenticación con API Key como parámetro ──────────────────────────
response = requests.get(
    "https://api.shodan.io/shodan/host/8.8.8.8",
    params={"key": "MI_API_KEY_SHODAN"}
)
```

## Sesiones: `requests.Session`

Un objeto `Session` permite compartir configuración (headers, cookies, autenticación, proxies) entre múltiples solicitudes, sin necesidad de especificarla en cada llamada individual. Además, `Session` reutiliza las conexiones TCP subyacentes mediante *connection pooling*, lo que mejora el rendimiento cuando se realizan muchas solicitudes al mismo servidor.

```python
import requests

# Sin sesión: los headers, cookies y configuración deben repetirse en cada llamada
r1 = requests.get("https://empresa.com/login", headers={"User-Agent": "Mi-Tool/1.0"})
r2 = requests.get("https://empresa.com/dashboard", headers={"User-Agent": "Mi-Tool/1.0"})

# Con sesión: la configuración se comparte automáticamente
with requests.Session() as session:
    # Configuración que aplica a TODAS las solicitudes de esta sesión
    session.headers.update({
        "User-Agent"    : "Mozilla/5.0 (compatible; MiScanner/1.0)",
        "Accept"        : "application/json",
        "Accept-Language": "es-ES,es;q=0.9",
    })

    # Autenticación que aplica a todas las solicitudes
    session.auth = ("admin", "S3cr3t!")

    # Login: la sesión guarda automáticamente la cookie de sesión recibida
    login_response = session.post("https://httpbin.org/post", json={
        "username": "admin",
        "password": "S3cr3t!"
    })
    print(f"Login: {login_response.status_code}")

    # Las solicitudes siguientes incluyen automáticamente la cookie de sesión
    # y todos los headers configurados, sin necesidad de repetirlos
    profile = session.get("https://httpbin.org/get")
    print(f"Perfil: {profile.status_code}")

    # Inspeccionar las cookies de la sesión
    print(f"Cookies en sesión: {dict(session.cookies)}")
```

## Cookies

```python
import requests

# Enviar cookies específicas en una solicitud
cookies = {
    "session_id": "abc123def456",
    "csrftoken"  : "xyz789",
}
response = requests.get("https://httpbin.org/cookies", cookies=cookies)
print(response.json())

# Leer las cookies de la respuesta
response = requests.get("https://httpbin.org/cookies/set?nombre=valor")
print(f"Cookies recibidas: {dict(response.cookies)}")

# Las cookies recibidas se mantienen automáticamente dentro de una Session
with requests.Session() as session:
    session.get("https://httpbin.org/cookies/set?auth_token=secret123")
    print(f"Cookie guardada en sesión: {dict(session.cookies)}")
    # La siguiente solicitud incluirá automáticamente la cookie auth_token
    response = session.get("https://httpbin.org/cookies")
    print(f"Cookies enviadas: {response.json()}")
```

## Timeout: Evitar Bloqueos Indefinidos

Siempre debe especificarse un timeout en las solicitudes de red, para evitar que el programa quede bloqueado indefinidamente ante un servidor que no responde. `requests` acepta un único valor (aplica tanto a la conexión como a la lectura) o una tupla `(connect_timeout, read_timeout)`.

```python
import requests

# Timeout único: aplica a conexión Y a lectura
try:
    response = requests.get("https://httpbin.org/delay/10", timeout=3)
except requests.exceptions.Timeout:
    print("[!] La solicitud superó el tiempo de espera")

# Timeout diferenciado: (tiempo_de_conexión, tiempo_de_lectura)
try:
    response = requests.get(
        "https://httpbin.org/get",
        timeout=(2, 5)   # 2 segundos para conectar, 5 segundos para leer
    )
except requests.exceptions.ConnectTimeout:
    print("[!] No se pudo establecer la conexión en el tiempo esperado")
except requests.exceptions.ReadTimeout:
    print("[!] El servidor tardó demasiado en responder")
```

## Manejo de Redirecciones

Por defecto, `requests` sigue automáticamente las redirecciones HTTP (301, 302, 307, 308). Es posible desactivar este comportamiento o limitar el número de redirecciones, lo que resulta útil en tests de seguridad para analizar el comportamiento de redirección de una aplicación.

```python
import requests

# Seguir redirecciones automáticamente (comportamiento por defecto)
response = requests.get("http://github.com")   # redirige a https://github.com
print(f"URL final: {response.url}")
print(f"Cadena de redirecciones: {[r.status_code for r in response.history]}")

# Desactivar el seguimiento de redirecciones
response = requests.get("http://github.com", allow_redirects=False)
print(f"Estado (sin seguir redirect): {response.status_code}")   # 301
print(f"Location: {response.headers.get('Location')}")           # https://github.com

# Limitar el número máximo de redirecciones
session = requests.Session()
session.max_redirects = 5   # lanza TooManyRedirects si supera este límite
```

## Proxies

`requests` permite enrutar el tráfico a través de proxies HTTP/HTTPS o SOCKS, lo que resulta esencial en ciberseguridad para anonimizar solicitudes, encadenarlas con herramientas como Burp Suite, o capturar el tráfico para análisis.

```python
import requests

# ── Proxy HTTP/HTTPS ──────────────────────────────────────────────────
proxies = {
    "http" : "http://127.0.0.1:8080",    # Burp Suite listener por defecto
    "https": "http://127.0.0.1:8080",
}
response = requests.get("https://httpbin.org/get", proxies=proxies, verify=False)

# ── Proxy SOCKS5 (requiere: pip install requests[socks]) ─────────────
proxies_socks = {
    "http" : "socks5://127.0.0.1:9050",    # Tor
    "https": "socks5://127.0.0.1:9050",
}

# ── Proxy con autenticación ───────────────────────────────────────────
proxies_auth = {
    "https": "http://usuario:contraseña@proxy.empresa.com:8080",
}

# ── Proxy en una sesión (aplica a todas las solicitudes) ─────────────
with requests.Session() as session:
    session.proxies.update(proxies)
    session.verify = False   # desactivar verificación SSL al pasar por Burp
    response = session.get("https://empresa.com/login")
```

## Verificación SSL y Certificados

```python
import requests

# Verificación SSL habilitada por defecto (comportamiento recomendado)
response = requests.get("https://httpbin.org/get")   # verifica el certificado

# Desactivar la verificación SSL (útil en tests con certificados autofirmados)
# Genera un InsecureRequestWarning que puede silenciarse con urllib3
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
response = requests.get("https://192.168.1.10", verify=False)

# Especificar un CA bundle personalizado (para entornos corporativos)
response = requests.get("https://internal.empresa.com", verify="/etc/ssl/certs/ca.pem")

# Autenticación mutua con certificado de cliente
response = requests.get(
    "https://api.secure.com",
    cert=("/path/to/client.pem", "/path/to/client.key")
)

# Inspeccionar el certificado SSL de un servidor
response = requests.get("https://empresa.com")
# El certificado no está directamente en response, pero se puede obtener
# a través del raw socket subyacente para inspección avanzada
```

## Manejo Completo de Excepciones

`requests` organiza sus excepciones en una jerarquía clara bajo `requests.exceptions`, lo que permite capturar tanto errores específicos como categorías amplias de error.

```python
import requests

def safe_request(url, **kwargs):
    """Realiza una solicitud HTTP con manejo robusto de todas las excepciones posibles."""
    try:
        response = requests.get(url, timeout=10, **kwargs)
        response.raise_for_status()   # lanza HTTPError para códigos 4xx y 5xx
        return response

    except requests.exceptions.ConnectionError:
        # No se pudo establecer la conexión: host no alcanzable, DNS fallido, etc.
        print(f"[!] Error de conexión: no se pudo alcanzar {url}")

    except requests.exceptions.ConnectTimeout:
        # El servidor no respondió al intento de conexión en el tiempo especificado
        print(f"[!] Timeout de conexión: {url} no respondió")

    except requests.exceptions.ReadTimeout:
        # La conexión se estableció pero el servidor tardó demasiado en responder
        print(f"[!] Timeout de lectura: {url} tardó demasiado en responder")

    except requests.exceptions.TooManyRedirects:
        # Se superó el número máximo de redirecciones permitidas
        print(f"[!] Demasiadas redirecciones para {url}")

    except requests.exceptions.SSLError as error:
        # Error de SSL/TLS: certificado inválido, expirado, etc.
        print(f"[!] Error SSL en {url}: {error}")

    except requests.exceptions.HTTPError as error:
        # Respuesta con código de error (4xx o 5xx), lanzada por raise_for_status()
        print(f"[!] Error HTTP {error.response.status_code}: {url}")

    except requests.exceptions.RequestException as error:
        # Superclase de todos los errores de requests: captura cualquier error no cubierto arriba
        print(f"[!] Error inesperado en {url}: {error}")

    return None

# Jerarquía de excepciones de requests:
# RequestException
#   ├── ConnectionError
#   │     ├── ProxyError
#   │     └── SSLError
#   ├── HTTPError
#   ├── URLRequired
#   ├── TooManyRedirects
#   └── Timeout
#         ├── ConnectTimeout
#         └── ReadTimeout
```

## Streaming de Respuestas

Para descargar archivos grandes o consumir respuestas de gran tamaño sin cargar todo el contenido en memoria, `requests` soporta el modo **streaming**: los datos del cuerpo de la respuesta se descargan de forma perezosa, en trozos, a medida que se van procesando.

```python
import requests

# stream=True: los datos del body NO se descargan hasta que se accede a ellos
response = requests.get("https://httpbin.org/bytes/10000", stream=True)

# iter_content() itera sobre el body en trozos de N bytes
total_bytes = 0
with open("/tmp/descarga.bin", "wb") as f:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:   # filtrar chunks vacíos (keep-alive)
            f.write(chunk)
            total_bytes += len(chunk)

print(f"Descargados {total_bytes} bytes")

# iter_lines() itera línea por línea (ideal para APIs de streaming como Twitter/X)
response = requests.get("https://httpbin.org/stream/5", stream=True)
for line in response.iter_lines():
    if line:
        print(line.decode("utf-8"))
```

## Inspección de la Solicitud Enviada: `PreparedRequest`

`requests` prepara la solicitud antes de enviarla en un objeto `PreparedRequest`. Acceder a él permite inspeccionar exactamente qué se envió: URL completa, headers, body.

```python
import requests

response = requests.post(
    "https://httpbin.org/post",
    json={"payload": "test"},
    headers={"Authorization": "Bearer token123"}
)

# Inspeccionar la solicitud que fue enviada
req = response.request
print(f"Método    : {req.method}")
print(f"URL       : {req.url}")
print(f"Headers   :")
for h, v in req.headers.items():
    print(f"  {h}: {v}")
print(f"Body      : {req.body}")
```

## Casos de Uso en Ciberseguridad

### Interacción con APIs de Threat Intelligence

```python
import requests

def query_virustotal(file_hash, api_key):
    """Consulta la reputación de un hash en VirusTotal."""
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    headers = {"x-apikey": api_key}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        stats = data["data"]["attributes"]["last_analysis_stats"]
        malicious = stats.get("malicious", 0)
        total = sum(stats.values())
        print(f"Hash: {file_hash}")
        print(f"Detecciones: {malicious}/{total}")
        return data
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Hash {file_hash} no encontrado en VirusTotal")
        return None
```

### Fuzzing de Endpoints Web

```python
import requests

def fuzz_directories(base_url, wordlist_path, extensions=None):
    """Enumera directorios y archivos en un servidor web."""
    extensions = extensions or ["", ".php", ".html", ".txt", ".bak"]
    found = []

    with requests.Session() as session:
        session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; DirFuzz/1.0)"})

        try:
            with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
                words = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"[-] Wordlist no encontrada: {wordlist_path}")
            return []

        for word in words:
            for ext in extensions:
                target = f"{base_url.rstrip('/')}/{word}{ext}"
                try:
                    response = session.get(target, timeout=5, allow_redirects=False)
                    if response.status_code not in (404, 400, 403):
                        found.append((response.status_code, target))
                        print(f"  [{response.status_code}] {target}")
                except requests.exceptions.RequestException:
                    pass

    return found
```

### Detección de Tecnologías por Cabeceras

```python
import requests

def fingerprint_server(url):
    """Identifica el servidor y tecnologías web a partir de las cabeceras HTTP."""
    try:
        response = requests.head(url, timeout=10, verify=False,
                                  headers={"User-Agent": "Mozilla/5.0"})
        headers = response.headers

        fingerprint = {
            "server"        : headers.get("Server"),
            "x_powered_by"  : headers.get("X-Powered-By"),
            "x_aspnet"      : headers.get("X-AspNet-Version"),
            "x_generator"   : headers.get("X-Generator"),
            "via"           : headers.get("Via"),
            "content_type"  : headers.get("Content-Type"),
        }

        print(f"\n[*] Fingerprint de {url}:")
        for key, value in fingerprint.items():
            if value:
                print(f"  {key:<20}: {value}")

        # Detectar cabeceras de seguridad ausentes
        missing_security = []
        security_headers = [
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "X-Frame-Options",
            "X-Content-Type-Options",
        ]
        for sh in security_headers:
            if sh not in headers:
                missing_security.append(sh)

        if missing_security:
            print(f"\n  [!] Cabeceras de seguridad ausentes:")
            for sh in missing_security:
                print(f"    - {sh}")

        return fingerprint

    except requests.exceptions.RequestException as error:
        print(f"[-] Error al analizar {url}: {error}")
        return {}
```

## Buenas Prácticas

Siempre especificar un `timeout` en toda solicitud de red: nunca debe enviarse una solicitud sin timeout en código de producción o en herramientas que pueden ejecutarse en entornos no controlados, ya que un servidor que no responde bloquearía el programa indefinidamente. Usar `raise_for_status()` tras cada solicitud para propagar errores HTTP de forma explícita, en lugar de comprobar manualmente el código de estado.

Para múltiples solicitudes al mismo servidor, usar siempre un objeto `Session`: esto no solo comparte la configuración de headers y autenticación de forma conveniente, sino que además reutiliza las conexiones TCP subyacentes (*connection pooling*), reduciendo la latencia y el overhead de establecer una nueva conexión en cada solicitud. Al enviar datos en formato JSON a APIs REST, usar el argumento `json=` en lugar de `data=json.dumps(...)` + el header `Content-Type` manual: `requests` lo hace automáticamente cuando se usa `json=`.

Desde el punto de vista de la seguridad, verificar siempre los certificados SSL (`verify=True`, que es el default) en código de producción, reservando `verify=False` únicamente para tests con certificados autofirmados y siempre acompañado de `urllib3.disable_warnings()` para evitar que los warnings contaminen la salida del programa. Finalmente, nunca incluir credenciales, tokens o API keys directamente en el código fuente: leerlos desde variables de entorno con `os.environ.get()` o desde un archivo de configuración externo.