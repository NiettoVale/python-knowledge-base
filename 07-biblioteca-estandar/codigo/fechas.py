#!/usr/bin/env python3
from datetime import datetime, date, timedelta, timezone
import time

WIDTH = 62

def section(title):
    print(f"\n{'═' * WIDTH}")
    print(f" {title}")
    print(f"{'═' * WIDTH}")

def sub(title):
    print(f"\n  ── {title}")


# ═════════════════════════════════════════════════════════════
# 1. TIPOS FUNDAMENTALES Y FECHA/HORA ACTUAL
# ═════════════════════════════════════════════════════════════
section("1. TIPOS FUNDAMENTALES Y FECHA/HORA ACTUAL")

sub("Fecha y hora actuales del sistema")
now = datetime.now()
today = date.today()

print(f"  Fecha y hora actual : {now}")
print(f"  Solo fecha          : {today}")
print(f"  Solo hora           : {now.time()}")

sub("Componentes individuales del datetime actual")
print(f"  Año        : {now.year}")
print(f"  Mes        : {now.month:02d}")
print(f"  Día        : {now.day:02d}")
print(f"  Hora       : {now.hour:02d}:{now.minute:02d}:{now.second:02d}")
print(f"  Microseg.  : {now.microsecond}")
print(f"  Día semana : {now.strftime('%A')} (índice {now.weekday()}, 0=lunes)")
print(f"  Día del año: {now.timetuple().tm_yday}")

sub("Datetime en UTC (recomendado para logs)")
now_utc = datetime.now(tz=timezone.utc)
print(f"  Ahora en UTC: {now_utc}")
print(f"  ISO 8601    : {now_utc.isoformat()}")


# ═════════════════════════════════════════════════════════════
# 2. CREACIÓN MANUAL Y strftime
# ═════════════════════════════════════════════════════════════
section("2. CREACIÓN MANUAL Y FORMATEO CON strftime")

# Evento de seguridad con fecha y hora conocidas
incident_start = datetime(2026, 6, 21, 2, 17, 43)
incident_end   = datetime(2026, 6, 21, 4, 55, 12)

sub("Formatos de fecha habituales en reportes")
print(f"  ISO 8601        : {incident_start.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  Europeo         : {incident_start.strftime('%d/%m/%Y %H:%M:%S')}")
print(f"  Solo fecha      : {incident_start.strftime('%d de %B de %Y')}")
print(f"  12h con AM/PM   : {incident_start.strftime('%I:%M:%S %p')}")
print(f"  Para archivo    : {incident_start.strftime('%Y%m%d_%H%M%S')}")

sub("Datos del incidente formateados")
duration = incident_end - incident_start
total_minutes = duration.total_seconds() / 60
print(f"  Inicio          : {incident_start.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  Fin             : {incident_end.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  Duración        : {total_minutes:.1f} minutos ({duration.total_seconds():.0f} segundos)")


# ═════════════════════════════════════════════════════════════
# 3. PARSEO CON strptime
# ═════════════════════════════════════════════════════════════
section("3. PARSEO DE TIMESTAMPS CON strptime")

sub("Parsear distintos formatos de log del mundo real")
# Cada fuente de log puede usar un formato diferente
raw_log_entries = [
    ("Syslog estándar",  "2026-06-21 02:17:43",        "%Y-%m-%d %H:%M:%S"),
    ("Auth.log Linux",   "Jun 21 02:17:43",             "%b %d %H:%M:%S"),
    ("Formato ISO 8601", "2026-06-21T02:17:43",         "%Y-%m-%dT%H:%M:%S"),
    ("Apache access.log","21/Jun/2026:02:17:43",        "%d/%b/%Y:%H:%M:%S"),
    ("Formato europeo",  "21/06/2026 02:17:43",         "%d/%m/%Y %H:%M:%S"),
    ("Nombre de archivo","20260621_021743",              "%Y%m%d_%H%M%S"),
]

for source, raw, fmt in raw_log_entries:
    try:
        parsed = datetime.strptime(raw, fmt)
        # Si el formato no tiene año, tomamos el actual para visualización
        if parsed.year == 1900:
            parsed = parsed.replace(year=now.year)
        print(f"  {source:<20} → {parsed.strftime('%Y-%m-%d %H:%M:%S')}")
    except ValueError as error:
        print(f"  [ERROR] {source}: {error}")

sub("Parseo defensivo con fallback entre múltiples formatos")

KNOWN_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%b %d %H:%M:%S",
    "%d/%b/%Y:%H:%M:%S",
]

def try_parse(raw_string):
    """Intenta parsear un timestamp probando múltiples formatos conocidos."""
    for fmt in KNOWN_FORMATS:
        try:
            return datetime.strptime(raw_string.strip(), fmt)
        except ValueError:
            continue
    return None   # no se pudo parsear con ningún formato conocido

mixed_timestamps = [
    "2026-06-21 02:17:43",
    "2026-06-21T02:17:43",
    "21/06/2026 02:17:43",
    "formato_desconocido",
]

for raw in mixed_timestamps:
    result = try_parse(raw)
    if result:
        print(f"  [OK]    '{raw}' → {result.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"  [ERROR] '{raw}' → formato no reconocido, se descarta")


# ═════════════════════════════════════════════════════════════
# 4. timedelta: CÁLCULOS DE TIEMPO
# ═════════════════════════════════════════════════════════════
section("4. timedelta: CÁLCULOS Y DIFERENCIAS DE TIEMPO")

sub("Antigüedad de vulnerabilidades detectadas")
# Simula vulnerabilidades encontradas en distintas fechas
today_sim = datetime(2026, 6, 21)
vulnerabilities = [
    ("CVE-2020-1472", "ZeroLogon",        datetime(2026, 1, 15)),
    ("CVE-2021-41773","Path Traversal",   datetime(2026, 5, 30)),
    ("CVE-2023-23397","Outlook RCE",      datetime(2026, 6, 18)),
    ("CVE-2022-26134","Confluence RCE",   datetime(2026, 3, 10)),
]

CRITICAL_THRESHOLD = 90   # días sin remediar para considerarse crítico
WARNING_THRESHOLD  = 30

print(f"  {'CVE':<16}{'NOMBRE':<22}{'DÍAS SIN REMEDIAR':<22}{'ESTADO'}")
print("  " + "─" * 62)
for cve_id, name, detected_date in vulnerabilities:
    age_days = (today_sim - detected_date).days
    if age_days >= CRITICAL_THRESHOLD:
        status = "🔴 CRÍTICO"
    elif age_days >= WARNING_THRESHOLD:
        status = "🟡 ALERTA"
    else:
        status = "🟢 RECIENTE"
    print(f"  {cve_id:<16}{name:<22}{age_days:<22}{status}")

sub("Calcular ventana de ataque de un incidente")
# Tiempo entre el primer indicador de compromiso y la detección
first_ioc   = datetime(2026, 6, 21, 2, 17, 43)   # primera actividad maliciosa
detection   = datetime(2026, 6, 21, 14, 32, 00)  # cuándo fue detectado
remediation = datetime(2026, 6, 21, 16, 45, 30)  # cuándo fue contenido

dwell_time    = detection - first_ioc
response_time = remediation - detection

print(f"  Primer IoC    : {first_ioc.strftime('%H:%M:%S')}")
print(f"  Detección     : {detection.strftime('%H:%M:%S')}")
print(f"  Remediación   : {remediation.strftime('%H:%M:%S')}")
print(f"  Tiempo de permanencia : {dwell_time.total_seconds()/3600:.2f} horas")
print(f"  Tiempo de respuesta   : {response_time.total_seconds()/60:.1f} minutos")

sub("Programar fechas futuras de seguimiento")
baseline_date = datetime(2026, 6, 21)
milestones = {
    "Revisión inicial"    : timedelta(days=7),
    "Validación de parche": timedelta(days=15),
    "Revisión completa"   : timedelta(days=30),
    "Informe ejecutivo"   : timedelta(days=45),
    "Auditoría final"     : timedelta(days=90),
}

print(f"  Fecha de inicio del seguimiento: {baseline_date.strftime('%d/%m/%Y')}")
for milestone, delta in milestones.items():
    due_date = baseline_date + delta
    print(f"  {milestone:<25}: {due_date.strftime('%d/%m/%Y')} (día {(due_date - baseline_date).days})")


# ═════════════════════════════════════════════════════════════
# 5. COMPARACIÓN Y ORDENAMIENTO DE TIMESTAMPS
# ═════════════════════════════════════════════════════════════
section("5. COMPARACIÓN Y ORDENAMIENTO DE TIMESTAMPS")

sub("Expiración de certificados TLS")
today_cert = datetime(2026, 6, 21)
certificates = [
    ("empresa.com",      datetime(2026, 7, 1)),    # vence en 10 días
    ("api.empresa.com",  datetime(2026, 12, 31)),   # vence en 6 meses
    ("old.empresa.com",  datetime(2026, 5, 15)),    # ya expiró
    ("vpn.empresa.com",  datetime(2026, 6, 30)),    # vence en 9 días
    ("mail.empresa.com", datetime(2027, 3, 15)),    # vence en 9 meses
]

print(f"  {'DOMINIO':<22}{'VENCIMIENTO':<14}{'DÍAS':<8}{'ESTADO'}")
print("  " + "─" * 55)
for domain, expiry in sorted(certificates, key=lambda x: x[1]):
    days_left = (expiry - today_cert).days
    if days_left < 0:
        status = "❌ EXPIRADO"
    elif days_left <= 14:
        status = "🔴 URGENTE"
    elif days_left <= 30:
        status = "🟡 PRÓXIMO"
    else:
        status = "🟢 OK"
    print(f"  {domain:<22}{expiry.strftime('%Y-%m-%d'):<14}{days_left:<8}{status}")

sub("Ordenar línea de tiempo de un incidente")
# Los eventos llegan desordenados desde distintas fuentes
raw_events = [
    ("Firewall",  "Conexión bloqueada a C2",     "2026-06-21 03:42:11"),
    ("EDR",       "Proceso sospechoso detectado","2026-06-21 02:19:05"),
    ("SIEM",      "Regla de correlación activada","2026-06-21 03:55:00"),
    ("Auth Log",  "Login SSH exitoso como root",  "2026-06-21 02:17:43"),
    ("Web proxy", "Descarga de payload",          "2026-06-21 02:18:30"),
    ("SIEM",      "Alerta: movimiento lateral",   "2026-06-21 03:10:22"),
]

fmt = "%Y-%m-%d %H:%M:%S"
# Convertir los timestamps a datetime para poder ordenar
parsed_events = [
    (source, description, datetime.strptime(ts, fmt))
    for source, description, ts in raw_events
]

print(f"\n  {'HORA':<12}{'FUENTE':<12}{'EVENTO'}")
print("  " + "─" * 55)
for source, description, ts in sorted(parsed_events, key=lambda x: x[2]):
    print(f"  {ts.strftime('%H:%M:%S'):<12}{source:<12}{description}")


# ═════════════════════════════════════════════════════════════
# 6. TIMESTAMPS UNIX
# ═════════════════════════════════════════════════════════════
section("6. TIMESTAMPS UNIX (EPOCH)")

sub("Conversión Unix timestamp ↔ datetime")
unix_timestamps = [1718972335, 1719038400, 1700000000]

print(f"  {'UNIX TIMESTAMP':<18}{'FECHA/HORA LOCAL':<25}{'FECHA/HORA UTC'}")
print("  " + "─" * 65)
for ts in unix_timestamps:
    dt_local = datetime.fromtimestamp(ts)
    dt_utc   = datetime.fromtimestamp(ts, tz=timezone.utc)
    print(f"  {ts:<18}{dt_local.strftime('%Y-%m-%d %H:%M:%S'):<25}{dt_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC")

sub("Parsear log de firewall con timestamps Unix")
firewall_entries = [
    {"ts": 1718972100, "src": "203.0.113.5",   "dst_port": 22,   "action": "DROP"},
    {"ts": 1718972335, "src": "185.220.101.5", "dst_port": 443,  "action": "DROP"},
    {"ts": 1718972400, "src": "198.51.100.7",  "dst_port": 3389, "action": "DROP"},
    {"ts": 1718972450, "src": "10.0.0.1",      "dst_port": 80,   "action": "ACCEPT"},
]

drop_count = sum(1 for e in firewall_entries if e["action"] == "DROP")
print(f"  Total entradas: {len(firewall_entries)} | Bloqueadas: {drop_count}")
print()
print(f"  {'TIMESTAMP':<22}{'ORIGEN':<20}{'PUERTO':<10}{'ACCIÓN'}")
print("  " + "─" * 56)
for entry in firewall_entries:
    readable = datetime.fromtimestamp(entry["ts"]).strftime("%Y-%m-%d %H:%M:%S")
    action_icon = "❌" if entry["action"] == "DROP" else "✅"
    print(f"  {readable:<22}{entry['src']:<20}{entry['dst_port']:<10}{action_icon} {entry['action']}")


# ═════════════════════════════════════════════════════════════
# 7. ZONAS HORARIAS
# ═════════════════════════════════════════════════════════════
section("7. ZONAS HORARIAS")

sub("Correlacionar el mismo evento en distintas zonas horarias")
# Un atacante opera a las 14:32 UTC — ¿qué hora era en cada región?
incident_utc = datetime(2026, 6, 21, 14, 32, 15, tzinfo=timezone.utc)

regions = [
    ("UTC",               timezone.utc),
    ("Argentina (UTC-3)", timezone(timedelta(hours=-3))),
    ("España (UTC+2)",    timezone(timedelta(hours=2))),
    ("India (UTC+5:30)",  timezone(timedelta(hours=5, minutes=30))),
    ("Japón (UTC+9)",     timezone(timedelta(hours=9))),
]

print(f"  Evento referencia UTC: {incident_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print()
print(f"  {'REGIÓN':<25}{'HORA LOCAL DEL ATAQUE'}")
print("  " + "─" * 48)
for region_name, tz in regions:
    local_time = incident_utc.astimezone(tz)
    print(f"  {region_name:<25}{local_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")

sub("Convertir timestamps naive a aware antes de comparar")
# Dos logs de sistemas en zonas distintas: comparación incorrecta vs correcta
log_server_a = datetime(2026, 6, 21, 11, 32, 15)   # naive (Argentina UTC-3)
log_server_b = datetime(2026, 6, 21, 14, 32, 15)   # naive (UTC)

# Comparación incorrecta: Python compara los números sin considerar la zona
print(f"  Comparación naive (INCORRECTA): server_a < server_b = {log_server_a < log_server_b}")
print(f"  (Parecen distintos, pero representan el MISMO instante!)")

# Comparación correcta: hacerlos aware primero
aware_a = log_server_a.replace(tzinfo=timezone(timedelta(hours=-3)))
aware_b = log_server_b.replace(tzinfo=timezone.utc)
print(f"  Comparación aware  (CORRECTA) : server_a == server_b = {aware_a == aware_b}")


# ═════════════════════════════════════════════════════════════
# 8. CASOS DE USO INTEGRADOS
# ═════════════════════════════════════════════════════════════
section("8. CASOS DE USO INTEGRADOS")

sub("Generar nombre de reporte con timestamp")
def generate_report_name(engagement_name, report_type="full"):
    """Genera un nombre de archivo único para un reporte de seguridad."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = engagement_name.lower().replace(" ", "_")
    return f"{safe_name}_{report_type}_{ts}.md"

engagements = [
    ("Empresa SA", "executive"),
    ("Red Interna", "technical"),
    ("API Gateway", "remediation"),
]
for name, rtype in engagements:
    print(f"  {generate_report_name(name, rtype)}")

sub("Calcular métricas de tiempo de respuesta a incidentes")
incidents = [
    {"id": "INC-001", "detected": datetime(2026, 6, 21, 2, 17, 43),
                       "contained": datetime(2026, 6, 21, 4, 55, 12)},
    {"id": "INC-002", "detected": datetime(2026, 6, 20, 18, 00, 00),
                       "contained": datetime(2026, 6, 21, 9, 30, 00)},
    {"id": "INC-003", "detected": datetime(2026, 6, 19, 10, 00, 00),
                       "contained": datetime(2026, 6, 19, 10, 45, 00)},
]

print(f"\n  {'ID':<10}{'DETECCIÓN':<22}{'CONTENCIÓN':<22}{'TIEMPO RESPUESTA'}")
print("  " + "─" * 68)

total_response = timedelta()
for inc in incidents:
    response_time = inc["contained"] - inc["detected"]
    total_response += response_time
    hours   = response_time.total_seconds() // 3600
    minutes = (response_time.total_seconds() % 3600) // 60
    print(f"  {inc['id']:<10}"
          f"{inc['detected'].strftime('%Y-%m-%d %H:%M'):<22}"
          f"{inc['contained'].strftime('%Y-%m-%d %H:%M'):<22}"
          f"{int(hours)}h {int(minutes)}m")

avg_response = total_response / len(incidents)
avg_hours   = avg_response.total_seconds() // 3600
avg_minutes = (avg_response.total_seconds() % 3600) // 60
print("  " + "─" * 68)
print(f"  {'TIEMPO MEDIO DE RESPUESTA (MTTR)':<54}{int(avg_hours)}h {int(avg_minutes)}m")

sub("Medir tiempo de ejecución de un escaneo")
scan_start = time.perf_counter()
# Simulación de un escaneo que tarda cierto tiempo
time.sleep(0.12)
scan_end = time.perf_counter()
elapsed = scan_end - scan_start

start_dt = datetime.now()
print(f"  Inicio del escaneo : {start_dt.strftime('%H:%M:%S')}")
print(f"  Tiempo de ejecución: {elapsed:.3f} segundos")
print(f"  Equivalente        : {elapsed*1000:.1f} ms")

print(f"\n{'═' * WIDTH}\n")