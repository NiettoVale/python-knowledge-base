#!/usr/bin/env python3
from abc import ABC, abstractmethod

TARGET = "192.168.1.10"

class Scanner(ABC):
    def __init__(self, nombre):
        self.nombre = nombre
        
    @abstractmethod
    def scan(self, target):
        pass
    # def scan(self, target):
    #     raise NotImplementedError("Debes implementar scan()")
    
class PortScanner(Scanner):
    def scan(self, target):
        return f'Puertos abiertos en {target}: 22, 80, 443'

class WebScanner(Scanner):
    def scan(self, target):
        return f'Vulnerabilidades encontradas en {target}: XSS, SQL Injection'

class MalwareScanner(Scanner):
    def scan(self, target):
        return f'Análisis de {target}: No se detectó malware'

class FirewallScanner(Scanner):
    def scan(self, target):
        return f'Ejecutando las reglas de firewall sobre {target}'

def ejecutar_scan(scanner, target):
    print(scanner.scan(target))

scanners = [
    PortScanner('Port Scanner'),
    WebScanner('Web Scanner'),
    MalwareScanner('Malware Scanner'),
    FirewallScanner('Firewall Scanner'),
    Scanner('Scanner')
]

for scanner in scanners:
    ejecutar_scan(scanner, TARGET)


