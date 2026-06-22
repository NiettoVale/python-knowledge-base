# Herencia y Polimorfismo en Python

## Introducción

La herencia y el polimorfismo son dos de los pilares más importantes de la Programación Orientada a Objetos, y su comprensión resulta fundamental para diseñar sistemas que sean fácilmente extensibles, mantenibles y libres de duplicación de código. Mientras que las clases, los atributos y los métodos vistos hasta ahora permiten modelar entidades individuales con sus propias características y comportamientos, la herencia y el polimorfismo aportan la capacidad de organizar esas entidades en jerarquías relacionadas, de modo que las similitudes entre clases se expresen explícitamente en el código, en lugar de repetirse de forma redundante en cada una de ellas.

## Herencia

La herencia es el mecanismo mediante el cual una clase (denominada **subclase**, **clase hija** o **clase derivada**) adquiere automáticamente todos los atributos y métodos de otra clase (denominada **superclase**, **clase padre** o **clase base**), con la posibilidad de extender su comportamiento con nuevos atributos o métodos propios, o de modificar el comportamiento heredado cuando sea necesario. En Python, la herencia se declara colocando el nombre de la superclase entre paréntesis en la línea de definición de la subclase.

La principal razón de existir de la herencia es la **reutilización de código**: en lugar de duplicar la lógica común en múltiples clases que comparten características, dicha lógica se define una única vez en la superclase, y todas las subclases la heredan y se benefician de ella automáticamente. Si más adelante se detecta un error o se decide mejorar esa lógica común, basta con modificarla en un único lugar (la superclase), y el cambio se propagará automáticamente a todas las subclases que la heredan.

```python
class Herramienta:
    """Superclase base: representa cualquier herramienta de seguridad."""

    def __init__(self, nombre, version):
        self.nombre = nombre
        self.version = version

    def info(self):
        return f"[{self.nombre} v{self.version}]"

    def ejecutar(self):
        print(f"{self.info()} ejecutándose en modo genérico...")


# Escaner hereda de Herramienta: adquiere __init__(), info() y ejecutar()
class Escaner(Herramienta):
    def __init__(self, nombre, version, objetivo):
        # super() permite invocar el constructor de la superclase desde la subclase,
        # evitando duplicar la lógica de inicialización de 'nombre' y 'version'.
        super().__init__(nombre, version)
        self.objetivo = objetivo   # atributo propio de Escaner, que Herramienta no tiene

    def ejecutar(self):
        # Sobreescritura (override): reemplaza el comportamiento heredado con uno específico
        print(f"{self.info()} escaneando objetivo: {self.objetivo}")


escaner = Escaner("NmapWrapper", "1.3", "192.168.1.0/24")
escaner.ejecutar()   # NmapWrapper v1.3 escaneando objetivo: 192.168.1.0/24
print(escaner.info())   # info() se usa sin redefinirla: viene heredada de Herramienta
```

### La Función `super()`

`super()` es una función incorporada de Python que devuelve una referencia a la superclase inmediata de la clase actual, permitiendo invocar sus métodos desde dentro de la subclase. Su uso más habitual es en el constructor (`__init__`) de la subclase, para delegar en la superclase la inicialización de los atributos comunes, evitando copiar y pegar esa lógica. Sin embargo, `super()` no se limita al constructor: puede usarse en cualquier método de la subclase para invocar la versión de ese mismo método definida en la superclase, lo que resulta especialmente útil cuando se desea extender un comportamiento heredado en lugar de reemplazarlo por completo.

```python
class Herramienta:
    def ejecutar(self):
        print("Iniciando componentes base...")

class Exploit(Herramienta):
    def ejecutar(self):
        super().ejecutar()   # primero ejecuta el comportamiento de la superclase
        print("Lanzando payload específico del exploit...")

exploit = Exploit()
exploit.ejecutar()
# Iniciando componentes base...
# Lanzando payload específico del exploit...
```

### Herencia Múltiple

Python admite la herencia múltiple: una clase puede heredar de más de una superclase simultáneamente, adquiriendo los atributos y métodos de todas ellas. Esto resulta útil cuando una entidad combina características de varios conceptos independientes entre sí, como un módulo que es al mismo tiempo un escáner y un generador de reportes.

```python
class Registrador:
    """Agrega capacidades de logging a cualquier clase que la herede."""

    def log(self, mensaje):
        print(f"[LOG] {mensaje}")


class Reportador:
    """Agrega capacidades de generación de reportes."""

    def generar_reporte(self, datos):
        print(f"[REPORTE] {datos}")


# EscanerCompleto hereda de ambas clases: adquiere log() y generar_reporte()
class EscanerCompleto(Registrador, Reportador):
    def ejecutar(self, objetivo):
        self.log(f"Iniciando escaneo de {objetivo}")
        resultado = f"3 puertos abiertos en {objetivo}"
        self.generar_reporte(resultado)
        self.log("Escaneo finalizado")


modulo = EscanerCompleto()
modulo.ejecutar("192.168.1.10")
```

Al trabajar con herencia múltiple conviene conocer el concepto de **MRO** (_Method Resolution Order_): el orden en que Python busca un método a través de la jerarquía de clases cuando este no se encuentra en la clase actual. Python sigue el algoritmo C3 (_linearización C3_) para determinar este orden, y puede consultarse mediante el atributo `.__mro__` de cualquier clase.

```python
print(EscanerCompleto.__mro__)
# (<class 'EscanerCompleto'>, <class 'Registrador'>, <class 'Reportador'>, <class 'object'>)
```

Obsérvese que `object` aparece siempre al final: en Python 3, todas las clases heredan implícitamente de `object`, la raíz de la jerarquía de clases del lenguaje, que proporciona una serie de métodos por defecto como `__str__`, `__repr__` y `__eq__` (los mismos que se vieron en notas anteriores sobre métodos especiales o _dunders_).

### Sobreescritura de Métodos (_Method Overriding_)

La sobreescritura, u _override_, es la capacidad de una subclase de redefinir un método heredado de la superclase, proporcionando una implementación propia específica para esa subclase. Cuando se invoca el método sobre un objeto de la subclase, Python utiliza la versión redefinida en lugar de la versión original heredada. Esto es lo que hace que la herencia sea verdaderamente potente: permite que las subclases partan de un comportamiento base común y luego lo especialicen según sus propias necesidades, sin afectar al resto de la jerarquía.

```python
class Herramienta:
    def ejecutar(self):
        print("Ejecutando herramienta genérica...")


class Escaner(Herramienta):
    def ejecutar(self):
        print("Ejecutando escaneo de puertos...")


class FuerzaBruta(Herramienta):
    def ejecutar(self):
        print("Ejecutando ataque de fuerza bruta...")


class AnalizadorSSL(Herramienta):
    pass   # No redefine ejecutar(): hereda directamente el comportamiento de la superclase


escaner = Escaner()
fuerza_bruta = FuerzaBruta()
analizador = AnalizadorSSL()

escaner.ejecutar()      # Ejecutando escaneo de puertos...
fuerza_bruta.ejecutar() # Ejecutando ataque de fuerza bruta...
analizador.ejecutar()   # Ejecutando herramienta genérica...  <- hereda la versión de Herramienta
```

### Verificación de Herencia: `isinstance()` e `issubclass()`

Python proporciona dos funciones incorporadas especialmente útiles para razonar sobre la jerarquía de herencia de los objetos en tiempo de ejecución. `isinstance(objeto, clase)` verifica si un objeto es una instancia de una clase determinada o de cualquiera de sus subclases, lo cual resulta más robusto que comparar directamente el tipo mediante `type()`. `issubclass(subclase, superclase)` verifica si una clase es subclase de otra, operando a nivel de clases en lugar de objetos.

```python
escaner = Escaner()

print(isinstance(escaner, Escaner))       # True  <- es directamente un Escaner
print(isinstance(escaner, Herramienta))   # True  <- Escaner hereda de Herramienta
print(isinstance(escaner, FuerzaBruta))   # False <- no hay relación de herencia

print(issubclass(Escaner, Herramienta))   # True
print(issubclass(Herramienta, object))    # True  <- toda clase hereda de object
```

Preferir `isinstance()` sobre `type(objeto) == Clase` es una buena práctica precisamente porque `isinstance()` respeta la jerarquía de herencia: una instancia de `Escaner` devolverá `True` al consultarse contra `Herramienta`, reflejando correctamente la relación de herencia, mientras que `type(escaner) == Herramienta` devolvería `False`, perdiendo esa información.

## Polimorfismo

El polimorfismo —del griego _polys_ (muchos) y _morphē_ (formas)— es la capacidad de objetos de diferentes clases de responder a una misma interfaz (es decir, a un mismo nombre de método o función) produciendo comportamientos distintos y específicos de cada clase. En términos prácticos, el polimorfismo permite escribir código que opera sobre objetos sin necesidad de conocer su tipo concreto en tiempo de escritura, confiando en que, sea cual sea el tipo real del objeto, este sabrá cómo responder apropiadamente cuando se le invoque un determinado método.

```python
class Herramienta:
    def ejecutar(self):
        raise NotImplementedError("La subclase debe implementar ejecutar()")


class Escaner(Herramienta):
    def ejecutar(self):
        print("Escaneando red...")


class ExplotadorVulnerabilidades(Herramienta):
    def ejecutar(self):
        print("Probando exploits conocidos...")


class GeneradorReporte(Herramienta):
    def ejecutar(self):
        print("Generando reporte en formato PDF...")


# Una función que trabaja polimórficamente: no le importa qué tipo específico
# de Herramienta recibe, solo necesita saber que todas responden a ejecutar()
def lanzar_herramienta(herramienta):
    herramienta.ejecutar()

pipeline = [Escaner(), ExplotadorVulnerabilidades(), GeneradorReporte()]

for herramienta in pipeline:
    lanzar_herramienta(herramienta)
```

Este ejemplo ilustra con precisión la esencia del polimorfismo: la función `lanzar_herramienta()` no necesita conocer ni verificar si su argumento es un `Escaner`, un `ExplotadorVulnerabilidades` o un `GeneradorReporte`, ni hacer nada diferente en cada caso. Le basta con saber que el objeto recibido responde al método `ejecutar()`, y Python se encarga en tiempo de ejecución de invocar la versión correcta según el tipo real del objeto. Este principio también se denomina **despacho dinámico** (_dynamic dispatch_): la asociación entre la llamada al método y la implementación concreta que se ejecutará se resuelve dinámicamente durante la ejecución, no estáticamente en tiempo de escritura del código.

### El Uso de `NotImplementedError` para Definir Interfaces

El uso de `raise NotImplementedError` dentro de un método de la superclase, como se vio en el ejemplo anterior, es una convención muy habitual en Python para señalar que ese método es parte de una **interfaz esperada**: define qué métodos deben implementar todas las subclases, y fuerza un error claro y descriptivo en tiempo de ejecución si alguna subclase se olvida de hacerlo, en lugar de producir un comportamiento silenciosamente incorrecto.

```python
class Herramienta:
    def ejecutar(self):
        raise NotImplementedError("Toda subclase de Herramienta debe implementar ejecutar()")

class HerramientaIncompleta(Herramienta):
    pass   # Olvidó implementar ejecutar()

herramienta = HerramientaIncompleta()
try:
    herramienta.ejecutar()
except NotImplementedError as error:
    print(f"Error de diseño detectado: {error}")
```

### Clases Base Abstractas: el Módulo `abc`

Una forma más formal y robusta de definir interfaces en Python es utilizar el módulo `abc` (_Abstract Base Classes_) de la biblioteca estándar. Las clases base abstractas permiten declarar explícitamente qué métodos son abstractos, es decir, qué métodos deben ser implementados obligatoriamente por cualquier subclase, bloqueando incluso la creación de instancias de la superclase abstracta o de cualquier subclase que no haya implementado la totalidad de los métodos abstractos declarados. Esta verificación ocurre ya en el momento de la instanciación, en lugar de esperar a que el método abstracto sea invocado.

```python
from abc import ABC, abstractmethod

class Herramienta(ABC):   # Herramienta ya no puede instanciarse directamente
    def __init__(self, nombre):
        self.nombre = nombre

    @abstractmethod
    def ejecutar(self):
        """Todas las subclases DEBEN implementar este método."""
        pass

    @abstractmethod
    def generar_reporte(self):
        """Todas las subclases DEBEN implementar este método."""
        pass

    def info(self):
        # Un método no abstracto puede coexistir con los abstractos
        return f"Herramienta: {self.nombre}"


class Escaner(Herramienta):
    def ejecutar(self):
        print(f"Escaneando con {self.nombre}...")

    def generar_reporte(self):
        print(f"Reporte del escaneo de {self.nombre} generado.")


# Herramienta() -> TypeError: no se puede instanciar una clase abstracta
try:
    h = Herramienta("base")
except TypeError as error:
    print(f"Error: {error}")

# Escaner() -> funciona: implementó todos los métodos abstractos
escaner = Escaner("NmapWrapper")
escaner.ejecutar()
escaner.generar_reporte()
print(escaner.info())
```

La diferencia entre usar `raise NotImplementedError` y definir métodos con `@abstractmethod` es que el primero es una convención informal que solo produce el error cuando el método se invoca en tiempo de ejecución, mientras que el segundo es una verificación formal del lenguaje que impide directamente la creación de instancias si algún método abstracto no fue implementado, detectando el problema de diseño de forma más temprana y más explícita.

### Polimorfismo con Funciones Incorporadas

El polimorfismo en Python no se limita a los métodos definidos por el programador: las propias funciones incorporadas del lenguaje, como `len()`, `str()` o el operador `+`, son ejemplos de polimorfismo. `len()`, por ejemplo, funciona con cadenas, listas, tuplas, diccionarios y conjuntos porque cada uno de esos tipos define el método especial `__len__`, y `len()` simplemente lo invoca sin necesitar saber qué tipo concreto de objeto está recibiendo.

```python
print(len("192.168.1.10"))   # 12  <- invoca str.__len__()
print(len([22, 80, 443]))    # 3   <- invoca list.__len__()
print(len({21: "ftp", 22: "ssh"}))   # 2   <- invoca dict.__len__()
```

En este sentido, al definir métodos especiales como `__str__`, `__len__`, `__eq__` o `__add__` en las propias clases (los _dunders_ vistos en notas anteriores), se está participando directamente en el sistema de polimorfismo del lenguaje, permitiendo que los objetos de dichas clases se comporten de forma coherente con las funciones incorporadas.

## Herencia y Polimorfismo Combinados: un Ejemplo Integrador

Para ilustrar cómo herencia y polimorfismo trabajan en conjunto en un escenario realista de ciberseguridad, consideremos un pipeline de módulos de reconocimiento donde cada módulo hereda comportamiento base y lo especializa, pero todos pueden ejecutarse de forma polimórfica desde el mismo punto de entrada.

```python
from abc import ABC, abstractmethod

class ModuloReconocimiento(ABC):
    def __init__(self, objetivo):
        self.objetivo = objetivo
        self.resultados = []

    @abstractmethod
    def ejecutar(self):
        pass

    def resumen(self):
        print(f"\n[{self.__class__.__name__}] Objetivo: {self.objetivo}")
        for resultado in self.resultados:
            print(f"  -> {resultado}")


class EscanerPuertos(ModuloReconocimiento):
    def ejecutar(self):
        self.resultados = ["Puerto 22 abierto (ssh)", "Puerto 443 abierto (https)"]


class EnumeradorDNS(ModuloReconocimiento):
    def ejecutar(self):
        self.resultados = ["admin.empresa.com", "vpn.empresa.com"]


class DetectorCMS(ModuloReconocimiento):
    def ejecutar(self):
        self.resultados = ["WordPress 6.1 detectado", "Plugin WooCommerce activo"]


# El pipeline trabaja polimórficamente: no le importa qué módulo concreto recibe
def ejecutar_pipeline(modulos):
    for modulo in modulos:
        modulo.ejecutar()   # cada uno ejecuta su propia versión de ejecutar()
        modulo.resumen()    # resumen() es heredado de ModuloReconocimiento, idéntico para todos


pipeline = [
    EscanerPuertos("192.168.1.10"),
    EnumeradorDNS("empresa.com"),
    DetectorCMS("http://empresa.com"),
]

ejecutar_pipeline(pipeline)
```

En este diseño, `ejecutar_pipeline()` no contiene ni un solo `if`/`elif` para distinguir entre tipos de módulos: simplemente recorre la lista e invoca `ejecutar()` y `resumen()` sobre cada elemento. Si en el futuro se agrega un nuevo módulo (por ejemplo, un `AnalizadorSSL`), basta con definir una nueva clase que herede de `ModuloReconocimiento` e implemente `ejecutar()`, sin necesidad de modificar `ejecutar_pipeline()` ni ninguna otra parte del código existente. Esta capacidad de extender el sistema sin modificar el código ya escrito es precisamente lo que se conoce como el **Principio Abierto/Cerrado** (_Open/Closed Principle_), uno de los principios SOLID del diseño orientado a objetos: las clases deben estar abiertas a la extensión pero cerradas a la modificación.

## Buenas Prácticas

La herencia debe usarse cuando existe una relación genuina de tipo "es un/a" (_is-a_) entre la subclase y la superclase: un `Escaner` _es una_ `Herramienta`, por lo que la herencia tiene sentido. Si la relación entre dos clases es más bien de tipo "tiene un/a" (_has-a_), como un `Reporte` que _tiene una_ lista de `Hallazgos`, la composición (almacenar objetos de una clase como atributos de otra) resulta generalmente más apropiada que la herencia, ya que produce un acoplamiento más débil y un diseño más flexible.

Respecto al polimorfismo, conviene apoyarse en clases base abstractas con `@abstractmethod` cuando se diseñan jerarquías de clases que deben garantizar la implementación de una interfaz, ya que su verificación en tiempo de instanciación detecta errores de diseño de forma más temprana y más explícita que las convenciones informales basadas en `NotImplementedError`. Finalmente, conviene usar `isinstance()` en lugar de `type() ==` al verificar el tipo de un objeto, y hacerlo con moderación: la necesidad frecuente de verificar el tipo de un objeto en tiempo de ejecución suele ser una señal de que el diseño podría aprovechar mejor el polimorfismo, permitiendo que cada objeto "sepa" cómo comportarse en lugar de que el código exterior deba decidirlo caso por caso.