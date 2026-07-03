#!/usr/bin/env python3
import os


def def_handler(sig, frame):
    print("\n[!] Saliendo del programa...\n")
    os._exit(1)
