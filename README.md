# 🐍 Python Knowledge Base

**Repositorio de aprendizaje de Python**, desde fundamentos del lenguaje hasta su aplicación en herramientas de ciberseguridad ofensiva. Combina apuntes teóricos, ejercicios prácticos y proyectos reales construidos como paquetes Python propios.

---

## 📖 Sobre este repositorio

Este espacio documenta mi progreso aprendiendo Python de forma estructurada: cada sección cubre un bloque temático con teoría en Markdown y código de práctica en carpetas `codigo/`. La última sección (`09-python-ofensivo`) es donde todo ese aprendizaje converge en **herramientas de seguridad ofensiva funcionales**, empaquetadas siguiendo buenas prácticas (estructura `src/`, tests con `pytest`, `pyproject.toml`).

---

## 📂 Estructura del repositorio

| Sección                                                                           | Contenido                                                                                                         |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| [`01-introduccion`](./01-introduccion/01-introduccion.md)                         | Introducción al lenguaje                                                                                          |
| [`02-fundamentos`](./02-fundamentos/01-interprete-y-shebang.md)                   | Intérprete y shebang, variables, operadores, control de flujo, funciones, funciones lambda, manejo de excepciones |
| [`03-estructuras-de-datos`](./03-estructuras-de-datos/01-profundizando-listas.md) | Listas, tuplas, conjuntos, diccionarios + proyecto integrador                                                     |
| [`04-poo`](./04-poo/01-clases-y-objetos.md)                                       | Clases y objetos, herencia y polimorfismo                                                                         |
| [`05-modulos-y-paquetes`](./05-modulos-y-paquetes/01-modulos-y-paquetes.md)       | Módulos, paquetes, creación y distribución de paquetes propios                                                    |
| [`06-input-output`](./06-input-output/01-input-output.md)                         | Entrada/salida, manejo de ficheros, formateo de cadenas                                                           |
| [`07-biblioteca-estandar`](./07-biblioteca-estandar/01-manejo-de-fechas.md)       | Fechas, expresiones regulares, sockets (TCP/UDP/avanzados)                                                        |
| [`08-librerias-estandar`](./08-librerias-estandar/01-sistema.md)                  | Módulos de sistema, `requests`, `urllib3`, `threading`/`multiprocessing`                                          |
| `09-python-ofensivo`                                                              | 🎯 Aplicación de Python a seguridad ofensiva — ver detalle abajo                                                  |

---

## 🎯 Python Ofensivo — Herramientas construidas

Cada herramienta está empaquetada como un proyecto Python independiente (`pyproject.toml`, estructura `src/`, suite de tests con `pytest`), no como scripts sueltos:

| Herramienta                                                                 | Descripción                                                                                     | Estado       |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ------------ |
| [`port-scanner`](./09-python-ofensivo/01-escaner-de-puertos/port-scanner)   | Escáner de puertos con interfaz CLI y salida enriquecida                                        | 🟢 Funcional |
| [`mac-changer`](./09-python-ofensivo/02-mac-changer/mac-changer)            | Cambio de dirección MAC vía CLI, con validadores y tests                                        | 🟢 Funcional |
| [`network-scanner`](./09-python-ofensivo/03-escaner-de-red/network-scanner) | Descubrimiento de hosts en red local                                                            | 🟢 Funcional |
| [`arp-spoofer`](./09-python-ofensivo/04-envenenador-arp/arp-spoofer)        | Envenenamiento ARP con módulo de escaneo dedicado                                               | 🟢 Funcional |
| DNS/HTTP Sniffer, Keylogger, C2/Backdoors, Forward Shell                    | Próximos temas de estudio: análisis de tráfico, conceptos de post-explotación y comunicación C2 | 🟡 Planeado  |

> Las últimas herramientas de la lista corresponden a temario teórico-práctico en curso (análisis de tráfico, técnicas de post-explotación y comunicación C2 con fines exclusivamente educativos, dentro de un entorno de laboratorio controlado).

---

## 🛠️ Stack

`Python 3.13` · `pytest` · `Rich` · `Typer` · `sockets` · `threading`/`multiprocessing`

---

## 👨‍💻 Autor

**Valentín Francisco Nieto** — Junior Penetration Tester & Backend Developer

[LinkedIn](https://linkedin.com/in/niettovale) · [GitHub](https://github.com/NiettoVale) · [HackTheBox](https://app.hackthebox.com/users/3366501) · [Portfolio](https://www.ntech.studio/)
