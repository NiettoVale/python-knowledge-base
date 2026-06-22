#!/usr/bin/env python3

class Animal:
    def __init__(self, nombre):
        self.nombre = nombre
        
    def hablar(self):
        pass

# Herencia
class Gato(Animal):
    def hablar(self):
        return '¡Miau!'

class Perro(Animal):
    def hablar(self):
        return '¡Guau!'

# Polimorfismo
def hacer_hablar(objeto):
    print(f"{objeto.nombre} dice {objeto.hablar()}")

gato = Gato('Firulais')
perro = Perro('Manchitas')

print(gato.hablar())
print(perro.hablar())

hacer_hablar(gato)
hacer_hablar(perro)
