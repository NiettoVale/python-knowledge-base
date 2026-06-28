# Bibliotecas `os` y `sys` en Python

## Introducción

Las bibliotecas `os` y `sys` son dos de los módulos más fundamentales de la biblioteca estándar de Python, y aunque con frecuencia se mencionan juntos, tienen responsabilidades claramente diferenciadas: `os` proporciona una interfaz portable para interactuar con el **sistema operativo** (sistema de archivos, variables de entorno, procesos, permisos), mientras que `sys` ofrece acceso al **intérprete de Python** en sí mismo (argumentos de línea de comandos, flujos de salida, versión del intérprete, módulos cargados).

Para quien trabaja en ciberseguridad y desarrollo de herramientas ofensivas o defensivas, ambas bibliotecas son omnipresentes: desde la detección del sistema operativo donde se ejecuta un payload, hasta la lectura de variables de entorno para extraer credenciales o tokens, la enumeración de procesos en ejecución, o la correcta gestión de los argumentos de línea de comandos de una herramienta propia.

---

## La Biblioteca `os`

### Información del Sistema Operativo

El módulo `os` permite consultar información básica sobre el sistema operativo y el entorno de ejecución, lo que resulta especialmente útil al escribir herramientas que deben comportarse de forma diferente según la plataforma donde se ejecuten.

```python
import os

# Nombre del sistema operativo: 'posix' en Linux/macOS, 'nt' en Windows
print(f"Sistema OS     : {os.name}")

# Separador de ruta del sistema: '/' en POSIX, '\\' en Windows
print(f"Separador      : {os.sep!r}")

# Separador de línea: '\n' en POSIX, '\r\n' en Windows
print(f"Fin de línea   : {os.linesep!r}")

# Separador de rutas en PATH: ':' en POSIX, ';' en Windows
print(f"Sep. de PATH   : {os.pathsep!r}")

# Para una detección más detallada (nombre, versión, arquitectura)
import platform
print(f"Plataforma     : {platform.system()}")       # Linux / Windows / Darwin
print(f"Versión kernel : {platform.release()}")
print(f"Arquitectura   : {platform.machine()}")      # x86_64, aarch64, etc.
print(f"Hostname       : {platform.node()}")

# Adaptar el comportamiento de la herramienta según el SO
if os.name == 'nt':
    shell_path = "C:\\Windows\\System32\\cmd.exe"
else:
    shell_path = "/bin/bash"
print(f"Shell objetivo : {shell_path}")
```

### Información del Proceso y del Usuario

```python
import os

# PID del proceso actual y del proceso padre
print(f"PID actual     : {os.getpid()}")
print(f"PID del padre  : {os.getppid()}")

# UID y GID del usuario que ejecuta el proceso (solo en sistemas POSIX)
if os.name == 'posix':
    uid = os.getuid()
    gid = os.getgid()
    euid = os.geteuid()   # UID efectivo (puede diferir si hay setuid)
    print(f"UID  : {uid}   GID: {gid}   EUID: {euid}")

    # En ciberseguridad: verificar si el proceso tiene privilegios de root
    if uid == 0:
        print("[!] El proceso se está ejecutando como root")
    else:
        print(f"[*] Proceso ejecutado como UID {uid} (sin privilegios root)")
```

### Variables de Entorno

Las variables de entorno son una fuente de información crítica en un sistema comprometido: pueden contener tokens de API, credenciales, rutas a archivos de configuración sensibles, o pistas sobre el contexto de ejecución (usuario, home directory, lenguaje del sistema).

```python
import os

# Acceder a todas las variables de entorno como un diccionario
env_vars = os.environ

# Leer una variable de entorno específica
path   = os.environ.get("PATH", "No definida")
home   = os.environ.get("HOME", os.environ.get("USERPROFILE", "No definida"))  # POSIX / Windows
user   = os.environ.get("USER", os.environ.get("USERNAME", "No definido"))
shell  = os.environ.get("SHELL", "No definida")

print(f"PATH  : {path[:60]}...")
print(f"HOME  : {home}")
print(f"USER  : {user}")
print(f"SHELL : {shell}")

# Variables de entorno frecuentemente interesantes en una auditoría
sensitive_vars = [
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY",
    "GITHUB_TOKEN", "DOCKER_AUTH_CONFIG",
    "DATABASE_URL", "API_KEY", "SECRET_KEY",
    "OPENAI_API_KEY", "SLACK_TOKEN",
]
print("\n[*] Buscando variables de entorno potencialmente sensibles:")
for var in sensitive_vars:
    value = os.environ.get(var)
    if value:
        # Mostrar solo los primeros caracteres para no exponer el valor completo
        masked = value[:4] + "*" * (len(value) - 4) if len(value) > 4 else "****"
        print(f"  [!] {var} = {masked}")

# Establecer una variable de entorno (solo afecta al proceso actual y sus hijos)
os.environ["MI_VARIABLE"] = "mi_valor"
print(f"\nMI_VARIABLE después de setear: {os.environ.get('MI_VARIABLE')}")

# Eliminar una variable de entorno
os.environ.pop("MI_VARIABLE", None)   # pop con default None evita KeyError si no existe
```

### Operaciones con el Sistema de Archivos

`os` y su submodule `os.path` proporcionan las herramientas para manipular rutas y realizar operaciones sobre el sistema de archivos de forma portable.

```python
import os

# ── Directorio actual y cambio de directorio ──────────────────────────
cwd = os.getcwd()
print(f"Directorio actual: {cwd}")

os.chdir("/tmp")
print(f"Nuevo directorio: {os.getcwd()}")
os.chdir(cwd)   # volver al directorio original

# ── Crear y eliminar directorios ──────────────────────────────────────
os.makedirs("/tmp/recon/output/logs", exist_ok=True)   # crea toda la jerarquía
print("Directorio 'recon/output/logs' creado")

os.rmdir("/tmp/recon/output/logs")   # elimina solo el directorio vacío más profundo
os.removedirs("/tmp/recon/output")   # elimina directorios vacíos en cadena

# ── Listar contenido de un directorio ────────────────────────────────
print("\nContenido de /etc (primeros 10 elementos):")
for entry in sorted(os.listdir("/etc"))[:10]:
    full_path = os.path.join("/etc", entry)
    entry_type = "DIR " if os.path.isdir(full_path) else "FILE"
    print(f"  [{entry_type}] {entry}")

# ── Recorrer recursivamente un árbol de directorios ──────────────────
# os.walk() es el estándar para recorrer árboles: devuelve (raíz, dirs, archivos)
print("\nRecorrido recursivo de /etc/ssh:")
for root, dirs, files in os.walk("/etc/ssh"):
    depth = root.replace("/etc/ssh", "").count(os.sep)
    indent = "  " * depth
    print(f"{indent}{os.path.basename(root)}/")
    for filename in files:
        print(f"{indent}  {filename}")
```

### `os.path`: Manipulación de Rutas

```python
import os

ruta = "/home/user/tools/recon/output/scan_results.txt"

# Descomposición de rutas
print(f"basename  : {os.path.basename(ruta)}")   # scan_results.txt
print(f"dirname   : {os.path.dirname(ruta)}")    # /home/user/tools/recon/output
print(f"splitext  : {os.path.splitext(ruta)}")   # ('/home/.../scan_results', '.txt')
print(f"split     : {os.path.split(ruta)}")       # (dirname, basename)

# Construcción portable de rutas (usa el separador correcto del SO)
ruta_construida = os.path.join("/home", "user", "tools", "recon", "output")
print(f"join      : {ruta_construida}")

# Verificaciones de existencia y tipo
print(f"exists    : {os.path.exists(ruta)}")
print(f"isfile    : {os.path.isfile(ruta)}")
print(f"isdir     : {os.path.isdir(os.path.dirname(ruta))}")
print(f"isabs     : {os.path.isabs(ruta)}")   # True: es una ruta absoluta

# Ruta absoluta y resolución de symlinks
print(f"abspath   : {os.path.abspath('.')}")
print(f"realpath  : {os.path.realpath('/etc/hosts')}")   # resuelve symlinks

# Tamaño y fechas de un archivo
if os.path.exists("/etc/hosts"):
    stat = os.stat("/etc/hosts")
    print(f"Tamaño    : {stat.st_size} bytes")
    import datetime
    mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
    print(f"Modificado: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
```

### Permisos de Archivos

```python
import os
import stat

# Leer los permisos de un archivo
file_path = "/etc/passwd"
file_stat = os.stat(file_path)
mode = file_stat.st_mode

# Representación octal de los permisos
print(f"Permisos de {file_path}: {oct(mode)[-3:]}")   # ej: 644

# Verificar permisos individuales con el módulo stat
print(f"Lectura para owner  : {bool(mode & stat.S_IRUSR)}")
print(f"Escritura para owner: {bool(mode & stat.S_IWUSR)}")
print(f"Bit SUID activo     : {bool(mode & stat.S_ISUID)}")

# Buscar archivos con bit SUID activo (común en enumeración de escalada de privilegios)
print("\n[*] Buscando archivos con bit SUID en /usr/bin:")
try:
    for entry in os.scandir("/usr/bin"):
        if entry.is_file():
            entry_stat = entry.stat()
            if entry_stat.st_mode & stat.S_ISUID:
                print(f"  [SUID] {entry.path}")
except PermissionError:
    print("  [!] Sin permisos para listar algunos directorios")

# Cambiar permisos de un archivo (equivalente a chmod)
# os.chmod("/tmp/mi_script.sh", 0o755)   # rwxr-xr-x
```

### Ejecución de Comandos del Sistema

`os.system()` y `os.popen()` permiten ejecutar comandos del sistema operativo directamente desde Python, aunque en la mayoría de los casos es preferible usar el módulo `subprocess`, que ofrece mayor control sobre stdin/stdout/stderr, manejo de errores y seguridad.

```python
import os

# os.system(): ejecuta el comando en una subshell, devuelve el código de retorno
return_code = os.system("id")
print(f"\nCódigo de retorno: {return_code}")

# os.popen(): ejecuta el comando y captura su salida como un objeto similar a un archivo
with os.popen("uname -a") as output:
    result = output.read().strip()
print(f"Sistema: {result}")

# RECOMENDADO: subprocess es más seguro y flexible que os.system() y os.popen()
import subprocess
result = subprocess.run(["id"], capture_output=True, text=True)
print(f"Salida de id: {result.stdout.strip()}")
```

### `os.scandir()`: Iteración Eficiente sobre Directorios

`os.scandir()` es la alternativa moderna y eficiente a `os.listdir()`: devuelve objetos `DirEntry` que ya contienen la información de tipo y stat del archivo, evitando llamadas adicionales al sistema operativo para cada entrada.

```python
import os

# scandir() es más eficiente que listdir() + os.stat() por cada elemento
target_dir = "/etc"
files_info = []

try:
    with os.scandir(target_dir) as entries:
        for entry in entries:
            try:
                info = {
                    "name"    : entry.name,
                    "is_file" : entry.is_file(),
                    "is_dir"  : entry.is_dir(),
                    "size"    : entry.stat().st_size if entry.is_file() else 0,
                }
                files_info.append(info)
            except PermissionError:
                pass

    # Ordenar por tamaño descendente y mostrar los 5 más grandes
    top_files = sorted([f for f in files_info if f["is_file"]],
                       key=lambda x: x["size"], reverse=True)[:5]
    print(f"Los 5 archivos más grandes en {target_dir}:")
    for f in top_files:
        print(f"  {f['size']:>8} bytes  {f['name']}")

except PermissionError:
    print(f"[!] Sin permisos para leer {target_dir}")
```

---

## La Biblioteca `sys`

### Argumentos de Línea de Comandos: `sys.argv`

`sys.argv` es una lista que contiene los argumentos pasados al script de Python desde la línea de comandos. El primer elemento (`sys.argv[0]`) es siempre el nombre del script en sí; los argumentos adicionales comienzan desde `sys.argv[1]`.

```python
import sys

# sys.argv[0] es el nombre del script
# sys.argv[1], sys.argv[2], ... son los argumentos adicionales
print(f"Nombre del script: {sys.argv[0]}")
print(f"Argumentos: {sys.argv[1:]}")
print(f"Total argumentos: {len(sys.argv) - 1}")

# Ejemplo: herramienta simple que lee target y puerto desde la línea de comandos
# Uso: python3 herramienta.py 192.168.1.10 443
if len(sys.argv) != 3:
    print(f"Uso: {sys.argv[0]} <host> <puerto>")
    sys.exit(1)   # termina el programa con código de error 1

target = sys.argv[1]
port   = int(sys.argv[2])
print(f"Escaneando {target}:{port}...")
```

Para herramientas más complejas con múltiples opciones, flags y argumentos opcionales, el módulo `argparse` de la biblioteca estándar es considerablemente más robusto y recomendable que procesar `sys.argv` manualmente.

```python
import argparse

parser = argparse.ArgumentParser(
    description="Herramienta de escaneo de puertos",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument("target",          help="IP o hostname objetivo")
parser.add_argument("--port",  "-p",   type=int, default=80, help="Puerto a escanear (default: 80)")
parser.add_argument("--timeout", "-t", type=float, default=3.0, help="Timeout en segundos")
parser.add_argument("--verbose", "-v", action="store_true", help="Modo verboso")
parser.add_argument("--output", "-o",  type=str, help="Archivo de salida (opcional)")

# args = parser.parse_args()   # en ejecución normal
# args = parser.parse_args(["192.168.1.10", "--port", "443", "--verbose"])  # para pruebas
```

### Salida del Programa: `sys.exit()`

`sys.exit()` termina la ejecución del programa con un código de salida. Por convención, un código `0` indica ejecución exitosa, y cualquier valor distinto de `0` indica un error. Los scripts de shell y los pipelines usan el código de salida para determinar si el comando previo tuvo éxito, por lo que el uso correcto de códigos de salida es importante en herramientas de línea de comandos.

```python
import sys

# Terminar con éxito (código 0)
# sys.exit(0)

# Terminar con error (código distinto de 0)
# sys.exit(1)

# También acepta una cadena, que se imprime en stderr antes de salir con código 1
# sys.exit("Error: archivo de configuración no encontrado")

# Ejemplo de uso en una herramienta:
def validate_args(target, port):
    if not target:
        print("[-] Error: debe especificarse un host objetivo", file=sys.stderr)
        sys.exit(1)
    if not (1 <= port <= 65535):
        print(f"[-] Error: puerto {port} fuera del rango válido [1-65535]", file=sys.stderr)
        sys.exit(2)   # código 2 para distinguir el tipo de error
```

### Flujos de Salida: `sys.stdout` y `sys.stderr`

`sys.stdout` y `sys.stderr` son los flujos de salida estándar y de error del programa. `print()` escribe por defecto en `sys.stdout`, pero puede redirigirse a `sys.stderr` para mensajes de diagnóstico y error. Esta separación es importante porque permite al usuario final redirigir la salida "útil" del programa (resultados, datos) a un archivo o a otro comando, mientras que los mensajes de error siguen apareciendo en la terminal.

```python
import sys

def log(msg):       print(f"[*] {msg}", file=sys.stdout)
def success(msg):   print(f"[+] {msg}", file=sys.stdout)
def warning(msg):   print(f"[!] {msg}", file=sys.stderr)
def error(msg):     print(f"[-] {msg}", file=sys.stderr)

# Los resultados van a stdout (redirigibles con >)
log("Iniciando escaneo de 192.168.1.0/24")
success("Host 192.168.1.10 activo — Puerto 443 abierto")

# Los errores y advertencias van a stderr (redirigibles con 2>)
warning("Timeout alcanzado para 192.168.1.20")
error("Permiso denegado al abrir el archivo de configuración")
```

```bash
# En la terminal, esto permite:
python3 scanner.py > resultados.txt     # solo los resultados al archivo
python3 scanner.py 2> errores.log       # solo los errores al archivo
python3 scanner.py > resultados.txt 2>&1  # todo junto al mismo archivo
```

También es posible redirigir completamente `sys.stdout` a un archivo para capturar toda la salida del programa:

```python
import sys

original_stdout = sys.stdout   # guardar referencia al stdout original

with open("output.txt", "w", encoding="utf-8") as f:
    sys.stdout = f              # redirigir toda la salida a un archivo
    print("Esta línea va al archivo, no a la consola")
    print("Esta también")

sys.stdout = original_stdout    # restaurar el stdout original
print("Esta línea vuelve a aparecer en la consola")
```

### Información del Intérprete de Python

```python
import sys

# Versión completa del intérprete de Python
print(f"Versión Python : {sys.version}")
print(f"Versión (tuple): {sys.version_info}")
print(f"Mayor.Menor    : {sys.version_info.major}.{sys.version_info.minor}")

# Verificar la versión mínima requerida antes de continuar
if sys.version_info < (3, 9):
    print("[-] Se requiere Python 3.9 o superior", file=sys.stderr)
    sys.exit(1)

# Plataforma donde corre el intérprete
print(f"Plataforma     : {sys.platform}")   # 'linux', 'win32', 'darwin'

# Ejecutable del intérprete (útil para saber qué Python está corriendo)
print(f"Ejecutable     : {sys.executable}")

# Tamaño de los enteros (32 o 64 bits)
print(f"Máx. int       : {sys.maxsize}")   # 2^63 - 1 en sistemas de 64 bits
print(f"Arquitectura   : {'64 bits' if sys.maxsize > 2**32 else '32 bits'}")

# Codificación por defecto del sistema de archivos
print(f"Codificación FS: {sys.getfilesystemencoding()}")
```

### `sys.path`: Rutas de Búsqueda de Módulos

`sys.path` es la lista de directorios en los que Python busca módulos cuando se ejecuta una instrucción `import`. El intérprete los recorre en orden y usa el primer módulo cuyo nombre coincida con el solicitado. Modificar `sys.path` en tiempo de ejecución permite importar módulos desde ubicaciones no estándar.

```python
import sys

# Ver las rutas actuales de búsqueda
print("Rutas de búsqueda de módulos (sys.path):")
for i, path in enumerate(sys.path):
    print(f"  [{i}] {path}")

# Agregar un directorio personalizado al inicio de sys.path
# (tiene prioridad sobre los directorios existentes)
sys.path.insert(0, "/opt/mis_herramientas/modulos")

# Agregar al final (menor prioridad)
sys.path.append("/home/user/proyectos/librerias")

# A partir de aquí, import buscará también en esos directorios
```

### `sys.modules`: Módulos Actualmente Importados

`sys.modules` es un diccionario que mapea los nombres de los módulos a sus objetos en memoria. Contiene todos los módulos que han sido importados desde el inicio de la sesión. Inspeccionarlo puede resultar útil para diagnóstico o para detectar qué módulos tiene cargados un proceso objetivo.

```python
import sys
import os
import re

# Ver todos los módulos actualmente importados
print(f"Total de módulos importados: {len(sys.modules)}")
print("Módulos de la biblioteca estándar importados:")
stdlib_modules = [name for name in sys.modules.keys()
                  if not name.startswith("_") and "." not in name]
print(stdlib_modules[:10])

# Verificar si un módulo está disponible sin importarlo
if "cryptography" in sys.modules:
    print("El módulo 'cryptography' ya está importado")
else:
    print("El módulo 'cryptography' no ha sido importado todavía")
```

### `sys.stdin`: Lectura desde la Entrada Estándar

`sys.stdin` permite leer datos de la entrada estándar, lo que hace posible que una herramienta reciba datos desde un pipe o desde la redirección de un archivo.

```python
import sys

# Verificar si hay datos siendo redirigidos por pipe (stdin no es un terminal)
if not sys.stdin.isatty():
    # Hay datos llegando por pipe: leer línea por línea
    print("[*] Leyendo datos desde stdin (pipe):")
    for line in sys.stdin:
        ip = line.strip()
        if ip:
            print(f"  Procesando: {ip}")
else:
    # stdin es un terminal: pedir input al usuario
    target = input("Introduce el host objetivo: ")
    print(f"Host objetivo: {target}")
```

```bash
# La herramienta puede usarse de dos formas:
# 1. Con pipe (sin TTY):
cat hosts.txt | python3 scanner.py

# 2. Interactiva (con TTY):
python3 scanner.py
```

---

## Combinando `os` y `sys`: Herramienta de Enumeración

Un ejemplo integrador que combina ambas bibliotecas en una herramienta de enumeración del entorno:

```python
import os
import sys
import stat
import datetime

def enumerate_environment():
    """Recopila información del entorno del sistema de forma estructurada."""

    print(f"\n{'═' * 55}")
    print("  ENUMERACIÓN DEL ENTORNO")
    print(f"{'═' * 55}")

    # ── Intérprete y versión ─────────────────────────────────
    print(f"\n[*] Intérprete  : {sys.executable}")
    print(f"[*] Python      : {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"[*] Plataforma  : {sys.platform}")
    print(f"[*] Arquitectura: {'64 bits' if sys.maxsize > 2**32 else '32 bits'}")

    # ── Proceso y usuario ────────────────────────────────────
    print(f"\n[*] PID         : {os.getpid()}")
    if os.name == 'posix':
        uid, gid = os.getuid(), os.getgid()
        print(f"[*] UID/GID     : {uid}/{gid}")
        if uid == 0:
            print("[!] EJECUTANDO COMO ROOT")

    # ── Variables de entorno interesantes ────────────────────
    interesting_env = ["HOME", "USER", "SHELL", "PATH", "SUDO_USER", "LOGNAME"]
    print("\n[*] Variables de entorno:")
    for var in interesting_env:
        value = os.environ.get(var, "No definida")
        display = value[:60] + "..." if len(value) > 60 else value
        print(f"    {var:<12}: {display}")

    # ── Directorio actual y de trabajo ───────────────────────
    print(f"\n[*] CWD         : {os.getcwd()}")

    # ── Argumentos del script ────────────────────────────────
    print(f"[*] Argumentos  : {sys.argv}")

    print(f"\n{'═' * 55}\n")

if __name__ == "__main__":
    enumerate_environment()
```

## Buenas Prácticas

Al usar `os.environ`, siempre debe preferirse `os.environ.get("VAR", default)` sobre el acceso directo `os.environ["VAR"]`, ya que el primero devuelve un valor por defecto si la variable no está definida, mientras que el segundo lanza un `KeyError`. Para operaciones con rutas, usar siempre `os.path.join()` en lugar de construir rutas concatenando cadenas con `/` o `\\`, garantizando portabilidad entre sistemas operativos.

Para ejecutar comandos del sistema, `subprocess` es prácticamente siempre preferible a `os.system()` y `os.popen()`, ya que ofrece mayor control sobre los streams de entrada/salida, mejor manejo de errores, y no invocan la shell de forma implícita (lo cual es relevante desde el punto de vista de seguridad cuando los argumentos del comando provienen de entradas del usuario). Para la separación entre salida útil y mensajes de diagnóstico, usar siempre `file=sys.stderr` en `print()` para los mensajes de error y advertencia, y `sys.stdout` para los resultados, permitiendo que quien usa la herramienta redirija ambos de forma independiente.