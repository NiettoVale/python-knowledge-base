# Control de Flujo en Python: Condicionales y Bucles

## Condicionales

Los condicionales son estructuras de control que permiten ejecutar distintos bloques de código en función de si una o varias condiciones se evalúan como verdaderas o falsas. En Python, las declaraciones condicionales fundamentales son `if`, `elif` y `else`, y su combinación permite construir lógicas de decisión tan simples o complejas como el problema lo requiera.

La declaración `if` evalúa una condición y, únicamente si esta resulta verdadera, ejecuta el bloque de código asociado. La declaración `elif`, abreviatura de _"else if"_, permite encadenar evaluaciones adicionales que solo se comprueban si la condición del `if` (o de un `elif` anterior) resultó falsa, lo cual posibilita verificar múltiples escenarios de forma secuencial sin necesidad de anidar múltiples bloques `if` independientes. Finalmente, la declaración `else` actúa como bloque de captura general, ejecutándose únicamente cuando ninguna de las condiciones anteriores se cumplió.

```python
# Clasificación de un puerto según su nivel de criticidad
puerto = 23

if puerto in (21, 23):
    print(f"Puerto {puerto}: protocolo inseguro, considerar como hallazgo crítico")
elif puerto in (80, 443):
    print(f"Puerto {puerto}: servicio web, evaluar configuración SSL/TLS")
else:
    print(f"Puerto {puerto}: requiere análisis adicional")
```

### Operadores Lógicos

Los operadores lógicos permiten combinar varias condiciones dentro de una misma evaluación, lo cual resulta indispensable a la hora de construir lógicas de decisión más expresivas. Python ofrece tres operadores lógicos: `and`, `or` y `not`.

El operador `and` devuelve verdadero únicamente cuando todas las condiciones evaluadas son verdaderas; basta con que una sola condición sea falsa para que el resultado completo sea falso. El operador `or` devuelve verdadero si al menos una de las condiciones evaluadas lo es, y solo resulta falso cuando todas las condiciones involucradas son falsas. El operador `not` invierte el valor lógico de una condición, transformando verdadero en falso y viceversa.

```python
# Combinación de condiciones con operadores lógicos
puerto_abierto = True
servicio_identificado = "ssh"
version_vulnerable = True

if puerto_abierto and servicio_identificado == "ssh" and version_vulnerable:
    print("[!] Posible vector de ataque: SSH con versión vulnerable detectada")

if servicio_identificado == "ftp" or servicio_identificado == "telnet":
    print("[!] Protocolo de transmisión en texto plano detectado")

if not puerto_abierto:
    print("El puerto se encuentra cerrado o filtrado")
```

### Operadores de Comprobación

Además de los operadores de comparación tradicionales (`'=='`, `!=`, `<`, `>`, `<=`, `>=`), Python ofrece dos categorías adicionales de operadores especialmente útiles dentro de estructuras condicionales: los operadores de **pertenencia** y los operadores de **identidad**.

Los operadores de pertenencia, `in` y `not in`, permiten comprobar si un valor se encuentra (o no) dentro de una secuencia, como una lista, una cadena o un diccionario, sin necesidad de recorrerla manualmente.

```python
# Operadores de pertenencia: comprobar si un puerto está en una lista de puertos críticos
puertos_criticos = [21, 23, 445, 3389]
puerto_actual = 445

if puerto_actual in puertos_criticos:
    print(f"Puerto {puerto_actual} clasificado como crítico")

if "admin" not in "usuario_invitado":
    print("La cadena no contiene la palabra 'admin'")
```

Los operadores de identidad, `is` e `is not`, comprueban si dos variables hacen referencia exactamente al mismo objeto en memoria, lo cual es distinto de comprobar si dos valores son simplemente iguales. Su uso más habitual y recomendado en Python es para comparar contra `None`, el valor especial que representa la ausencia de dato.

```python
# Operador de identidad: comprobación recomendada contra None
resultado_escaneo = None

if resultado_escaneo is None:
    print("El escaneo aún no produjo resultados")
```

### Operador Ternario

El operador ternario, también conocido como expresión condicional, permite escribir una estructura `if`/`else` simple en una única línea, devolviendo uno de dos valores posibles en función de si una condición se cumple o no. Resulta especialmente útil cuando se necesita asignar un valor de forma condicional sin justificar la escritura de un bloque `if`/`else` completo.

Su sintaxis general es `valor_si_verdadero if condicion else valor_si_falso`.

```python
# Operador ternario: clasificar el estado de un host en una sola línea
tiempo_respuesta = 0.05

estado = "activo" if tiempo_respuesta < 1.0 else "sin respuesta"
print(f"Estado del host: {estado}")

# Equivalente utilizando un bloque if/else tradicional
if tiempo_respuesta < 1.0:
    estado = "activo"
else:
    estado = "sin respuesta"
```

### Condicionales Anidados

Es posible colocar una estructura condicional dentro de otra, dando lugar a condicionales anidados. Esta técnica resulta útil cuando una decisión depende, a su vez, de otra decisión previa, aunque conviene utilizarla con moderación, ya que un anidamiento excesivo tiende a reducir la legibilidad del código y, en muchos casos, puede simplificarse combinando las condiciones con operadores lógicos.

```python
# Condicionales anidados: análisis de un host según su estado y servicios
host_activo = True
puerto_80_abierto = True

if host_activo:
    print("El host respondió al escaneo")
    if puerto_80_abierto:
        print("  -> Servicio web detectado en el puerto 80")
    else:
        print("  -> No se detectaron servicios web")
else:
    print("El host no respondió al escaneo")
```

## Bucles

Los bucles permiten ejecutar un bloque de código de forma repetida, ya sea mientras se cumpla una determinada condición, o una vez por cada elemento de una secuencia. Python ofrece dos tipos principales de bucles: `for` y `while`.

El bucle `for` se utiliza para iterar sobre una secuencia, como una lista, una cadena, un diccionario, una tupla o un conjunto, ejecutando el bloque de código asociado una vez por cada elemento de dicha secuencia. El bucle `while`, en cambio, ejecuta el bloque de código de forma repetida mientras una condición específica continúe evaluándose como verdadera, sin estar necesariamente vinculado a una secuencia predefinida.

```python
# Bucle for: recorrer una lista de puertos a escanear
puertos = [22, 80, 443]

for puerto in puertos:
    print(f"Escaneando puerto {puerto}...")
```

```python
# Bucle while: reintentar una conexión hasta lograr una respuesta o agotar los intentos
intentos = 0
maximo_intentos = 5
conexion_exitosa = False

while intentos < maximo_intentos and not conexion_exitosa:
    intentos += 1
    print(f"Intento {intentos} de conexión...")
    # Aquí iría la lógica real de conexión, que eventualmente
    # actualizaría la variable conexion_exitosa
```

El bucle `while` resulta especialmente adecuado en escenarios donde no se conoce de antemano cuántas iteraciones serán necesarias, como ocurre al esperar una respuesta de red, monitorizar un proceso en ejecución o reintentar una operación hasta que esta tenga éxito o se agote un número máximo de intentos.

### Bucles Anidados

Al igual que ocurre con los condicionales, es posible colocar un bucle dentro de otro, dando lugar a bucles anidados. Esta estructura resulta indispensable cuando se necesita combinar dos secuencias entre sí, como ocurre, por ejemplo, al recorrer una lista de hosts y, para cada uno de ellos, recorrer a su vez una lista de puertos a verificar.

```python
# Bucles anidados: escanear varios puertos en varios hosts
hosts = ["192.168.1.10", "192.168.1.11"]
puertos = [22, 80, 443]

for host in hosts:
    print(f"Analizando host: {host}")
    for puerto in puertos:
        print(f"  -> Verificando puerto {puerto}")
```

Es importante tener en cuenta que el costo computacional de los bucles anidados crece de forma proporcional al producto de la longitud de cada secuencia involucrada, por lo que su uso debe evaluarse con cuidado cuando se trabaja con conjuntos de datos de gran tamaño, como ocurre habitualmente en escaneos de redes extensas o en ataques de fuerza bruta con diccionarios voluminosos.

## Declaraciones de Control de Flujo en Bucles

Existen tres declaraciones especiales que permiten modificar el comportamiento estándar de un bucle desde dentro de su propio cuerpo: `break`, `continue` y `pass`.

La declaración `break` finaliza la ejecución del bucle de forma inmediata, sin completar las iteraciones restantes, y transfiere el control del programa a la primera instrucción ubicada inmediatamente después del bucle. Resulta de gran utilidad cuando se ha encontrado lo que se buscaba y continuar iterando ya no aporta ningún valor.

```python
# Uso de break: detener la búsqueda apenas se encuentra un puerto crítico abierto
puertos_a_revisar = [21, 22, 80, 23, 443]
puertos_criticos = [21, 23, 3389]

for puerto in puertos_a_revisar:
    if puerto in puertos_criticos:
        print(f"[!] Puerto crítico {puerto} encontrado, deteniendo el escaneo")
        break
    print(f"Puerto {puerto} verificado, continuando...")
```

La declaración `continue` omite el resto del código restante dentro de la iteración actual y pasa directamente a la siguiente iteración del bucle, sin finalizarlo por completo. Resulta útil cuando se desea ignorar ciertos elementos de la secuencia sin interrumpir el recorrido del resto.

```python
# Uso de continue: omitir puertos ya conocidos como cerrados
puertos = [21, 22, 80, 443, 8080]
puertos_cerrados_conocidos = [21, 8080]

for puerto in puertos:
    if puerto in puertos_cerrados_conocidos:
        continue
    print(f"Analizando puerto {puerto} en detalle...")
```

La declaración `pass` no realiza ninguna acción: se trata de una declaración nula, utilizada como marcador de posición en aquellos lugares donde la sintaxis de Python exige la presencia de un bloque de código, pero dicho bloque todavía no ha sido implementado. Es habitual encontrarla durante las primeras etapas de desarrollo de un script, como recordatorio de una sección pendiente de completar.

```python
# Uso de pass: estructura pendiente de implementación
for puerto in [22, 80, 443]:
    if puerto == 443:
        pass   # TODO: implementar lógica específica para analizar HTTPS
    else:
        print(f"Puerto {puerto} sin tratamiento especial todavía")
```

### La Cláusula `else` en Bucles

Una característica del lenguaje frecuentemente desconocida, incluso entre programadores con cierta experiencia, es que tanto el bucle `for` como el bucle `while` admiten una cláusula `else` propia. A diferencia del `else` asociado a un `if`, el `else` de un bucle no evalúa una condición booleana adicional, sino que se ejecuta automáticamente cuando el bucle finaliza todas sus iteraciones de forma normal, es decir, sin haber sido interrumpido mediante una declaración `break`.

Este comportamiento convierte al `else` de los bucles en una herramienta muy precisa para distinguir entre dos escenarios distintos al finalizar una búsqueda: que el elemento buscado haya sido encontrado (y el bucle se haya interrumpido con `break`), o que se haya recorrido la totalidad de la secuencia sin encontrarlo. Esta distinción resulta extremadamente útil en tareas de ciberseguridad, como verificar si un puerto vulnerable se encuentra entre los detectados, o si una contraseña dentro de un diccionario logró autenticar correctamente.

```python
# Uso de else en un bucle for: distinguir entre "encontrado" y "no encontrado"
puertos_detectados = [22, 80, 443]
puerto_vulnerable = 3389

for puerto in puertos_detectados:
    if puerto == puerto_vulnerable:
        print(f"[!] Puerto vulnerable {puerto} encontrado")
        break
else:
    # Este bloque solo se ejecuta si el bucle terminó SIN haber hecho break,
    # es decir, si se recorrieron todos los puertos sin encontrar el vulnerable
    print("No se encontraron puertos vulnerables conocidos en este host")
```

El mismo principio aplica al bucle `while`: su cláusula `else` se ejecuta únicamente si el bucle finaliza porque su condición pasó a ser falsa de forma natural, y no porque haya sido interrumpido mediante `break`.

```python
# Uso de else en un bucle while
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
    # Se ejecuta si se agotaron los intentos sin haber encontrado una credencial válida
    print("Se agotaron los intentos sin lograr autenticación")
```

## Comprensión de Listas (_List Comprehensions_)

La comprensión de listas es una construcción sintáctica propia de Python que permite generar una nueva lista de forma compacta y declarativa, a partir de una secuencia existente, combinando en una única línea lo que tradicionalmente requeriría un bucle `for` junto con el método `append()`. Se trata de una de las características más distintivas y valoradas del lenguaje, y su dominio resulta fundamental para escribir código verdaderamente idiomático en Python.

Su sintaxis general consiste en colocar, dentro de corchetes, una expresión seguida de una cláusula `for` que recorre una secuencia, y, opcionalmente, una cláusula `if` que filtra los elementos a incluir:

```python
# Forma tradicional: construir una lista con un bucle for y append
puertos_texto = ["22", "80", "443"]
puertos_enteros = []

for p in puertos_texto:
    puertos_enteros.append(int(p))

print(puertos_enteros)   # [22, 80, 443]
```

```python
# Misma operación utilizando comprensión de listas
puertos_texto = ["22", "80", "443"]
puertos_enteros = [int(p) for p in puertos_texto]

print(puertos_enteros)   # [22, 80, 443]
```

La comprensión de listas también admite una cláusula condicional al final, que permite filtrar únicamente aquellos elementos que cumplan una determinada condición, sustituyendo de forma compacta a un bucle `for` combinado con un `if` interno:

```python
# Filtrar únicamente los puertos considerados críticos, usando comprensión de listas
puertos_detectados = [21, 22, 23, 80, 443, 445, 3389]
puertos_criticos = [21, 23, 445, 3389]

hallazgos_criticos = [p for p in puertos_detectados if p in puertos_criticos]
print(hallazgos_criticos)   # [21, 23, 445, 3389]
```

### Utilidad y Ventajas de la Comprensión de Listas

La principal ventaja de la comprensión de listas frente al uso de un bucle `for` tradicional con `append()` es la **concisión**: una operación que normalmente ocuparía entre tres y cinco líneas de código puede expresarse en una única línea, sin que ello implique una pérdida de claridad, siempre que la expresión utilizada se mantenga razonablemente simple.

Esto está directamente alineado con la filosofía de diseño de Python expresada en el Zen de Python, particularmente con el principio de que el código bello es preferible al código feo, y de que las soluciones simples son preferibles a las complejas. Una comprensión de listas bien escrita comunica de forma casi inmediata su intención: "generar una nueva lista a partir de esta secuencia, aplicando esta transformación y este filtro", sin que el lector deba seguir mentalmente el flujo de inicialización de una lista vacía, su posterior llenado iterativo y su eventual retorno.

Además de la legibilidad, la comprensión de listas ofrece, en la práctica totalidad de los casos, un **mejor rendimiento** que su equivalente escrito mediante un bucle `for` explícito. Esto se debe a que la comprensión de listas está optimizada internamente por el intérprete de Python, evitando parte de la sobrecarga asociada a las llamadas repetidas al método `append()` dentro de un bucle.

Por estas razones, en el ecosistema de Python se considera una buena práctica recurrir a la comprensión de listas siempre que la transformación a realizar sea razonablemente simple, reservando el uso de un bucle `for` tradicional para aquellos casos en los que la lógica involucrada sea lo suficientemente compleja como para que forzarla dentro de una comprensión de listas termine perjudicando, en lugar de favorecer, la legibilidad del código.

```python
# Ejemplo aplicado a ciberseguridad: extraer solo los hosts activos de una lista de resultados
resultados_escaneo = [
    {"host": "192.168.1.10", "activo": True},
    {"host": "192.168.1.11", "activo": False},
    {"host": "192.168.1.12", "activo": True},
]

hosts_activos = [r["host"] for r in resultados_escaneo if r["activo"]]
print(hosts_activos)   # ['192.168.1.10', '192.168.1.12']
```
