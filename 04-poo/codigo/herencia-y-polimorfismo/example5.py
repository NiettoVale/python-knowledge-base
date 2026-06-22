#!/usr/bin/env python3
from abc import ABC, abstractmethod

ANCHO = 60


def titulo(texto):
    print("\n" + "═" * ANCHO)
    print(f" {texto}")
    print("═" * ANCHO)


def subtitulo(texto):
    print(f"\n── {texto} {'─' * (ANCHO - len(texto) - 4)}")


class LoggerMixin:
    """
    Mixin que aporta capacidad de logging a cualquier clase que lo herede.
    No define __init__ propio: está diseñado para combinarse con otras clases.
    Al ser un mixin, no representa una entidad del dominio por sí solo.
    """

    def log(self, nivel, mensaje):
        prefijos = {"info": "[*]", "ok": "[+]", "warn": "[!]", "error": "[-]"}
        prefijo = prefijos.get(nivel, "[?]")
        print(f"  {prefijo} {mensaje}")


class ModuloReconocimiento(LoggerMixin, ABC):
    """
    Superclase abstracta del framework.
    Hereda LoggerMixin para que todos los módulos dispongan de self.log().
    Declara ejecutar() y generar_reporte() como abstractos: ninguna subclase
    puede instanciarse sin haber implementado ambos métodos.
    """

    # Atributo de clase: contador global compartido por todos los módulos
    total_modulos_ejecutados = 0

    def __init__(self, objetivo):
        self.objetivo = objetivo
        self.resultados = []

    @abstractmethod
    def ejecutar(self):
        """Lógica específica de reconocimiento de cada módulo."""
        pass

    @abstractmethod
    def generar_reporte(self):
        """Formato de salida específico de cada módulo."""
        pass

    def resumen(self):
        """
        Método concreto heredado por todos los módulos.
        Muestra los resultados acumulados en self.resultados después
        de llamar a ejecutar(). Usa self.__class__.__name__ para mostrar
        el nombre real de la subclase concreta, no de la superclase.
        """
        print(f"\n  Módulo : {self.__class__.__name__}")
        print(f"  Objetivo: {self.objetivo}")
        if self.resultados:
            for hallazgo in self.resultados:
                print(f"    -> {hallazgo}")
        else:
            print("    -> Sin resultados")

    @classmethod
    def incrementar_contador(cls):
        """
        Método de clase: actualiza el atributo de clase compartido.
        Se accede explícitamente a ModuloReconocimiento para garantizar que el
        contador siempre viva en la superclase, independientemente de la
        subclase concreta que lo invoque.
        """
        ModuloReconocimiento.total_modulos_ejecutados += 1


class EscanerPuertos(ModuloReconocimiento):
    """
    Módulo de escaneo de puertos TCP.
    Hereda __init__, resumen() y log() de la superclase y el mixin.
    Implementa ejecutar() y generar_reporte() con lógica propia.
    """

    PUERTOS_CRITICOS = {21: "ftp", 22: "ssh", 23: "telnet", 445: "smb", 3389: "rdp"}

    def __init__(self, objetivo, puertos=None):
        # super() delega la inicialización de 'objetivo' y 'resultados' a la superclase
        super().__init__(objetivo)
        # Se añade un atributo propio que ModuloReconocimiento no tiene
        self.puertos = puertos or [21, 22, 23, 80, 443, 445, 3389]

    def ejecutar(self):
        self.log("info", f"Iniciando escaneo de puertos en {self.objetivo}")
        puertos_simulados_abiertos = [22, 80, 445]
        for puerto in self.puertos:
            if puerto in puertos_simulados_abiertos:
                servicio = self.PUERTOS_CRITICOS.get(puerto, "desconocido")
                criticidad = "CRÍTICO" if puerto in self.PUERTOS_CRITICOS else "estándar"
                hallazgo = f"Puerto {puerto}/{servicio} abierto [{criticidad}]"
                self.resultados.append(hallazgo)
                self.log("warn" if criticidad == "CRÍTICO" else "ok", hallazgo)
        self.incrementar_contador()

    def generar_reporte(self):
        self.log("ok", f"Reporte de puertos: {len(self.resultados)} hallazgo(s) registrado(s)")


class EnumeradorDNS(ModuloReconocimiento):
    """
    Módulo de enumeración de subdominios.
    Sobreescribe ejecutar() y generar_reporte() con lógica completamente distinta
    a la de EscanerPuertos, pero comparte la misma interfaz.
    """

    def __init__(self, objetivo, wordlist=None):
        super().__init__(objetivo)
        self.wordlist = wordlist or ["www", "admin", "vpn", "mail", "dev"]

    def ejecutar(self):
        self.log("info", f"Enumerando subdominios de {self.objetivo}")
        subdominios_resueltos = {"admin", "vpn"}
        for subdominio in self.wordlist:
            fqdn = f"{subdominio}.{self.objetivo}"
            if subdominio in subdominios_resueltos:
                self.resultados.append(f"{fqdn} -> RESUELTO")
                self.log("ok", f"{fqdn} resuelto")
            else:
                self.log("info", f"{fqdn} no resuelto")
        self.incrementar_contador()

    def generar_reporte(self):
        self.log("ok", f"Reporte DNS: {len(self.resultados)} subdominio(s) activo(s)")


class DetectorTecnologias(ModuloReconocimiento):
    """
    Módulo de fingerprinting de tecnologías web.
    Hereda todo el comportamiento base e implementa su propia variante
    de ejecutar() y generar_reporte().
    """

    def ejecutar(self):
        self.log("info", f"Analizando stack tecnológico de {self.objetivo}")
        tecnologias_simuladas = [
            ("WordPress", "6.4.2", "ALTA", "CVE-2024-1234 disponible"),
            ("PHP", "7.4.3", "MEDIA", "Versión end-of-life"),
            ("nginx", "1.18.0", "BAJA", "Sin vulnerabilidades conocidas"),
        ]
        for nombre, version, riesgo, nota in tecnologias_simuladas:
            hallazgo = f"{nombre} {version} [Riesgo: {riesgo}] — {nota}"
            self.resultados.append(hallazgo)
            nivel_log = "warn" if riesgo in ("ALTA", "MEDIA") else "ok"
            self.log(nivel_log, hallazgo)
        self.incrementar_contador()

    def generar_reporte(self):
        self.log("ok", f"Reporte tecnológico: {len(self.resultados)} tecnología(s) identificada(s)")


class Pipeline:
    """
    Orquestador del framework: ejecuta cualquier lista de módulos de forma
    polimórfica, sin conocer ni verificar el tipo concreto de cada uno.
    Solo necesita saber que todos heredan de ModuloReconocimiento y, por lo
    tanto, responden a ejecutar(), generar_reporte() y resumen().
    """

    def __init__(self, nombre_engagement):
        self.nombre_engagement = nombre_engagement
        self.modulos = []

    def agregar_modulo(self, modulo):
        # Validación defensiva: garantiza que solo ingresen módulos del framework
        if not isinstance(modulo, ModuloReconocimiento):
            raise TypeError(f"'{type(modulo).__name__}' no es un módulo válido del framework")
        self.modulos.append(modulo)

    def ejecutar_todos(self):
        titulo(f"ENGAGEMENT: {self.nombre_engagement}")
        print(f"  Módulos cargados : {len(self.modulos)}")
        print(f"  Objetivos únicos : {len({m.objetivo for m in self.modulos})}")

        for modulo in self.modulos:
            # Polimorfismo: la llamada a ejecutar() y generar_reporte() resuelve
            # en tiempo de ejecución la versión correcta según el tipo real del objeto.
            # Este bucle funcionará sin cambios si se agrega un nuevo módulo mañana.
            subtitulo(modulo.__class__.__name__)
            modulo.ejecutar()
            modulo.generar_reporte()
            modulo.resumen()

    def estadisticas_finales(self):
        titulo("ESTADÍSTICAS DEL ENGAGEMENT")
        total_hallazgos = sum(len(m.resultados) for m in self.modulos)
        print(f"  Módulos ejecutados   : {ModuloReconocimiento.total_modulos_ejecutados}")
        print(f"  Total de hallazgos   : {total_hallazgos}")
        for modulo in self.modulos:
            print(f"  {modulo.__class__.__name__:<25} {len(modulo.resultados)} hallazgo(s) sobre {modulo.objetivo}")


# ---------------------------------------------------------------------------
# Verificaciones de herencia (isinstance / issubclass)
# ---------------------------------------------------------------------------

def verificar_jerarquia():
    titulo("VERIFICACIÓN DE JERARQUÍA")

    escaner = EscanerPuertos("192.168.1.10")
    dns = EnumeradorDNS("empresa.com")

    subtitulo("isinstance()")
    print(f"  escaner es EscanerPuertos      : {isinstance(escaner, EscanerPuertos)}")
    print(f"  escaner es ModuloReconocimiento : {isinstance(escaner, ModuloReconocimiento)}")
    print(f"  escaner es EnumeradorDNS        : {isinstance(escaner, EnumeradorDNS)}")
    print(f"  dns     es ModuloReconocimiento : {isinstance(dns, ModuloReconocimiento)}")

    subtitulo("issubclass()")
    print(f"  EscanerPuertos  < ModuloReconocimiento : {issubclass(EscanerPuertos, ModuloReconocimiento)}")
    print(f"  EnumeradorDNS   < ModuloReconocimiento : {issubclass(EnumeradorDNS, ModuloReconocimiento)}")
    print(f"  ModuloReconocimiento < ABC             : {issubclass(ModuloReconocimiento, ABC)}")

    subtitulo("MRO de EscanerPuertos")
    for i, clase in enumerate(EscanerPuertos.__mro__):
        print(f"  {i}: {clase}")

    subtitulo("Intento de instanciar clase abstracta (capturado)")
    try:
        ModuloReconocimiento("192.168.1.1")
    except TypeError as error:
        print(f"  Error esperado: {error}")


if __name__ == "__main__":

    # 1. Verificar jerarquía de clases antes de ejecutar el pipeline
    verificar_jerarquia()

    # 2. Construir el pipeline del engagement
    pipeline = Pipeline("Empresa S.A. — Q2 2026")

    pipeline.agregar_modulo(EscanerPuertos("192.168.1.10"))
    pipeline.agregar_modulo(EscanerPuertos("192.168.1.11", puertos=[22, 80, 443]))
    pipeline.agregar_modulo(EnumeradorDNS("empresa.com"))
    pipeline.agregar_modulo(DetectorTecnologias("http://empresa.com"))

    # 3. Ejecutar todos los módulos de forma polimórfica
    pipeline.ejecutar_todos()

    # 4. Mostrar estadísticas consolidadas del engagement
    pipeline.estadisticas_finales()

    # 5. Validación de tipo incorrecto al agregar un módulo inválido
    titulo("INTENTO DE MÓDULO INVÁLIDO")
    try:
        pipeline.agregar_modulo("no soy un módulo")
    except TypeError as error:
        print(f"  Error capturado: {error}")