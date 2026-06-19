#!/usr/bin/env python3

# ---------------------------------------------------------------------------
# 1. Bucle for: recorrer una lista de puertos a escanear
# ---------------------------------------------------------------------------
print("== 1. Bucle for ==")
 
puertos = [22, 80, 443]
 
for puerto in puertos:
    print(f"Escaneando puerto {puerto}...")
 
 
# ---------------------------------------------------------------------------
# 2. Bucle while: reintentar una conexión hasta lograr respuesta o agotar intentos
# ---------------------------------------------------------------------------
print("\n== 2. Bucle while ==")
 
intentos = 0
maximo_intentos = 5
conexion_exitosa = False
 
while intentos < maximo_intentos and not conexion_exitosa:
    intentos += 1
    print(f"Intento {intentos} de conexión...")
    if intentos == 3:
        conexion_exitosa = True   # simula que la conexión se logró en el intento 3
 
print(f"Conexión exitosa: {conexion_exitosa} (en {intentos} intentos)")
 
 
# ---------------------------------------------------------------------------
# 3. Bucles anidados: escanear varios puertos en varios hosts
# ---------------------------------------------------------------------------
print("\n== 3. Bucles anidados ==")
 
hosts = ["192.168.1.10", "192.168.1.11"]
puertos_a_revisar = [22, 80, 443]
 
for host in hosts:
    print(f"Analizando host: {host}")
    for puerto in puertos_a_revisar:
        print(f"  -> Verificando puerto {puerto}")
 
 
# ---------------------------------------------------------------------------
# 4. break: detener el escaneo apenas se encuentra un puerto crítico abierto
# ---------------------------------------------------------------------------
print("\n== 4. break ==")
 
puertos_detectados = [21, 22, 80, 23, 443]
puertos_criticos = [21, 23, 3389]
 
for puerto in puertos_detectados:
    if puerto in puertos_criticos:
        print(f"[!] Puerto crítico {puerto} encontrado, deteniendo el escaneo")
        break
    print(f"Puerto {puerto} verificado, continuando...")
 
 
# ---------------------------------------------------------------------------
# 5. continue: omitir puertos ya conocidos como cerrados
# ---------------------------------------------------------------------------
print("\n== 5. continue ==")
 
puertos_a_analizar = [21, 22, 80, 443, 8080]
puertos_cerrados_conocidos = [21, 8080]
 
for puerto in puertos_a_analizar:
    if puerto in puertos_cerrados_conocidos:
        continue
    print(f"Analizando puerto {puerto} en detalle...")
 
 
# ---------------------------------------------------------------------------
# 6. pass: estructura pendiente de implementación
# ---------------------------------------------------------------------------
print("\n== 6. pass ==")
 
for puerto in [22, 80, 443]:
    if puerto == 443:
        pass   # TODO: implementar lógica específica para analizar HTTPS
    else:
        print(f"Puerto {puerto} sin tratamiento especial todavía")
 
 
# ---------------------------------------------------------------------------
# 7. else en bucle for: distinguir "encontrado" vs "no encontrado"
# ---------------------------------------------------------------------------
print("\n== 7. else en for ==")
 
puertos_host = [22, 80, 443]
puerto_vulnerable = 3389
 
for puerto in puertos_host:
    if puerto == puerto_vulnerable:
        print(f"[!] Puerto vulnerable {puerto} encontrado")
        break
else:
    print("No se encontraron puertos vulnerables conocidos en este host")
 
 
# ---------------------------------------------------------------------------
# 8. else en bucle while: distinguir agotamiento de intentos vs éxito
# ---------------------------------------------------------------------------
print("\n== 8. else en while ==")
 
intentos = 0
maximo_intentos = 3
credencial_valida = False
 
while intentos < maximo_intentos:
    intentos += 1
    print(f"Probando credencial, intento {intentos}")
    if credencial_valida:
        print("Acceso concedido")
        break
else:
    print("Se agotaron los intentos sin lograr autenticación")
 
 
# ---------------------------------------------------------------------------
# 9. Comprensión de listas: forma tradicional vs. comprensión
# ---------------------------------------------------------------------------
print("\n== 9. Comprensión de listas ==")
 
puertos_texto = ["22", "80", "443"]
 
# Forma tradicional
puertos_enteros_tradicional = []
for p in puertos_texto:
    puertos_enteros_tradicional.append(int(p))
print(f"Forma tradicional: {puertos_enteros_tradicional}")
 
# Forma con comprensión de listas
puertos_enteros = [int(p) for p in puertos_texto]
print(f"Comprensión de listas: {puertos_enteros}")
 
# Comprensión de listas con filtro: solo puertos críticos detectados
puertos_detectados_full = [21, 22, 23, 80, 443, 445, 3389]
puertos_criticos_full = [21, 23, 445, 3389]
 
hallazgos_criticos = [p for p in puertos_detectados_full if p in puertos_criticos_full]
print(f"Hallazgos críticos: {hallazgos_criticos}")
