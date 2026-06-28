#!/usr/bin/env python3
import sys

import requests
import urllib3

# Silenciar InsecureRequestWarning para cuando verify=False (certificados autofirmados)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─────────────────────────────────────────────────────────────────────
# Cabeceras que revelan tecnología o versión (interesantes para fingerprinting)
TECHNOLOGY_HEADERS = [
    "Server",
    "X-Powered-By",
    "X-AspNet-Version",
    "X-AspNetMvc-Version",
    "X-Generator",
    "X-Drupal-Cache",
    "X-Wordpress-Powered-By",
    "Via",
    "X-Varnish",
    "CF-Cache-Status",  # Cloudflare
    "X-Cache",
]

# Cabeceras de seguridad que DEBEN estar presentes en una web bien configurada
SECURITY_HEADERS = [
    "Strict-Transport-Security",  # fuerza HTTPS
    "Content-Security-Policy",  # previene XSS
    "X-Frame-Options",  # previene clickjacking
    "X-Content-Type-Options",  # previene MIME sniffing
    "Referrer-Policy",  # controla el header Referer
    "Permissions-Policy",  # controla permisos del navegador
    "Cross-Origin-Opener-Policy",
    "Cross-Origin-Resource-Policy",
]

# Cabeceras que podrían revelar información del entorno interno
SENSITIVE_HEADERS = [
    "X-Debug",
    "X-Debug-Token",
    "X-Debug-Token-Link",
    "X-Environment",
    "X-Application-Context",
    "X-Powered-CMS",
    "X-Backend-Server",
    "X-Internal-IP",
    "X-Original-URL",
    "X-Rewrite-URL",
]

WIDTH = 62


def separator(title=""):
    print(f"\n  {'─' * (WIDTH - 4)} {title}" if title else f"\n{'─' * WIDTH}")


def analyze_headers(url: str):
    """
    Envía una petición HEAD al objetivo y analiza sus cabeceras de respuesta.
    Usa HEAD (no GET) porque solo necesitamos las cabeceras, no el body.
    Esto reduce el ancho de banda consumido y es más discreto.

    Args:
        url: URL completa del objetivo a analizar.
    """
    print(f"\n{'═' * WIDTH}")
    print("  ANÁLISIS DE CABECERAS HTTP")
    print(f"{'═' * WIDTH}")
    print(f"  Objetivo: {url}")

    try:
        # timeout=(conexión, lectura): 5s para conectar, 10s para recibir respuesta
        # verify=False: útil en entornos con certificados autofirmados (laboratorios)
        response = requests.get(
            url, verify=False, timeout=(5, 10), allow_redirects=True
        )

        print(f"  Código de estado  : {response.status_code} {response.reason}")
        print(f"  URL final         : {response.url}")
        print(f"  Tiempo respuesta  : {response.elapsed.total_seconds():.3f}s")

        headers = response.headers

        # ── 1. Todas las cabeceras recibidas ─────────────────────────
        separator("CABECERAS RECIBIDAS")
        print(f"  Total: {len(headers)} cabecera(s)\n")
        for header_name, header_value in headers.items():
            print(f"  {header_name:<38}: {header_value}")

        # ── 2. Fingerprinting de tecnología ──────────────────────────
        separator("TECNOLOGÍAS IDENTIFICADAS")
        tech_found = False
        for header in TECHNOLOGY_HEADERS:
            value = headers.get(header)
            if value:
                print(f"  [+] {header:<38}: {value}")
                tech_found = True
        if not tech_found:
            print("  [-] No se identificaron cabeceras de tecnología")

        # ── 3. Análisis de cabeceras de seguridad ─────────────────────
        separator("CABECERAS DE SEGURIDAD")
        present = []
        missing = []

        for sec_header in SECURITY_HEADERS:
            if sec_header in headers:
                present.append((sec_header, headers[sec_header]))
            else:
                missing.append(sec_header)

        if present:
            print(f"  Presentes ({len(present)}):")
            for name, value in present:
                # Truncar valores muy largos para no romper el formato
                display_value = value[:50] + "..." if len(value) > 50 else value
                print(f"    [✓] {name:<38}: {display_value}")

        if missing:
            print(f"\n  Ausentes ({len(missing)}) — posibles hallazgos:")
            for name in missing:
                print(f"    [✗] {name}")

        # Calcular puntuación de seguridad básica
        score = int((len(present) / len(SECURITY_HEADERS)) * 100)
        print(
            f"\n  Puntuación de seguridad de cabeceras: {score}% "
            f"({len(present)}/{len(SECURITY_HEADERS)} presentes)"
        )

        # ── 4. Detección de cabeceras sensibles ───────────────────────
        separator("CABECERAS POTENCIALMENTE SENSIBLES")
        sensitive_found = False
        for header in SENSITIVE_HEADERS:
            value = headers.get(header)
            if value:
                print(f"  [!] {header}: {value}")
                sensitive_found = True
        if not sensitive_found:
            print("  [-] No se detectaron cabeceras sensibles evidentes")

        # ── 5. Análisis de cookies ────────────────────────────────────
        separator("COOKIES")
        if response.cookies:
            print(f"  Total cookies recibidas: {len(response.cookies)}\n")
            for cookie in response.cookies:
                flags = []
                if cookie.secure:
                    flags.append("Secure")
                if cookie.has_nonstandard_attr("HttpOnly"):
                    flags.append("HttpOnly")
                if cookie.has_nonstandard_attr("SameSite"):
                    flags.append(f"SameSite={cookie.get_nonstandard_attr('SameSite')}")

                print(f"  [+] {cookie.name}")
                print(
                    f"      Valor  : {str(cookie.value)[:30]}{'...' if len(str(cookie.value)) > 30 else ''}"
                )
                print(
                    f"      Flags  : {', '.join(flags) if flags else 'ninguno — posible vulnerabilidad'}"
                )
                print(f"      Dominio: {cookie.domain or 'no definido'}")
        else:
            print("  [-] No se recibieron cookies en la respuesta")

        print(f"\n{'═' * WIDTH}\n")

    except requests.exceptions.ConnectionError:
        print(f"\n  [!] Error de conexión: no se pudo alcanzar '{url}'")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"\n  [!] Tiempo de espera agotado al conectar con '{url}'")
        sys.exit(1)
    except requests.exceptions.RequestException as error:
        print(f"\n  [!] Error inesperado: {error}")
        sys.exit(1)


def main():
    # Análisis de un único objetivo
    target_url = "https://ntech.studio"
    analyze_headers(target_url)


if __name__ == "__main__":
    main()
