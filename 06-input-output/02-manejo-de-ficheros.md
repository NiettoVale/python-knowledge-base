# Lectura y Escritura de Archivos en Python

## Introducción

El manejo de archivos es una de las operaciones más frecuentes en cualquier herramienta de software real. En ciberseguridad en particular, prácticamente ningún script de tamaño mediano escapa de la necesidad de leer archivos: diccionarios de contraseñas, listas de hosts, reglas de detección, configuraciones, capturas de red, reportes anteriores. Y del lado de la salida, casi siempre existe la necesidad de escribir resultados, generar reportes, registrar logs o exportar hallazgos en algún formato consumible. Python proporciona una API de manejo de archivos que combina simplicidad, robustez y suficiente control de bajo nivel para cubrir la mayor parte de estos casos con pocas líneas de código.

## La Función `open()`

La función `open()` es el punto de entrada para cualquier operación con archivos en Python. Devuelve un **objeto archivo** (también llamado _file object_ o _stream_) que actúa como intermediario entre el programa y el archivo en disco, y a través del cual se realizan todas las operaciones de lectura y escritura. Su firma completa es:

```python
open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)
```

Los parámetros más relevantes en el uso cotidiano son `file` (la ruta al archivo), `mode` (el modo de apertura), `encoding` (la codificación de caracteres para archivos de texto, siempre recomendado especificarlo explícitamente), y `errors` (el comportamiento ante caracteres no decodificables).

## Modos de Apertura

El modo de apertura determina qué operaciones estarán disponibles sobre el archivo y cómo se comportará `open()` si el archivo ya existe o si no existe. Comprender en profundidad cada modo evita una clase frecuente de errores: sobrescribir accidentalmente un archivo que se quería conservar, o descubrir que no se puede escribir en un archivo abierto en modo lectura.

```python
# Modos de apertura y su comportamiento

'r'   # Lectura de texto. El archivo debe existir. Posición inicial: inicio.
'w'   # Escritura de texto. BORRA el contenido existente si el archivo ya existe.
      # Si el archivo no existe, lo crea.
'a'   # Append (añadir). Escritura al FINAL. Preserva contenido existente.
      # Si el archivo no existe, lo crea.
'x'   # Creación exclusiva. Crea el archivo y falla con FileExistsError si ya existe.
      # Evita sobreescrituras accidentales: ideal cuando se necesita garantizar
      # que el archivo es nuevo.

'r+'  # Lectura Y escritura. El archivo debe existir. No borra el contenido.
'w+'  # Lectura Y escritura. BORRA el contenido existente si el archivo ya existe.
'a+'  # Lectura Y escritura al final. Preserva el contenido existente.

'b'   # Modo binario (se combina con los anteriores: 'rb', 'wb', 'ab', 'rb+', etc.)
      # Trabaja con bytes en lugar de cadenas de texto.
't'   # Modo texto (por defecto, no es necesario especificarlo).
```

La distinción entre **modo texto** y **modo binario** es fundamental:

- En **modo texto**, Python decodifica los bytes del archivo a cadenas de texto (`str`) al leer, y codifica las cadenas a bytes al escribir, utilizando la codificación especificada en el parámetro `encoding`. Además, en modo texto Python normaliza los saltos de línea según la plataforma (en Windows, `\r\n` se convierte a `\n` al leer, y `\n` se convierte a `\r\n` al escribir).
- En **modo binario**, Python trabaja directamente con bytes (`bytes`) sin ninguna decodificación ni conversión de saltos de línea. Este modo es necesario para trabajar con archivos que no son texto plano: imágenes, ejecutables, archivos comprimidos, capturas de red en formato pcap, archivos de firma de antivirus, etc.

```python
# Comparación práctica: mismo archivo, modo texto vs. modo binario
ruta = "/tmp/demo.txt"

with open(ruta, "w", encoding="utf-8") as f:
    f.write("línea 1\nlínea 2\n")

# Modo texto: Python maneja la decodificación y los saltos de línea
with open(ruta, "r", encoding="utf-8") as f:
    contenido_texto = f.read()
print(type(contenido_texto), repr(contenido_texto))
# <class 'str'> 'línea 1\nlínea 2\n'

# Modo binario: Python devuelve bytes crudos, sin procesamiento
with open(ruta, "rb") as f:
    contenido_binario = f.read()
print(type(contenido_binario), repr(contenido_binario))
# <class 'bytes'> b'l\xc3\xadnea 1\nl\xc3\xadnea 2\n'
```

## Manejadores de Contexto: `with open()`

Antes de abordar las operaciones de lectura y escritura en detalle, es esencial entender la forma correcta y moderna de abrir archivos en Python: el **gestor de contexto** mediante la sentencia `with`.

Cuando se abre un archivo con `open()` sin el gestor de contexto, es responsabilidad del programador cerrar explícitamente el archivo llamando al método `close()` cuando ya no se necesita, de lo contrario el archivo permanece abierto, consumiendo recursos del sistema operativo hasta que el recolector de basura de Python lo cierra automáticamente (lo que puede no ocurrir de inmediato). Peor aún, si ocurre una excepción antes de llegar a la llamada a `close()`, el archivo podría quedar abierto indefinidamente.

```python
# Forma INCORRECTA: si ocurre una excepción antes de close(), el archivo
# queda abierto indefinidamente
archivo = open("wordlist.txt", "r", encoding="utf-8")
contenido = archivo.read()   # si esta línea lanza una excepción...
archivo.close()               # ...esta línea nunca se ejecuta
```

La sentencia `with` resuelve este problema de forma elegante: garantiza que, independientemente de cómo salga el bloque de código (finalización normal, excepción, `return`, `break`), el archivo siempre sea cerrado correctamente al salir del bloque, invocando automáticamente el método `__exit__()` del gestor de contexto.

```python
# Forma CORRECTA: el archivo se cierra automáticamente al salir del bloque with,
# haya ocurrido una excepción o no
with open("wordlist.txt", "r", encoding="utf-8") as archivo:
    contenido = archivo.read()
    # Si esta línea lanza una excepción, el archivo se cierra igualmente

# A partir de aquí, el archivo ya está cerrado
print(archivo.closed)   # True
```

Es también posible abrir varios archivos simultáneamente dentro de un mismo `with`, separándolos con coma, lo cual resulta muy conveniente cuando se necesita leer de un archivo y escribir en otro al mismo tiempo:

```python
with open("hosts.txt", "r", encoding="utf-8") as entrada, \
     open("activos.txt", "w", encoding="utf-8") as salida:
    for linea in entrada:
        host = linea.strip()
        if host:
            salida.write(f"{host} -> verificado\n")
```

## Lectura de Archivos

Python ofrece tres métodos principales para leer el contenido de un archivo de texto, cada uno con un comportamiento distinto respecto a cuánto lee en cada llamada y cómo devuelve el resultado.

### `read()`: Leer Todo el Contenido de Una Vez

El método `read()` lee la totalidad del contenido del archivo y lo devuelve como una única cadena de texto. Opcionalmente, puede recibir un argumento entero que indica la cantidad máxima de caracteres (en modo texto) o bytes (en modo binario) a leer en esa llamada, lo cual resulta útil para procesar archivos grandes por trozos sin cargar todo en memoria.

```python
# Leer todo el archivo de una vez
with open("reporte_escaneo.txt", "r", encoding="utf-8") as f:
    contenido_completo = f.read()
print(f"Caracteres leídos: {len(contenido_completo)}")

# Leer en fragmentos de tamaño fijo: útil para archivos grandes
TAMANO_FRAGMENTO = 1024   # 1 KB por fragmento

with open("captura.bin", "rb") as f:
    while True:
        fragmento = f.read(TAMANO_FRAGMENTO)
        if not fragmento:   # fragmento vacío indica que se llegó al final del archivo
            break
        print(f"Procesando {len(fragmento)} bytes...")
```

### `readline()`: Leer una Línea por Vez

El método `readline()` lee y devuelve la siguiente línea del archivo (incluyendo el carácter `\n` al final, salvo en la última línea si esta no termina con salto de línea). Cada llamada a `readline()` avanza la posición de lectura a la siguiente línea. Cuando se llega al final del archivo, devuelve una cadena vacía `""`.

```python
# Leer un archivo línea por línea con readline() explícito
with open("wordlist.txt", "r", encoding="utf-8") as f:
    linea = f.readline()
    while linea:
        palabra = linea.strip()   # strip() elimina el \n y espacios en los extremos
        if palabra:               # ignorar líneas vacías
            print(f"Probando: {palabra}")
        linea = f.readline()
```

### `readlines()`: Leer Todas las Líneas en una Lista

El método `readlines()` lee la totalidad del archivo y devuelve una lista de cadenas, donde cada elemento corresponde a una línea (incluyendo el carácter `\n` al final de cada una). Es conveniente cuando se necesita acceder a líneas por índice o realizar operaciones sobre el conjunto completo de líneas.

```python
# Cargar un diccionario de contraseñas en memoria como lista
with open("rockyou.txt", "r", encoding="utf-8", errors="ignore") as f:
    passwords = [linea.strip() for linea in f.readlines() if linea.strip()]

print(f"Contraseñas cargadas: {len(passwords):,}")
print(f"Primeras 5: {passwords[:5]}")
```

### Iteración Directa sobre el Archivo: La Forma Más Eficiente

La forma más eficiente y pythónica de leer un archivo línea por línea es iterar directamente sobre el objeto archivo en un bucle `for`, sin llamar a ningún método de lectura explícitamente. Este enfoque es equivalente a llamar a `readline()` en cada iteración, pero resulta más legible y es considerablemente más eficiente en memoria que `readlines()`, porque no carga todo el archivo en una lista de una vez, sino que lo va leyendo de a una línea por vez según el bucle lo necesite.

```python
# Forma recomendada: iteración directa sobre el objeto archivo
with open("ips_objetivo.txt", "r", encoding="utf-8") as f:
    for linea in f:
        ip = linea.strip()
        if ip and not ip.startswith("#"):   # ignorar líneas vacías y comentarios
            print(f"Procesando host: {ip}")
```

Esta es la forma preferida para procesar archivos grandes (como un diccionario de contraseñas con millones de entradas) sin riesgo de agotar la memoria del sistema, ya que el archivo se lee progresivamente en lugar de cargarse completo en memoria de una sola vez.

### Control del Puntero de Posición: `seek()` y `tell()`

El objeto archivo mantiene internamente un **puntero de posición** que indica en qué byte del archivo se encuentra actualmente la lectura o escritura. Los métodos `tell()` y `seek()` permiten consultar y manipular este puntero directamente.

`tell()` devuelve la posición actual del puntero (en bytes desde el inicio del archivo). `seek(offset, whence)` desplaza el puntero a una posición específica: si `whence=0` (por defecto), `offset` es la posición absoluta desde el inicio; si `whence=1`, es un desplazamiento relativo a la posición actual; y si `whence=2`, es un desplazamiento relativo al final del archivo (solo disponible en modo binario o para buscar el final).

```python
with open("log_eventos.txt", "r", encoding="utf-8") as f:
    # Leer las primeras dos líneas
    print(f.readline().strip())
    print(f.readline().strip())

    posicion_actual = f.tell()
    print(f"\nPosición actual del puntero: {posicion_actual} bytes")

    # Volver al inicio del archivo
    f.seek(0)
    print(f"\nTras seek(0), primera línea de nuevo:")
    print(f.readline().strip())

    # Ir directamente al final del archivo para leer los últimos bytes
    f.seek(0, 2)   # 2 = desde el final
    tamano_total = f.tell()
    print(f"\nTamaño del archivo: {tamano_total} bytes")
```

El uso de `seek()` resulta especialmente relevante al trabajar con archivos en modo `r+` (lectura y escritura simultánea) o al procesar formatos de archivo binario con una estructura fija en la que es necesario saltar a posiciones específicas.

## Escritura en Archivos

### `write()`: Escribir una Cadena

El método `write()` escribe la cadena que recibe como argumento en el archivo y devuelve la cantidad de caracteres escritos. A diferencia de `print()`, `write()` **no añade automáticamente un salto de línea** al final: si se necesita separar las líneas, el carácter `\n` debe incluirse explícitamente en la cadena que se escribe.

```python
hallazgos = [
    "[CRÍTICO] CVE-2020-1472 — ZeroLogon en 192.168.1.10",
    "[ALTO]    CVE-2021-41773 — Path Traversal en 192.168.1.12",
    "[MEDIO]   CVE-2022-26134 — OGNL Injection en 192.168.1.15",
]

with open("hallazgos.txt", "w", encoding="utf-8") as f:
    f.write("=== REPORTE DE HALLAZGOS ===\n\n")
    for hallazgo in hallazgos:
        caracteres_escritos = f.write(hallazgo + "\n")
        print(f"Escritos {caracteres_escritos} caracteres")
```

### `writelines()`: Escribir una Secuencia de Cadenas

El método `writelines()` recibe cualquier iterable de cadenas y las escribe en el archivo de forma consecutiva, sin añadir ningún separador entre ellas (ni espacios ni saltos de línea). Esto significa que, si se desea que cada cadena quede en una línea separada, el `\n` debe estar incluido en cada cadena del iterable.

```python
# writelines() escribe todos los elementos del iterable SIN separadores entre ellos
# Los \n deben incluirse manualmente en cada cadena

hosts_activos = ["192.168.1.10", "192.168.1.11", "192.168.1.15"]

with open("hosts_activos.txt", "w", encoding="utf-8") as f:
    # Se añade \n a cada host antes de pasarlo a writelines()
    f.writelines(host + "\n" for host in hosts_activos)

# Comparación: diferencia entre write() y writelines()
with open("/tmp/test_write.txt", "w") as f:
    f.write("linea1\nlinea2\n")    # write recibe UNA cadena (con \n incluido)

with open("/tmp/test_writelines.txt", "w") as f:
    f.writelines(["linea1\n", "linea2\n"])   # writelines recibe UNA LISTA de cadenas
```

### Modo `a` (Append): Añadir sin Sobrescribir

Cuando se necesita agregar contenido a un archivo existente sin borrar lo que ya contiene, el modo `"a"` posiciona automáticamente el puntero de escritura al final del archivo al abrirlo. Si el archivo no existe, lo crea. Esta es la diferencia fundamental con el modo `"w"`, que borra el contenido existente.

```python
import datetime

def registrar_evento(ruta_log, nivel, mensaje):
    """Agrega una entrada formateada al archivo de log sin sobrescribir entradas anteriores."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entrada = f"[{timestamp}] [{nivel}] {mensaje}\n"
    with open(ruta_log, "a", encoding="utf-8") as f:
        f.write(entrada)

# Cada llamada agrega una línea al final del archivo, sin borrar las anteriores
registrar_evento("actividad.log", "INFO",  "Escaneo iniciado en 192.168.1.0/24")
registrar_evento("actividad.log", "OK",    "Host 192.168.1.10 activo")
registrar_evento("actividad.log", "WARN",  "Puerto 23 abierto en 192.168.1.10")
registrar_evento("actividad.log", "ERROR", "Tiempo de espera agotado para 192.168.1.20")
```

### Modo `x` (Creación Exclusiva): Evitar Sobrescrituras Accidentales

El modo `"x"` intenta crear el archivo y falla con `FileExistsError` si ya existe. Este comportamiento es el más seguro cuando se genera un reporte o archivo de resultados que no debe sobrescribir otro anterior, ya que obliga al programador a gestionar explícitamente la colisión de nombres.

```python
import os

nombre_reporte = "reporte_q2_2026.md"

try:
    with open(nombre_reporte, "x", encoding="utf-8") as f:
        f.write("# Reporte de Reconocimiento Q2 2026\n")
    print(f"Reporte creado: {nombre_reporte}")
except FileExistsError:
    # El archivo ya existe: se genera un nombre alternativo con timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_alternativo = f"reporte_q2_2026_{timestamp}.md"
    with open(nombre_alternativo, "x", encoding="utf-8") as f:
        f.write("# Reporte de Reconocimiento Q2 2026\n")
    print(f"El reporte ya existía. Creado con nombre alternativo: {nombre_alternativo}")
```

## Archivos Binarios

El modo binario (`"rb"`, `"wb"`, `"ab"`) trabaja con bytes en lugar de cadenas de texto y no aplica ninguna conversión de codificación ni de saltos de línea. Es imprescindible para cualquier archivo que no sea texto plano puro: ejecutables (`.exe`, ELF), imágenes, archivos comprimidos (`.zip`, `.gz`), capturas de red (`.pcap`), archivos de firma (`.sig`), y cualquier formato propietario binario.

```python
# Leer un archivo binario y examinar sus primeros bytes (magic bytes / firma del archivo)
def identificar_tipo_archivo(ruta):
    """Identifica el tipo de archivo a partir de sus primeros bytes (magic bytes)."""
    firmas_conocidas = {
        b"\x7fELF":     "Ejecutable ELF (Linux)",
        b"MZ":          "Ejecutable PE (Windows .exe/.dll)",
        b"\x89PNG":     "Imagen PNG",
        b"PK\x03\x04":  "Archivo ZIP (o .docx/.jar/.apk)",
        b"\xd4\xc3\xb2\xa1": "Captura pcap (little-endian)",
        b"\xa1\xb2\xc3\xd4": "Captura pcap (big-endian)",
        b"JFIF":        "Imagen JPEG",
    }

    with open(ruta, "rb") as f:
        primeros_bytes = f.read(8)   # leer los primeros 8 bytes

    for firma, descripcion in firmas_conocidas.items():
        if primeros_bytes.startswith(firma):
            return descripcion

    return "Tipo desconocido"


# Copiar un archivo binario (útil para extraer o preservar muestras de malware)
def copiar_binario(origen, destino, tamano_bloque=4096):
    """Copia un archivo binario en bloques, sin cargarlo completo en memoria."""
    with open(origen, "rb") as src, open(destino, "wb") as dst:
        while True:
            bloque = src.read(tamano_bloque)
            if not bloque:
                break
            dst.write(bloque)


# Calcular el hash MD5 de un archivo binario para verificar integridad
import hashlib

def calcular_hash(ruta, algoritmo="sha256"):
    """Calcula el hash criptográfico de un archivo sin cargarlo completo en memoria."""
    hasher = hashlib.new(algoritmo)
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):   # bloques de 64 KB
            hasher.update(bloque)
    return hasher.hexdigest()
```

## Trabajo con Rutas: el Módulo `pathlib`

A partir de Python 3.4, el módulo `pathlib` ofrece una alternativa orientada a objetos para el manejo de rutas del sistema de archivos, mucho más intuitiva y portátil que las funciones de `os.path`. La clase `Path` representa una ruta y encapsula operaciones como comprobar si existe, obtener el nombre o la extensión, crear directorios, iterar sobre el contenido de un directorio, o abrir archivos directamente.

```python
from pathlib import Path

# Crear objetos Path
ruta_wordlist = Path("/usr/share/wordlists/rockyou.txt")
ruta_resultados = Path("resultados") / "escaneo_q2" / "hosts.txt"

# Información sobre la ruta
print(ruta_wordlist.name)       # "rockyou.txt"
print(ruta_wordlist.stem)       # "rockyou"      (nombre sin extensión)
print(ruta_wordlist.suffix)     # ".txt"         (extensión)
print(ruta_wordlist.parent)     # /usr/share/wordlists

# Verificaciones
print(ruta_wordlist.exists())   # True si el archivo existe en el sistema
print(ruta_wordlist.is_file())  # True si es un archivo (no un directorio)

# Crear un directorio y todos sus padres automáticamente
ruta_resultados.parent.mkdir(parents=True, exist_ok=True)

# Iterar sobre todos los archivos .txt de un directorio
directorio_logs = Path("/var/log")
if directorio_logs.exists():
    for archivo_log in directorio_logs.glob("*.log"):
        print(archivo_log.name, archivo_log.stat().st_size, "bytes")

# Abrir archivos directamente desde un objeto Path
with ruta_resultados.open("w", encoding="utf-8") as f:
    f.write("192.168.1.10\n")
```

## Manejo de Excepciones al Trabajar con Archivos

Las operaciones con archivos son inherentemente propensas a errores: el archivo puede no existir, el proceso puede no tener permisos de lectura o escritura, el disco puede estar lleno, o la ruta puede contener caracteres inválidos. Un manejo adecuado de excepciones es esencial para que la herramienta se comporte de forma robusta ante estas condiciones en lugar de interrumpirse de forma abrupta.

```python
def cargar_wordlist(ruta):
    """Carga un wordlist con manejo robusto de errores."""
    try:
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            palabras = [linea.strip() for linea in f if linea.strip()]
        print(f"[+] Wordlist cargado: {len(palabras):,} entradas desde '{ruta}'")
        return palabras
    except FileNotFoundError:
        print(f"[-] Archivo no encontrado: '{ruta}'")
    except PermissionError:
        print(f"[-] Sin permiso de lectura sobre '{ruta}'")
    except OSError as error:
        print(f"[-] Error al abrir '{ruta}': {error}")
    return []


def guardar_reporte(ruta, contenido):
    """Guarda un reporte con manejo robusto de errores."""
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"[+] Reporte guardado en '{ruta}'")
    except PermissionError:
        print(f"[-] Sin permiso de escritura en '{ruta}'")
    except OSError as error:
        print(f"[-] Error al escribir '{ruta}': {error}")
```

Las excepciones más relevantes al trabajar con archivos son `FileNotFoundError` (el archivo o directorio no existe), `PermissionError` (el proceso no tiene los permisos necesarios), `FileExistsError` (el archivo ya existe, aplica con el modo `"x"`), `IsADirectoryError` (se intentó abrir como archivo algo que es un directorio), y la clase general `OSError`, que es la superclase de todas las anteriores y captura cualquier error a nivel del sistema operativo relacionado con operaciones de I/O.

## Formatos de Archivo Comunes en Ciberseguridad

Python incluye en su biblioteca estándar módulos dedicados para leer y escribir varios formatos de archivo que aparecen con frecuencia en el trabajo de ciberseguridad.

### CSV: Datos Tabulares

El módulo `csv` permite leer y escribir archivos de valores separados por coma de forma robusta, manejando correctamente los casos complejos como campos que contienen comas o saltos de línea dentro de comillas.

```python
import csv

# Leer un reporte de Nessus o similar exportado como CSV
with open("resultados_escaneo.csv", "r", encoding="utf-8", newline="") as f:
    lector = csv.DictReader(f)   # DictReader: cada fila es un diccionario {encabezado: valor}
    for fila in lector:
        if float(fila.get("cvss", 0)) >= 9.0:
            print(f"[CRÍTICO] {fila['host']} — {fila['cve']} (CVSS: {fila['cvss']})")

# Escribir resultados en formato CSV
campos = ["host", "puerto", "servicio", "cvss", "cve"]
hallazgos = [
    {"host": "192.168.1.10", "puerto": "445", "servicio": "smb", "cvss": "10.0", "cve": "CVE-2020-1472"},
    {"host": "192.168.1.12", "puerto": "443", "servicio": "https", "cvss": "9.8", "cve": "CVE-2021-41773"},
]

with open("hallazgos_exportados.csv", "w", encoding="utf-8", newline="") as f:
    escritor = csv.DictWriter(f, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(hallazgos)
```

### JSON: Datos Estructurados

El módulo `json` permite serializar estructuras de datos Python (diccionarios, listas, cadenas, números, booleanos y `None`) a formato JSON y deserializar JSON de vuelta a estructuras Python, siendo el formato de intercambio más frecuente con APIs de herramientas de ciberseguridad.

```python
import json

# Guardar resultados de escaneo en formato JSON
resultados = {
    "engagement": "Empresa S.A. — Q2 2026",
    "fecha": "2026-06-21",
    "hosts": [
        {"ip": "192.168.1.10", "activo": True, "puertos": [22, 445]},
        {"ip": "192.168.1.11", "activo": False, "puertos": []},
    ],
}

with open("resultados.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, indent=4, ensure_ascii=False)
    # indent=4: formato legible con sangría de 4 espacios
    # ensure_ascii=False: permite caracteres Unicode (como acentos) sin escapar

# Leer y procesar un archivo JSON de resultados anteriores
with open("resultados.json", "r", encoding="utf-8") as f:
    datos = json.load(f)

print(f"Engagement: {datos['engagement']}")
hosts_activos = [h["ip"] for h in datos["hosts"] if h["activo"]]
print(f"Hosts activos: {hosts_activos}")
```

## Buenas Prácticas

El principio más importante al trabajar con archivos en Python es siempre usar `with open()` en lugar de llamar a `open()` y `close()` manualmente: los gestores de contexto eliminan completamente la posibilidad de olvidarse de cerrar un archivo o de que este quede abierto por una excepción. En segundo lugar, siempre debe especificarse el parámetro `encoding="utf-8"` explícitamente en lugar de depender de la codificación por defecto del sistema, que varía entre plataformas y puede generar comportamientos inconsistentes en diferentes entornos.

Al procesar archivos grandes, como un diccionario de contraseñas de varios gigabytes, siempre debe preferirse la iteración directa sobre el objeto archivo (`for linea in archivo`) en lugar de `readlines()`, ya que la primera lee línea por línea sin cargar todo en memoria, mientras que la segunda carga la totalidad del contenido en una lista. Cuando no se tiene certeza de si un archivo con el nombre que se quiere crear ya existe y no se desea sobrescribirlo accidentalmente, el modo `"x"` es la opción más segura. Para calcular hashes u operar sobre archivos binarios grandes, leer en bloques de tamaño fijo (`read(65536)`) es siempre preferible a cargar el archivo completo en memoria. Finalmente, el módulo `pathlib.Path` debe preferirse sobre `os.path` para toda operación de manejo de rutas, ya que ofrece una interfaz más legible, orientada a objetos, y consistente entre sistemas operativos.