#!/usr/bin/env python3
import os
import sys

import requests
import urllib3

# Silenciar las advertencias de InsecureRequestWarning cuando verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─────────────────────────────────────────────────────────────────────
# Códigos de estado que consideramos "no interesantes" (nada encontrado)
IGNORE_CODES = {404, 400}

# Extensiones a probar por cada palabra del wordlist
EXTENSIONS = ["", ".php", ".html", ".bak", ".txt", ".json", ".xml"]

# Timeout para cada petición individual (en segundos)
REQUEST_TIMEOUT = 5


# ─────────────────────────────────────────────────────────────────────
def read_wordlist(file_path: str) -> list[str]:
    """
    Lee un archivo de wordlist línea por línea.
    Elimina espacios y líneas vacías. Termina el programa si el archivo no existe.

    Args:
        file_path: ruta al archivo de wordlist.

    Returns:
        Lista de palabras limpias.
    """
    if not os.path.exists(file_path):
        print(f"\n[!] Error: El fichero '{file_path}' no existe.")
        sys.exit(1)

    wordlist = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            word = line.strip()
            if word and not word.startswith("#"):  # ignorar líneas vacías y comentarios
                wordlist.append(word)

    return wordlist


def fuzz_target(base_url: str, wordlist: list[str]) -> list[tuple]:
    """
    Itera sobre el wordlist probando cada palabra (y sus extensiones) contra la URL base.
    Registra todos los recursos cuyo código de estado no esté en IGNORE_CODES.

    Args:
        base_url: URL raíz del objetivo (ej: https://empresa.com).
        wordlist: lista de palabras a probar.

    Returns:
        Lista de tuplas (url, status_code) de los recursos encontrados.
    """
    found = []

    # Usar Session reutiliza la conexión TCP entre peticiones al mismo servidor,
    # reduciendo el overhead de establecer una nueva conexión en cada iteración.
    with requests.Session() as session:
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (compatible; WebFuzzer/1.0)",
            }
        )

        processed = 0

        for word in wordlist:
            for ext in EXTENSIONS:
                processed += 1
                target_url = f"{base_url.rstrip('/')}/{word}{ext}"

                try:
                    response = session.get(
                        target_url,
                        verify=False,  # útil en servidores con cert autofirmado
                        timeout=REQUEST_TIMEOUT,
                        allow_redirects=False,  # ver el código real sin seguir redirecciones
                    )

                    if response.status_code not in IGNORE_CODES:
                        entry = (target_url, response.status_code)
                        found.append(entry)
                        # Mostrar resultado inmediatamente (no esperar al final)
                        _print_result(response.status_code, target_url)

                except requests.exceptions.Timeout:
                    # El servidor no respondió: no es un hallazgo, se ignora
                    pass
                except requests.exceptions.ConnectionError:
                    print(f"  [!] Error de conexión: {target_url}")
                except requests.exceptions.RequestException as error:
                    # Cualquier otro error de requests (URL malformada, SSL, etc.)
                    print(f"  [!] Error inesperado en {target_url}: {error}")

        # Mostrar progreso al finalizar
        print(f"\n  [*] Peticiones enviadas: {processed:,}")

    return found


def _print_result(status_code: int, url: str):
    """Imprime un hallazgo con el color apropiado según el código de estado."""
    # Clasificación visual por código de estado
    if status_code == 200:
        tag = "[200 OK]      "
    elif status_code in (301, 302, 307, 308):
        tag = f"[{status_code} REDIRECT]"
    elif status_code == 403:
        tag = "[403 FORBIDDEN]"
    elif status_code == 401:
        tag = "[401 AUTH REQ] "
    elif status_code == 500:
        tag = "[500 ERROR]    "
    else:
        tag = f"[{status_code}]          "

    print(f"  {tag} {url}")


def show_summary(results: list[tuple]):
    """Muestra un resumen final agrupado por código de estado."""
    if not results:
        print("\n  [-] No se encontraron recursos.")
        return

    print(f"\n{'═' * 60}")
    print(f"  RESUMEN — {len(results)} recurso(s) encontrado(s)")
    print(f"{'═' * 60}")

    # Agrupar por código de estado
    by_status: dict[int, list[str]] = {}
    for url, status in results:
        by_status.setdefault(status, []).append(url)

    for status in sorted(by_status.keys()):
        print(f"\n  [{status}] → {len(by_status[status])} resultado(s):")
        for url in by_status[status]:
            print(f"    {url}")


def create_sample_wordlist(path: str):
    """Crea un wordlist de muestra si no existe ninguno."""
    sample_words = [
        "admin",
        "login",
        "dashboard",
        "uploads",
        "backup",
        "config",
        "api",
        "v1",
        "users",
        "test",
        "dev",
        ".git",
        ".env",
        "wp-admin",
        "phpmyadmin",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(sample_words))
    print(f"  [*] Wordlist de muestra creada: {path} ({len(sample_words)} palabras)")


def main():
    target_url = "https://example.com"
    wordlist_path = "./wordlist.txt"

    # Crear un wordlist de muestra si no existe ninguno para probar la herramienta
    if not os.path.exists(wordlist_path):
        create_sample_wordlist(wordlist_path)

    words = read_wordlist(wordlist_path)
    total_requests = len(words) * len(EXTENSIONS)

    print(f"\n{'═' * 60}")
    print("  FUZZING WEB")
    print(f"{'═' * 60}")
    print(f"  Objetivo          : {target_url}")
    print(f"  Wordlist          : {wordlist_path} ({len(words)} palabras)")
    print(f"  Extensiones       : {EXTENSIONS}")
    print(f"  Total peticiones  : {total_requests:,}")
    print(f"  Timeout           : {REQUEST_TIMEOUT}s por petición")
    print(f"  Ignorar códigos   : {IGNORE_CODES}")
    print(f"{'═' * 60}\n")

    results = fuzz_target(target_url, words)
    show_summary(results)


if __name__ == "__main__":
    main()
