#!/usr/bin/env python3


# ---------------------------------------------------------------------------
# 1. Comprensión básica: transformar tipos de datos
# ---------------------------------------------------------------------------
print("== 1. Comprensión básica ==")
 
# Forma tradicional: convertir puertos en formato texto a enteros
puertos_texto = ["22", "80", "443", "445", "3389"]
 
puertos_enteros_tradicional = []
for p in puertos_texto:
    puertos_enteros_tradicional.append(int(p))
print(f"Forma tradicional: {puertos_enteros_tradicional}")
 
# Misma operación con comprensión de listas
puertos_enteros = [int(p) for p in puertos_texto]
print(f"Comprensión de listas: {puertos_enteros}")
 
 
# ---------------------------------------------------------------------------
# 2. Comprensión con filtro: extraer solo los elementos que cumplen una condición
# ---------------------------------------------------------------------------
print("\n== 2. Comprensión con filtro (if) ==")
 
puertos_detectados = [21, 22, 23, 80, 443, 445, 3389]
puertos_criticos = [21, 23, 445, 3389]
 
# Filtrar únicamente los puertos considerados críticos
hallazgos_criticos = [p for p in puertos_detectados if p in puertos_criticos]
print(f"Puertos críticos detectados: {hallazgos_criticos}")
 
# Filtrar hosts activos a partir de una lista de diccionarios
resultados_escaneo = [
    {"host": "192.168.1.10", "activo": True},
    {"host": "192.168.1.11", "activo": False},
    {"host": "192.168.1.12", "activo": True},
    {"host": "192.168.1.13", "activo": False},
]
 
hosts_activos = [r["host"] for r in resultados_escaneo if r["activo"]]
print(f"Hosts activos: {hosts_activos}")
 
 
# ---------------------------------------------------------------------------
# 3. Comprensión con condicional ternario: transformar según una condición
# ---------------------------------------------------------------------------
print("\n== 3. Comprensión con if/else (ternario) ==")
 
# Clasificar cada puerto como "crítico" o "estándar" según pertenezca o no
# a la lista de puertos críticos, conservando todos los elementos
puertos_clasificados = [
    f"{p} (crítico)" if p in puertos_criticos else f"{p} (estándar)"
    for p in puertos_detectados
]
print(f"Clasificación de puertos: {puertos_clasificados}")
 
 
# ---------------------------------------------------------------------------
# 4. Comprensión aplicada a cadenas: normalizar y transformar texto
# ---------------------------------------------------------------------------
print("\n== 4. Comprensión sobre cadenas ==")
 
# Normalizar una lista de hosts eliminando espacios y pasando a minúsculas
hosts_crudos = ["  Host-A.local  ", "HOST-B.local", " host-c.local"]
hosts_normalizados = [h.strip().lower() for h in hosts_crudos]
print(f"Hosts normalizados: {hosts_normalizados}")
 
# Construir una lista de URLs a partir de una lista de hosts
hosts = ["192.168.1.10", "192.168.1.11", "192.168.1.12"]
urls = [f"http://{h}:8080" for h in hosts]
print(f"URLs generadas: {urls}")
 
 
# ---------------------------------------------------------------------------
# 5. Comprensión anidada: combinar hosts y puertos en pares (host, puerto)
# ---------------------------------------------------------------------------
print("\n== 5. Comprensión anidada ==")
 
hosts_a_escanear = ["192.168.1.10", "192.168.1.11"]
puertos_a_escanear = [22, 80, 443]
 
# Equivalente a un doble bucle for anidado: genera todas las combinaciones
objetivos_escaneo = [
    (host, puerto)
    for host in hosts_a_escanear
    for puerto in puertos_a_escanear
]
print(f"Combinaciones host:puerto a escanear ({len(objetivos_escaneo)} en total):")
for objetivo in objetivos_escaneo:
    print(f"  -> {objetivo[0]}:{objetivo[1]}")
 
 
# ---------------------------------------------------------------------------
# 6. Comparación de rendimiento: bucle for vs. comprensión de listas
# ---------------------------------------------------------------------------
print("\n== 6. Comparación de rendimiento ==")
 
import timeit
 
rango_simulado = range(100_000)
 
def con_bucle_for():
    resultado = []
    for n in rango_simulado:
        resultado.append(n * 2)
    return resultado
 
def con_comprension():
    return [n * 2 for n in rango_simulado]
 
tiempo_for = timeit.timeit(con_bucle_for, number=20)
tiempo_comprension = timeit.timeit(con_comprension, number=20)
 
print(f"Tiempo con bucle for:         {tiempo_for:.4f} seg")
print(f"Tiempo con comprensión de listas: {tiempo_comprension:.4f} seg")
