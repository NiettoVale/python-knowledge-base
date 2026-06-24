# Manejo de Fechas y Horas en Python: el Módulo `datetime`

## Introducción

El manejo preciso de fechas y horas es una necesidad transversal en prácticamente cualquier herramienta de software real. En ciberseguridad, esta necesidad se vuelve especialmente crítica: los logs de sistemas, firewalls y SIEMs están indexados por tiempo, y la capacidad de parsear, comparar, calcular diferencias y formatear timestamps determina si se puede correlacionar eventos, identificar ventanas de ataque, calcular la antigüedad de una vulnerabilidad o determinar si un certificado SSL está próximo a expirar. La biblioteca estándar de Python provee el módulo `datetime`, que cubre la gran mayoría de estas necesidades con una API coherente y bien diseñada.

## Tipos de Datos Principales del Módulo `datetime`

El módulo `datetime` expone cuatro tipos de datos fundamentales, cada uno orientado a representar un concepto temporal distinto.

**`date`** representa únicamente una fecha (año, mes y día), sin información de hora. Es el tipo apropiado cuando solo importa el día, como la fecha de publicación de un CVE o la fecha de inicio de un engagement.

**`time`** representa únicamente una hora (hora, minuto, segundo y microsegundo), sin fecha asociada. Se utiliza cuando solo interesa la parte horaria de un evento, aunque en la práctica esto es menos común que el tipo combinado.

**`datetime`** combina fecha y hora en un único objeto, y es el tipo más utilizado en la práctica. Representa un instante concreto en el tiempo, como el timestamp de un evento de seguridad o el momento exacto en que se realizó un escaneo.

**`timedelta`** representa una **diferencia de tiempo**: un intervalo entre dos momentos, expresado internamente en días, segundos y microsegundos. Es el resultado de restar dos objetos `datetime` entre sí, y puede usarse para sumar o restar tiempo a una fecha.

```python
from datetime import date, time, datetime, timedelta

# date: solo fecha (sin hora)
fecha_publicacion = date(2020, 11, 11)   # CVE-2020-1472 publicado el 11/11/2020
print(fecha_publicacion)          # 2020-11-11
print(type(fecha_publicacion))    # <class 'datetime.date'>

# time: solo hora (sin fecha)
hora_inicio_escaneo = time(14, 30, 0)   # 14:30:00
print(hora_inicio_escaneo)        # 14:30:00

# datetime: fecha y hora combinadas
timestamp_evento = datetime(2026, 6, 21, 14, 32, 15)   # 21/06/2026 14:32:15
print(timestamp_evento)           # 2026-06-21 14:32:15

# timedelta: diferencia de tiempo
diferencia = timedelta(days=30, hours=6, minutes=30)
print(diferencia)                 # 30 days, 6:30:00
print(type(diferencia))           # <class 'datetime.timedelta'>
```

## Obtener la Fecha y Hora Actual

El tipo `datetime` ofrece métodos de clase para obtener la fecha u hora actual del sistema sin necesidad de pasar argumentos manualmente.

```python
from datetime import date, datetime

# Fecha y hora actuales del sistema local
ahora = datetime.now()
print(f"Ahora (local): {ahora}")
# 2026-06-21 14:32:15.847293

# Solo la fecha actual
hoy = date.today()
print(f"Hoy: {hoy}")
# 2026-06-21

# Fecha y hora actuales en UTC (importante para logs y correlación internacional)
ahora_utc = datetime.utcnow()
print(f"Ahora (UTC): {ahora_utc}")

# Acceso a componentes individuales del datetime
print(f"Año   : {ahora.year}")
print(f"Mes   : {ahora.month}")
print(f"Día   : {ahora.day}")
print(f"Hora  : {ahora.hour}")
print(f"Minuto: {ahora.minute}")
print(f"Segundo: {ahora.second}")
print(f"Microsegundo: {ahora.microsecond}")
print(f"Día de la semana (0=lunes): {ahora.weekday()}")
print(f"Día del año: {ahora.timetuple().tm_yday}")
```

## Formateo de Fechas y Horas: `strftime()`

El método `strftime()` (_string format time_) convierte un objeto `datetime` (o `date` o `time`) en una cadena de texto formateada según un patrón definido mediante **códigos de formato**. Estos códigos comienzan siempre con el carácter `%` seguido de una letra que identifica el componente temporal que debe insertarse.

```python
from datetime import datetime

evento = datetime(2026, 6, 21, 14, 32, 15)

# Formatos más comunes
print(evento.strftime("%Y-%m-%d"))               # 2026-06-21  (ISO 8601, el más recomendado)
print(evento.strftime("%d/%m/%Y"))               # 21/06/2026  (formato europeo)
print(evento.strftime("%m/%d/%Y"))               # 06/21/2026  (formato estadounidense)
print(evento.strftime("%Y-%m-%d %H:%M:%S"))      # 2026-06-21 14:32:15
print(evento.strftime("%d de %B de %Y"))         # 21 de June de 2026
print(evento.strftime("%A, %d %B %Y"))           # Saturday, 21 June 2026
print(evento.strftime("%H:%M:%S"))               # 14:32:15
print(evento.strftime("%I:%M %p"))               # 02:32 PM  (formato 12h)
print(evento.strftime("%Y%m%d_%H%M%S"))          # 20260621_143215  (para nombres de archivo)
```

### Tabla de Códigos de Formato Más Utilizados

|Código|Significado|Ejemplo|
|---|---|---|
|`%Y`|Año con 4 dígitos|`2026`|
|`%y`|Año con 2 dígitos|`26`|
|`%m`|Mes con 2 dígitos (01–12)|`06`|
|`%B`|Nombre completo del mes (en el idioma del sistema)|`June`|
|`%b`|Nombre abreviado del mes|`Jun`|
|`%d`|Día del mes con 2 dígitos (01–31)|`21`|
|`%A`|Nombre completo del día de la semana|`Saturday`|
|`%a`|Nombre abreviado del día|`Sat`|
|`%H`|Hora en formato 24h (00–23)|`14`|
|`%I`|Hora en formato 12h (01–12)|`02`|
|`%M`|Minutos (00–59)|`32`|
|`%S`|Segundos (00–59)|`15`|
|`%f`|Microsegundos (000000–999999)|`847293`|
|`%p`|AM/PM|`PM`|
|`%j`|Día del año (001–366)|`172`|
|`%W`|Número de semana del año (lunes como primer día)|`24`|
|`%Z`|Nombre de la zona horaria|`UTC`|
|`%z`|Offset de zona horaria|`+0000`|

## Parseo de Fechas: `strptime()`

La operación inversa a `strftime()` es `strptime()` (_string parse time_): convierte una cadena de texto que representa una fecha/hora en un objeto `datetime`, usando el mismo sistema de códigos de formato para indicar cómo interpretar la cadena. Esta operación es fundamental al procesar logs, reportes o cualquier fuente de datos externa que incluya timestamps en formato texto.

```python
from datetime import datetime

# Parsear distintos formatos de timestamp presentes en logs reales
formatos_log = [
    ("2026-06-21 14:32:15",         "%Y-%m-%d %H:%M:%S"),     # syslog estándar
    ("21/06/2026 02:32:15 PM",      "%d/%m/%Y %I:%M:%S %p"),  # formato europeo 12h
    ("Jun 21 14:32:15",             "%b %d %H:%M:%S"),         # formato /var/log/auth.log
    ("2026-06-21T14:32:15",         "%Y-%m-%dT%H:%M:%S"),      # ISO 8601 (JSON, APIs)
    ("21-Jun-2026 14:32:15",        "%d-%b-%Y %H:%M:%S"),      # formato Apache
    ("20260621143215",              "%Y%m%d%H%M%S"),            # compacto (nombres de archivo)
]

for texto, formato in formatos_log:
    dt = datetime.strptime(texto, formato)
    print(f"  '{texto}' → {dt}  (tipo: {type(dt).__name__})")

# Parseo con manejo de error: protección ante logs con formato inesperado
raw_timestamp = "fecha_invalida_2026"
try:
    dt_parseado = datetime.strptime(raw_timestamp, "%Y-%m-%d %H:%M:%S")
except ValueError as error:
    print(f"\n[!] No se pudo parsear '{raw_timestamp}': {error}")
```

## Manipulación de Fechas con `timedelta`

El tipo `timedelta` es la herramienta fundamental para calcular diferencias entre fechas o desplazarse hacia adelante y hacia atrás en el tiempo. Se puede crear directamente especificando la cantidad de días, horas, minutos y segundos, o se obtiene como resultado de restar dos objetos `datetime` entre sí.

```python
from datetime import datetime, timedelta

ahora = datetime(2026, 6, 21, 14, 32, 15)

# Sumar y restar tiempo a una fecha
manana          = ahora + timedelta(days=1)
hace_una_semana = ahora - timedelta(weeks=1)
en_30_dias      = ahora + timedelta(days=30)
hace_2_horas    = ahora - timedelta(hours=2)

print(f"Ahora         : {ahora}")
print(f"Mañana        : {manana}")
print(f"Hace una semana: {hace_una_semana}")
print(f"En 30 días    : {en_30_dias}")
print(f"Hace 2 horas  : {hace_2_horas}")

# Calcular la diferencia entre dos fechas
fecha_vuln     = datetime(2020, 11, 11)   # fecha de publicación de CVE-2020-1472
fecha_parche   = datetime(2020, 8, 11)    # fecha del parche de Microsoft

diferencia = fecha_vuln - fecha_parche
print(f"\nCVE-2020-1472 fue publicado {diferencia.days} días después del parche disponible")

# Extraer componentes de un timedelta
delta = timedelta(days=365, hours=5, minutes=30, seconds=15)
print(f"\nDescomposición del timedelta:")
print(f"  Días totales   : {delta.days}")
print(f"  Segundos extras: {delta.seconds}")
print(f"  Total segundos : {delta.total_seconds():.0f}")
print(f"  Total horas    : {delta.total_seconds() / 3600:.2f}")

# Determinar si una vulnerabilidad ya es "antigua" (más de 90 días)
today = datetime(2026, 6, 21)
vuln_date = datetime(2026, 2, 15)
age = today - vuln_date
if age.days > 90:
    print(f"\n[!] Vulnerabilidad con {age.days} días sin remediar (umbral: 90 días)")
```

## Comparación de Fechas

Los objetos `datetime`, `date` y `time` soportan directamente los operadores de comparación estándar (`<`, `<=`, `>`, `>=`, `"=="`, `!=`), lo que permite comparar fechas de la misma forma en que se compararían números o cadenas.

```python
from datetime import datetime, date

# Comparar fechas directamente con operadores
fecha_escaneo1 = datetime(2026, 6, 15, 10, 0, 0)
fecha_escaneo2 = datetime(2026, 6, 21, 14, 32, 0)

print(fecha_escaneo1 < fecha_escaneo2)    # True: el primer escaneo fue antes
print(fecha_escaneo1 == fecha_escaneo2)   # False: no son el mismo instante

# Verificar si un certificado SSL ha expirado o está por vencer
cert_expiry = datetime(2026, 8, 30)
today       = datetime(2026, 6, 21)
days_until  = (cert_expiry - today).days

if today > cert_expiry:
    print("[!] CRÍTICO: El certificado ha EXPIRADO")
elif days_until <= 30:
    print(f"[!] ALERTA: El certificado vence en {days_until} días")
else:
    print(f"[+] Certificado válido. Vence en {days_until} días")

# Ordenar una lista de eventos por timestamp (los objetos datetime son comparables)
eventos = [
    ("Login fallido",  datetime(2026, 6, 21, 14, 35, 10)),
    ("Escaneo de red", datetime(2026, 6, 21, 14, 30, 00)),
    ("Shell reversa",  datetime(2026, 6, 21, 14, 38, 55)),
    ("Exfiltración",   datetime(2026, 6, 21, 14, 42, 30)),
]

eventos_ordenados = sorted(eventos, key=lambda x: x[1])
print("\nLínea de tiempo del incidente:")
for nombre, ts in eventos_ordenados:
    print(f"  {ts.strftime('%H:%M:%S')} — {nombre}")
```

## Timestamps Unix (Epoch)

En muchos contextos de sistemas, red y ciberseguridad, el tiempo se representa como un **timestamp Unix**: el número de segundos transcurridos desde el 1 de enero de 1970 a las 00:00:00 UTC (el _epoch_). Este formato es ubicuo en logs de sistemas, respuestas de APIs, metadatos de archivos, capturas de red y tráfico de protocolos de red. Python permite convertir entre timestamps Unix y objetos `datetime` de forma directa.

```python
from datetime import datetime, timezone
import time

# Obtener el timestamp Unix actual
unix_now = time.time()
print(f"Timestamp Unix actual: {unix_now:.0f}")

# Convertir timestamp Unix → datetime (zona horaria local)
ts_log = 1718972335
dt_local = datetime.fromtimestamp(ts_log)
print(f"Timestamp {ts_log} → local: {dt_local}")

# Convertir timestamp Unix → datetime UTC (más preciso para correlación)
dt_utc = datetime.fromtimestamp(ts_log, tz=timezone.utc)
print(f"Timestamp {ts_log} → UTC: {dt_utc}")

# Convertir datetime → timestamp Unix
evento = datetime(2026, 6, 21, 14, 32, 15, tzinfo=timezone.utc)
ts_unix = evento.timestamp()
print(f"Datetime → timestamp Unix: {ts_unix:.0f}")

# Caso de uso: parsear timestamps Unix de un log de firewall
firewall_log_entries = [
    {"ts": 1718972335, "src": "203.0.113.5", "dst": "192.168.1.10", "action": "BLOCK"},
    {"ts": 1718972340, "src": "185.220.101.5","dst": "192.168.1.10", "action": "BLOCK"},
    {"ts": 1718972400, "src": "10.0.0.1",    "dst": "8.8.8.8",      "action": "ALLOW"},
]

print("\nLog de firewall parseado:")
for entry in firewall_log_entries:
    readable_ts = datetime.fromtimestamp(entry["ts"]).strftime("%Y-%m-%d %H:%M:%S")
    print(f"  [{readable_ts}] {entry['action']:5} {entry['src']:16} → {entry['dst']}")
```

## Zonas Horarias

Trabajar con zonas horarias es uno de los aspectos más propensos a errores en el manejo de fechas, especialmente en herramientas de ciberseguridad que procesan logs de sistemas distribuidos globalmente o correlacionan eventos de distintas fuentes que pueden estar en diferentes zonas horarias. Python distingue entre objetos _naive_ (sin información de zona horaria) y objetos _aware_ (con zona horaria asociada).

### Objetos _Naive_ vs. Objetos _Aware_

Un objeto `datetime` creado sin información de zona horaria se denomina _naive_: Python no puede determinar a qué instante absoluto corresponde en el tiempo global. Un objeto `datetime` al que se le asocia una zona horaria (`tzinfo`) se denomina _aware_, y representa un instante inequívoco en el tiempo, comparable con otros objetos _aware_ de cualquier zona horaria.

```python
from datetime import datetime, timezone, timedelta

# Objeto naive: sin zona horaria
naive_dt = datetime(2026, 6, 21, 14, 32, 15)
print(f"Naive: {naive_dt}  |  tzinfo: {naive_dt.tzinfo}")   # None

# Objeto aware: con zona horaria UTC
aware_dt = datetime(2026, 6, 21, 14, 32, 15, tzinfo=timezone.utc)
print(f"Aware: {aware_dt}  |  tzinfo: {aware_dt.tzinfo}")   # UTC

# Convertir un datetime naive a aware (añadir información de zona horaria)
naive_log_ts = datetime(2026, 6, 21, 14, 32, 15)
aware_log_ts = naive_log_ts.replace(tzinfo=timezone.utc)
print(f"Convertido a aware: {aware_log_ts}")

# Crear zonas horarias con offset fijo respecto a UTC
utc_minus_3 = timezone(timedelta(hours=-3))   # Argentina (sin DST)
utc_plus_2  = timezone(timedelta(hours=2))    # Europa del Este

# Convertir un mismo instante UTC a distintas zonas horarias
ts_utc = datetime(2026, 6, 21, 14, 32, 15, tzinfo=timezone.utc)
ts_arg = ts_utc.astimezone(utc_minus_3)
ts_cet = ts_utc.astimezone(utc_plus_2)

print(f"\nMismo instante en distintas zonas:")
print(f"  UTC        : {ts_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"  Argentina  : {ts_arg.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"  Europa (+2): {ts_cet.strftime('%Y-%m-%d %H:%M:%S %Z')}")
```

### `pytz`: Zonas Horarias por Nombre

El módulo `pytz` (instalable mediante `pip install pytz`) extiende el soporte de zonas horarias de Python, permitiendo hacer referencia a ellas por su nombre estándar de la base de datos de zonas horarias IANA (como `"America/Argentina/Buenos_Aires"`, `"UTC"`, `"Europe/London"`, `"US/Eastern"`), incluyendo el manejo automático del horario de verano (_Daylight Saving Time_, DST).

```python
# pip install pytz
try:
    import pytz

    # Definir zonas horarias por nombre
    tz_utc    = pytz.utc
    tz_arg    = pytz.timezone("America/Argentina/Buenos_Aires")
    tz_ny     = pytz.timezone("America/New_York")
    tz_london = pytz.timezone("Europe/London")

    # Crear un datetime aware en UTC
    ts_utc = datetime(2026, 6, 21, 14, 32, 15, tzinfo=tz_utc)

    # Convertir a distintas zonas horarias
    ts_arg    = ts_utc.astimezone(tz_arg)
    ts_ny     = ts_utc.astimezone(tz_ny)
    ts_london = ts_utc.astimezone(tz_london)

    print("\nCorrelación de timestamps entre zonas horarias:")
    for label, ts in [("UTC", ts_utc), ("Buenos Aires", ts_arg), ("Nueva York", ts_ny), ("Londres", ts_london)]:
        print(f"  {label:<15}: {ts.strftime('%Y-%m-%d %H:%M:%S %Z (%z)')}")

except ImportError:
    print("\n[!] pytz no está instalado. Ejecutar: pip3 install pytz")
    print("    Se puede usar datetime.timezone con offsets manuales como alternativa.")
```

## Operaciones Avanzadas con Fechas

### `isoformat()` y `fromisoformat()`: el Estándar ISO 8601

El formato ISO 8601 (`YYYY-MM-DDTHH:MM:SS`) es el estándar internacional para representar fechas y horas, y es el que se utiliza en la mayoría de las APIs REST, archivos JSON, bases de datos y protocolos modernos. Python ofrece `isoformat()` para convertir un `datetime` a este formato y `fromisoformat()` para parsear cadenas en este formato (disponible desde Python 3.7).

```python
from datetime import datetime, timezone

ts = datetime(2026, 6, 21, 14, 32, 15, tzinfo=timezone.utc)

# Serializar a ISO 8601 (ideal para JSON y APIs)
iso_string = ts.isoformat()
print(f"ISO 8601: {iso_string}")    # 2026-06-21T14:32:15+00:00

# Deserializar desde ISO 8601
ts_recuperado = datetime.fromisoformat(iso_string)
print(f"Recuperado: {ts_recuperado}")
print(f"Son iguales: {ts == ts_recuperado}")
```

### Calcular Tiempos de Ejecución con `datetime`

Medir el tiempo que tarda en ejecutarse una operación es un caso de uso frecuente, tanto para profiling de herramientas como para estimar el tiempo total de un escaneo largo.

```python
from datetime import datetime
import time

inicio = datetime.now()

# Simulación de una operación que tarda cierto tiempo
time.sleep(0.1)   # simula 100ms de trabajo

fin = datetime.now()
duracion = fin - inicio   # esto devuelve un timedelta

print(f"Inicio   : {inicio.strftime('%H:%M:%S.%f')[:-3]}")   # hasta milisegundos
print(f"Fin      : {fin.strftime('%H:%M:%S.%f')[:-3]}")
print(f"Duración : {duracion.total_seconds():.3f} segundos")
```

### Generación de Timestamps para Nombres de Archivo

Un patrón frecuente al generar reportes, capturas o logs es incluir la fecha y hora en el nombre del archivo para evitar colisiones y facilitar su ordenamiento cronológico.

```python
from datetime import datetime

def generate_report_filename(prefix="report", extension="txt"):
    """Genera un nombre de archivo único con timestamp incluido."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

print(generate_report_filename("escaneo_red"))      # escaneo_red_20260621_143215.txt
print(generate_report_filename("hallazgos", "json")) # hallazgos_20260621_143215.json
print(generate_report_filename("captura", "pcap"))   # captura_20260621_143215.pcap
```

### Parseo Automático de Múltiples Formatos

En herramientas que procesan logs de distintas fuentes, cada fuente puede usar un formato de timestamp diferente. Un patrón útil es intentar parsear el timestamp con cada formato conocido hasta que uno funcione.

```python
from datetime import datetime

KNOWN_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%b %d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%d-%b-%Y %H:%M:%S",
]

def parse_timestamp(raw_string):
    """Intenta parsear un timestamp probando múltiples formatos conocidos."""
    raw_string = raw_string.strip()
    for fmt in KNOWN_FORMATS:
        try:
            return datetime.strptime(raw_string, fmt)
        except ValueError:
            continue
    raise ValueError(f"No se pudo parsear el timestamp: '{raw_string}'")

# Timestamps de distintas fuentes (Syslog, Apache, ISO, etc.)
raw_timestamps = [
    "2026-06-21 14:32:15",
    "2026-06-21T14:32:15",
    "21/06/2026 14:32:15",
    "Jun 21 14:32:15",
    "21-Jun-2026 14:32:15",
]

for raw in raw_timestamps:
    dt = parse_timestamp(raw)
    print(f"  '{raw:<30}' → {dt.strftime('%Y-%m-%d %H:%M:%S')}")
```

## Buenas Prácticas

Probablemente la buena práctica más importante al trabajar con fechas y horas en Python es **siempre usar UTC internamente** y convertir a la zona horaria local solo en el momento de mostrar la información al usuario. Almacenar, comparar y calcular diferencias con fechas _naive_ mezcladas de distintas zonas horarias es una fuente frecuente de errores sutiles y difíciles de detectar, especialmente al correlacionar logs de distintos sistemas.

En la misma línea, siempre que sea posible conviene trabajar con objetos `datetime` _aware_ (con zona horaria explícita) en lugar de objetos _naive_, ya que los primeros representan instantes inequívocos en el tiempo global, mientras que los segundos son ambiguos respecto a la zona horaria que representan. Al serializar fechas para almacenamiento, intercambio de datos o registros de log, el formato ISO 8601 (`isoformat()`) debe ser la opción por defecto, ya que es el estándar internacional más ampliamente adoptado, sin ambigüedad en el orden de los campos y directamente parseable por la mayoría de las herramientas y lenguajes.

Para medir tiempos de ejecución cortos con alta precisión, el módulo `time` con `time.perf_counter()` es más apropiado que `datetime.now()`, ya que ofrece mayor resolución y está diseñado específicamente para la medición de intervalos de tiempo cortos, mientras que `datetime` está diseñado para representar instantes del calendario. Finalmente, al parsear timestamps de fuentes externas, siempre debe protegerse el parseo con un bloque `try/except ValueError`, ya que los logs del mundo real frecuentemente contienen timestamps malformados o en formatos inesperados que, sin ese manejo, interrumpirían la ejecución del script.