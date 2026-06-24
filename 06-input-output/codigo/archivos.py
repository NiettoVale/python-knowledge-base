#!/usr/bin/env python3
import csv
import json
import hashlib
import datetime
from pathlib import Path

Path("output").mkdir(exist_ok=True)


# ═════════════════════════════════════════════════════════════════════
# 1. ESCRITURA DE ARCHIVOS
# ═════════════════════════════════════════════════════════════════════
print("=" * 55)
print(" 1. ESCRITURA DE ARCHIVOS")
print("=" * 55)

# ── 1a. Forma tradicional (NO recomendada): requiere cerrar manualmente ──
file = open("output/example.txt", "w", encoding="utf-8")   # abre el archivo
file.write("Hola mundo!")                                    # escribe el contenido
file.close()                                                 # cierra el archivo (obligatorio con esta forma)
print("[+] Archivo 'example.txt' creado con la forma tradicional.")

# ── 1b. Forma óptima: gestor de contexto 'with' ──
# El archivo se cierra automáticamente al salir del bloque,
# incluso si ocurre una excepción dentro de él.
with open("output/example2.txt", "w", encoding="utf-8") as f:
    f.write("Nuevo fichero creado con el gestor de contexto!\n")
print("[+] Archivo 'example2.txt' creado con el gestor de contexto.")

# ── 1c. Escribir múltiples líneas con writelines() ──
# writelines() escribe una secuencia de cadenas sin agregar separadores automáticamente.
# Los saltos de línea (\n) deben incluirse en cada cadena.
target_list = [
    "192.168.1.10\n",
    "192.168.1.11\n",
    "192.168.1.12\n",
    "10.10.10.5\n",
]
with open("output/targets.txt", "w", encoding="utf-8") as f:
    f.writelines(target_list)
print(f"[+] Archivo 'targets.txt' creado con {len(target_list)} objetivos.")

# ── 1d. Modo append: agregar sin sobrescribir ──
# El modo 'a' coloca el puntero al final del archivo existente,
# preservando todo el contenido anterior. Si el archivo no existe, lo crea.
findings = [
    "[CRÍTICO] CVE-2020-1472 — ZeroLogon en 192.168.1.10\n",
    "[ALTO]    CVE-2021-41773 — Path Traversal en 192.168.1.12\n",
    "[MEDIO]   CVE-2022-26134 — OGNL Injection en 10.10.10.5\n",
]
for finding in findings:
    with open("output/findings.txt", "a", encoding="utf-8") as f:
        f.write(finding)
print("[+] Archivo 'findings.txt' creado con modo append (cada hallazgo añadido de forma independiente).")

# ── 1e. Modo 'x': creación exclusiva, falla si el archivo ya existe ──
# Útil para evitar sobrescribir reportes anteriores accidentalmente.
report_path = "output/report_exclusive.txt"
try:
    with open(report_path, "x", encoding="utf-8") as f:
        f.write("Reporte de reconocimiento — Q2 2026\n")
    print(f"[+] Reporte creado con modo exclusivo: '{report_path}'.")
except FileExistsError:
    print(f"[!] El archivo '{report_path}' ya existe. No se sobrescribió.")


# ═════════════════════════════════════════════════════════════════════
# 2. LECTURA DE ARCHIVOS
# ═════════════════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print(" 2. LECTURA DE ARCHIVOS")
print("=" * 55)

# ── 2a. Leer todo el contenido de una vez con read() ──
# Carga el archivo completo en memoria como una sola cadena.
# Apropiado para archivos de tamaño moderado.
with open("output/targets.txt", "r", encoding="utf-8") as f:
    full_content = f.read()
print("[*] Contenido completo de 'targets.txt':")
print(full_content.strip())

# ── 2b. Lectura línea a línea con iteración directa (forma recomendada) ──
# La más eficiente en memoria: lee una línea por vez sin cargar todo el archivo.
# Ideal para wordlists o listas de hosts de gran tamaño.
print("\n[*] Objetivos leídos línea a línea:")
with open("output/targets.txt", "r", encoding="utf-8") as f:
    for line in f:
        target = line.strip()
        if target:   # ignorar líneas vacías
            print(f"    -> {target}")

# ── 2c. Leer con readline(): control manual línea por línea ──
# Útil cuando se necesita procesar exactamente N líneas o saltar el encabezado.
print("\n[*] Solo las 2 primeras líneas con readline():")
with open("output/findings.txt", "r", encoding="utf-8") as f:
    first_line  = f.readline().strip()
    second_line = f.readline().strip()
    print(f"    Línea 1: {first_line}")
    print(f"    Línea 2: {second_line}")

# ── 2d. Leer con readlines(): todas las líneas en una lista ──
# Carga el archivo completo en memoria como una lista de cadenas.
# Permite acceso por índice, pero consume más memoria que la iteración directa.
with open("output/targets.txt", "r", encoding="utf-8") as f:
    all_targets = [line.strip() for line in f.readlines() if line.strip()]
print(f"\n[*] Todos los objetivos cargados en lista: {all_targets}")

# ── 2e. Leer /etc/hosts del sistema (solo en Linux/macOS) ──
# Se usa try/except porque el archivo puede no estar disponible en todos los entornos.
try:
    with open("/etc/hosts", "r", encoding="utf-8") as f:
        print("\n[*] Primeras 5 líneas de /etc/hosts:")
        for i, line in enumerate(f):
            if i >= 5:
                break
            print(f"    {line}", end="")
except FileNotFoundError:
    print("\n[!] /etc/hosts no encontrado en este entorno.")


# ═════════════════════════════════════════════════════════════════════
# 3. MANEJO DE EXCEPCIONES
# ═════════════════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print(" 3. MANEJO DE EXCEPCIONES")
print("=" * 55)

# ── 3a. FileNotFoundError: archivo inexistente ──
try:
    with open("database.sql", "r", encoding="utf-8") as f:
        for line in f:
            print(line, end="")
except FileNotFoundError:
    print("[!] No fue posible encontrar ese archivo: 'database.sql'")

# ── 3b. PermissionError: sin permisos de lectura ──
try:
    with open("/etc/shadow", "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    print("[!] Archivo '/etc/shadow' no encontrado.")
except PermissionError:
    print("[!] Sin permiso para leer '/etc/shadow' (se requiere root).")

# ── 3c. Manejo completo con múltiples excepciones ──
def safe_read(file_path):
    """Intenta leer un archivo y devuelve su contenido o None ante cualquier error."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"[!] Archivo no encontrado: '{file_path}'")
    except PermissionError:
        print(f"[!] Permiso denegado al leer: '{file_path}'")
    except OSError as error:
        print(f"[!] Error del sistema al abrir '{file_path}': {error}")
    return None

content = safe_read("output/targets.txt")
if content:
    print(f"[+] 'targets.txt' leído correctamente ({len(content)} caracteres).")


# ═════════════════════════════════════════════════════════════════════
# 4. ARCHIVOS BINARIOS
# ═════════════════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print(" 4. ARCHIVOS BINARIOS")
print("=" * 55)

# ── 4a. Copiar un archivo binario en bloques ──
# No se carga el archivo completo en memoria: se lee y escribe bloque a bloque.
# Apropiado para imágenes, ejecutables, capturas PCAP, etc.
BLOCK_SIZE = 4096   # 4 KB por bloque

source_path = "output/targets.txt"   # se usa un txt como demo (cualquier archivo sirve)
dest_path   = "output/targets_backup.bin"

with open(source_path, "rb") as f_in, open(dest_path, "wb") as f_out:
    blocks_written = 0
    while True:
        block = f_in.read(BLOCK_SIZE)
        if not block:
            break
        f_out.write(block)
        blocks_written += 1

print(f"[+] Archivo copiado en modo binario: '{source_path}' → '{dest_path}' ({blocks_written} bloque(s)).")

# ── 4b. Identificar el tipo de archivo por sus magic bytes ──
# Los primeros bytes de un archivo (firma o magic bytes) identifican su formato.
# Este patrón aparece frecuentemente en análisis de malware y forense digital.
MAGIC_SIGNATURES = {
    b"\x7fELF":          "Ejecutable ELF (Linux)",
    b"MZ":               "Ejecutable PE (Windows .exe / .dll)",
    b"\x89PNG":          "Imagen PNG",
    b"PK\x03\x04":       "Archivo ZIP / .jar / .apk / .docx",
    b"\xd4\xc3\xb2\xa1": "Captura PCAP (little-endian)",
    b"JFIF":             "Imagen JPEG",
    b"%PDF":             "Documento PDF",
}

def identify_file_type(file_path):
    """Identifica el tipo de archivo comparando sus primeros bytes con las firmas conocidas."""
    try:
        with open(file_path, "rb") as f:
            header = f.read(8)
        for signature, description in MAGIC_SIGNATURES.items():
            if header.startswith(signature):
                return description
        return "Tipo desconocido o no registrado"
    except (FileNotFoundError, PermissionError):
        return "No accesible"

print(f"[*] Tipo de 'targets_backup.bin': {identify_file_type(dest_path)}")
print(f"[*] Tipo de '/bin/ls':             {identify_file_type('/bin/ls')}")

# ── 4c. Calcular el hash SHA-256 de un archivo sin cargarlo completo en memoria ──
# Imprescindible para verificar integridad de archivos, comparar muestras de malware,
# o generar indicadores de compromiso (IOCs) de tipo hash.
def calculate_file_hash(file_path, algorithm="sha256"):
    """Calcula el hash criptográfico de un archivo leyéndolo en bloques de 64 KB."""
    hasher = hashlib.new(algorithm)
    try:
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(65536), b""):
                hasher.update(block)
        return hasher.hexdigest()
    except (FileNotFoundError, PermissionError) as error:
        return f"Error: {error}"

sha256 = calculate_file_hash("output/targets.txt")
print(f"[+] SHA-256 de 'targets.txt': {sha256}")


# ═════════════════════════════════════════════════════════════════════
# 5. PATHLIB: manejo moderno de rutas
# ═════════════════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print(" 5. PATHLIB")
print("=" * 55)

base_dir = Path("output")
targets_file = base_dir / "targets.txt"

# Información sobre la ruta
print(f"[*] Nombre del archivo : {targets_file.name}")
print(f"[*] Extensión          : {targets_file.suffix}")
print(f"[*] Directorio padre   : {targets_file.parent}")
print(f"[*] ¿Existe?           : {targets_file.exists()}")
print(f"[*] Tamaño             : {targets_file.stat().st_size} bytes")

# Listar todos los archivos del directorio de salida
print("\n[*] Archivos en 'output/':")
for item in sorted(base_dir.iterdir()):
    if item.is_file():
        print(f"    {item.name:<35} {item.stat().st_size:>6} bytes")


# ═════════════════════════════════════════════════════════════════════
# 6. FORMATOS ESTRUCTURADOS: CSV y JSON
# ═════════════════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print(" 6. FORMATOS ESTRUCTURADOS: CSV Y JSON")
print("=" * 55)

# ── 6a. Exportar hallazgos a CSV ──
scan_results = [
    {"host": "192.168.1.10", "port": 445,  "service": "smb",   "cve": "CVE-2020-1472", "cvss": 10.0},
    {"host": "192.168.1.12", "port": 443,  "service": "https", "cve": "CVE-2021-41773","cvss": 9.8},
    {"host": "10.10.10.5",   "port": 8080, "service": "http",  "cve": "CVE-2022-26134","cvss": 7.5},
]

csv_path = base_dir / "scan_results.csv"
fieldnames = ["host", "port", "service", "cve", "cvss"]

with open(csv_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(scan_results)
print(f"[+] Resultados exportados a CSV: '{csv_path}' ({len(scan_results)} filas).")

# Leer el CSV e imprimir solo los hallazgos críticos (CVSS >= 9.0)
print("[*] Hallazgos críticos (CVSS ≥ 9.0):")
with open(csv_path, "r", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        if float(row["cvss"]) >= 9.0:
            print(f"    [{row['cvss']}] {row['cve']} en {row['host']}:{row['port']}")

# ── 6b. Exportar resultados completos a JSON ──
engagement_report = {
    "engagement": "Empresa S.A. — Reconocimiento Q2 2026",
    "date": datetime.date.today().isoformat(),
    "total_findings": len(scan_results),
    "findings": scan_results,
}

json_path = base_dir / "engagement_report.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(engagement_report, f, indent=4, ensure_ascii=False)
print(f"\n[+] Reporte JSON guardado: '{json_path}'.")

# Leer y consumir el JSON
with open(json_path, "r", encoding="utf-8") as f:
    loaded_report = json.load(f)

print(f"[*] Engagement cargado : {loaded_report['engagement']}")
print(f"[*] Fecha              : {loaded_report['date']}")
print(f"[*] Total de hallazgos : {loaded_report['total_findings']}")