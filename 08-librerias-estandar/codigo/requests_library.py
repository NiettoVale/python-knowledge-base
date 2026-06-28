#!/usr/bin/env python3
import os

import requests

# ─────────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────────
OUTPUT_FILE = "index.html"
URL_PHOTOS = "https://jsonplaceholder.typicode.com/photos"
URL_POSTS = "https://jsonplaceholder.typicode.com/posts"
URL_USERS = "https://jsonplaceholder.typicode.com/users"
URL_INVALID = "https://google.comeasd"

WIDTH = 60


def separator(title):
    print(f"\n{'═' * WIDTH}")
    print(f" {title}")
    print(f"{'═' * WIDTH}")


# ═════════════════════════════════════════════════════════════
# 1. GET BÁSICO: descargar una página y guardarla en disco
# ═════════════════════════════════════════════════════════════
separator("1. GET — Descargar página web")

# requests.get() envía una petición HTTP GET y devuelve un objeto Response.
# Al seguir redirecciones por defecto (301 → 200), obtenemos la página final.
response = requests.get("http://google.com")
print(f"  URL final (tras redirección) : {response.url}")
print(f"  Código de estado             : {response.status_code}")
print(f"  Tipo de contenido            : {response.headers.get('Content-Type')}")
print(f"  Tamaño de la respuesta       : {len(response.content):,} bytes")

# Guardar el HTML en disco solo si el archivo no existe todavía.
# response.text devuelve el contenido decodificado como cadena.
if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"  Archivo guardado             : {OUTPUT_FILE}")
else:
    print(f"  Archivo ya existe, no se sobreescribe: {OUTPUT_FILE}")


# ═════════════════════════════════════════════════════════════
# 2. GET con API REST: leer colección y mostrar primeros items
# ═════════════════════════════════════════════════════════════
separator("2. GET — Consumir API REST (fotos)")

response = requests.get(URL_PHOTOS)
print(f"  Código de estado : {response.status_code}")

# response.json() parsea automáticamente el body JSON a dict/list de Python
photos = response.json()
print(f"  Total de fotos   : {len(photos):,}")

print("\n  Primeras 3 fotos:")
for photo in photos[:3]:
    print(f"    ID {photo['id']:<5} | Album {photo['albumId']} | {photo['title'][:40]}")


# ═════════════════════════════════════════════════════════════
# 3. POST con datos de formulario y cabeceras personalizadas
# ═════════════════════════════════════════════════════════════
separator("3. POST — Enviar datos con cabeceras personalizadas")

# data=payload envía los datos como formulario (application/x-www-form-urlencoded).
# Si la API espera JSON, usar json=payload en su lugar.
payload = {
    "title": "Prueba de Post",
    "body": "Esto es una prueba de prácticas con la librería requests de Python",
    "userId": 1,
}

# Las cabeceras personalizadas se mezclan con las que requests genera automáticamente
custom_headers = {
    "User-Agent": "MiHerramienta/1.0 (Python requests)",
    "Accept": "application/json",
}

response = requests.post(URL_POSTS, data=payload, headers=custom_headers)

print(f"  URL de destino       : {response.url}")
print(f"  Código de estado     : {response.status_code}")

# response.request es el objeto PreparedRequest: lo que realmente se envió
print("\n  Cabeceras enviadas en la solicitud:")
for header, value in response.request.headers.items():
    print(f"    {header}: {value}")

print("\n  Respuesta del servidor:")
print(f"    {response.text[:200]}")


# ═════════════════════════════════════════════════════════════
# 4. POST con JSON: formato preferido por APIs REST modernas
# ═════════════════════════════════════════════════════════════
separator("4. POST — Enviar JSON (json= en vez de data=)")

# json=payload hace tres cosas automáticamente:
#   1. Serializa el dict a JSON
#   2. Codifica a UTF-8
#   3. Agrega Content-Type: application/json al header
json_payload = {
    "title": "Post con JSON",
    "body": "Usando json= en vez de data= para que el Content-Type sea correcto",
    "userId": 1,
}

response = requests.post(URL_POSTS, json=json_payload)
print(f"  Content-Type enviado : {response.request.headers.get('Content-Type')}")
print(f"  Código de estado     : {response.status_code}")
print(f"  Respuesta JSON       : {response.json()}")


# ═════════════════════════════════════════════════════════════
# 5. Excepciones: manejo robusto de errores de red y HTTP
# ═════════════════════════════════════════════════════════════
separator("5. Excepciones en requests")

# raise_for_status() lanza HTTPError si el status es 4xx o 5xx.
# Es el complemento de las excepciones de red: cubre los errores del servidor.
try:
    response = requests.get(URL_INVALID, timeout=3)
    response.raise_for_status()  # levanta HTTPError ante 4xx/5xx

except requests.Timeout:
    # El servidor no respondió en el tiempo especificado
    print("  [!] La petición superó el límite de tiempo de espera")

except requests.HTTPError as http_err:
    # La conexión se estableció, pero el servidor devolvió un error HTTP
    print(f"  [!] Error HTTP: {http_err}")

except requests.ConnectionError:
    # No se pudo establecer la conexión: host inválido, DNS fallido, etc.
    print(f"  [!] Error de conexión: no se pudo resolver '{URL_INVALID}'")

except requests.RequestException as err:
    # Superclase de todos los errores de requests: atrapa cualquier caso no cubierto
    print(f"  [!] Ocurrió un error inesperado: {err}")

else:
    # Solo se ejecuta si no se lanzó ninguna excepción
    print("  [+] La petición se completó sin errores")


# ═════════════════════════════════════════════════════════════
# 6. JSON: procesar una colección de usuarios de la API
# ═════════════════════════════════════════════════════════════
separator("6. JSON — Procesar colección de usuarios")

response = requests.get(URL_USERS)
users = response.json()  # convierte el JSON a lista de dicts de Python

print(f"  Total de usuarios encontrados: {len(users)}")
print()
for user in users:
    user_info = {
        "nombre": user["name"],
        "email": user["email"],
        "web": user["website"],
        "ciudad": user["address"]["city"],
    }
    print(
        f"  [+] {user_info['nombre']:<25} | {user_info['email']:<30} | {user_info['web']}"
    )
