#!/usr/bin/env python3

# ---------------------------------------------------------------------------
# 1. if / elif / else: clasificación de un puerto según su criticidad
# ---------------------------------------------------------------------------
print("== 1. if / elif / else ==")
 
puerto = 23
 
if puerto in (21, 23):
    print(f"Puerto {puerto}: protocolo inseguro, hallazgo crítico")
elif puerto in (80, 443):
    print(f"Puerto {puerto}: servicio web, evaluar configuración SSL/TLS")
else:
    print(f"Puerto {puerto}: requiere análisis adicional")
 
 
# ---------------------------------------------------------------------------
# 2. Operadores lógicos: and, or, not
# ---------------------------------------------------------------------------
print("\n== 2. Operadores lógicos ==")
 
puerto_abierto = True
servicio_identificado = "ssh"
version_vulnerable = True
 
if puerto_abierto and servicio_identificado == "ssh" and version_vulnerable:
    print("[!] Posible vector de ataque: SSH con versión vulnerable")
 
if servicio_identificado == "ftp" or servicio_identificado == "telnet":
    print("[!] Protocolo de transmisión en texto plano detectado")
else:
    print(f"Servicio '{servicio_identificado}' no transmite en texto plano")
 
if not puerto_abierto:
    print("El puerto se encuentra cerrado o filtrado")
else:
    print("El puerto se encuentra abierto")
 
 
# ---------------------------------------------------------------------------
# 3. Operadores de pertenencia: in / not in
# ---------------------------------------------------------------------------
print("\n== 3. Operadores de pertenencia ==")
 
puertos_criticos = [21, 23, 445, 3389]
puerto_actual = 445
 
if puerto_actual in puertos_criticos:
    print(f"Puerto {puerto_actual} clasificado como crítico")
 
usuario = "guest_invitado"
if "admin" not in usuario:
    print(f"La cuenta '{usuario}' no contiene la palabra 'admin'")
 
 
# ---------------------------------------------------------------------------
# 4. Operadores de identidad: is / is not
# ---------------------------------------------------------------------------
print("\n== 4. Operadores de identidad ==")
 
resultado_escaneo = None
 
if resultado_escaneo is None:
    print("El escaneo aún no produjo resultados")
else:
    print(f"Resultado disponible: {resultado_escaneo}")
 
 
# ---------------------------------------------------------------------------
# 5. Operador ternario: clasificar el estado de un host en una sola línea
# ---------------------------------------------------------------------------
print("\n== 5. Operador ternario ==")
 
tiempo_respuesta = 0.05
estado = "activo" if tiempo_respuesta < 1.0 else "sin respuesta"
print(f"Estado del host (tiempo {tiempo_respuesta}s): {estado}")
 
tiempo_respuesta_alto = 3.5
estado_2 = "activo" if tiempo_respuesta_alto < 1.0 else "sin respuesta"
print(f"Estado del host (tiempo {tiempo_respuesta_alto}s): {estado_2}")
 
 
# ---------------------------------------------------------------------------
# 6. Condicionales anidados: análisis de un host según estado y servicios
# ---------------------------------------------------------------------------
print("\n== 6. Condicionales anidados ==")
 
host_activo = True
puerto_80_abierto = True
puerto_443_abierto = False
 
if host_activo:
    print("El host respondió al escaneo")
    if puerto_80_abierto:
        print("  -> Servicio web HTTP detectado en el puerto 80")
        if puerto_443_abierto:
            print("     -> HTTPS también disponible en el puerto 443")
        else:
            print("     -> HTTPS no disponible, posible tráfico sin cifrar")
    else:
        print("  -> No se detectaron servicios web")
else:
    print("El host no respondió al escaneo")
