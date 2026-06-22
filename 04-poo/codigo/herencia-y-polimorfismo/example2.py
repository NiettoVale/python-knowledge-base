#!/usr/bin/env python3

class Vehiculo:
    def __init__(self, marca, modelo):
        self.marca = marca
        self.modelo = modelo
    
    def describir(self):
        raise NotImplementedError(
            f"La clase '{self.__class__.__name__}' debe implementar el método 'describir()'."
        )


# Herencia
class Auto(Vehiculo):
    pass
    # def describir(self):
    #     return f'Vehiculo: {self.marca} - Modelo: {self.modelo}'
    
class Moto(Vehiculo):
    def describir(self):
        return f'Moto: {self.marca} - Modelo: {self.modelo}'
    

moto = Moto("Honda", "CBR")
auto = Auto("Toyota", "Hilux")
# auto2 = Auto("Ford", "Ranger Raptor")
auto2 = Auto("Ford", "Ranger Raptor")

print(moto.describir())
print(auto.describir())
print(auto2.describir())
