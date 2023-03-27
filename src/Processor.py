from Memory import Memory
import time
from Cache import Cache
from Controller import Controller
from Utils import *


class Processor():
    def __init__(self, id, bus):
        self.id = id
        self.cache = Cache(id)
        self.bus = bus
        self.controller = Controller(self.cache, self.bus)

    def operate(self):
        # Generar una dirección aleatoria entre 0 y 7
        address = random.randint(0, 7)
        # Generar una operación aleatoria (lectura o escritura)
        operation = random.choice(['read', 'write', 'read','write'])
        # operation = 'write'
        if operation == 'read':
            print(f'Read from address {address}: ')
            self.read(address)
        elif operation == 'write':
            print(f'Write to address {address}')
            self.write(address, random.randint(0, 65535))
        elif operation == 'calc':
            print(f'Calc')
            self.calc()

    def read(self, address):
        self.controller.read(self, address)

    def write(self, address, data):
        self.controller.write(self, address, data)

    def calc(self):
        time.sleep(random.uniform(0.001, 0.01))

    def run(self):
        # Establecer el modo (paso a paso o automático)
        # modo = input("¿Qué modo quieres utilizar? (paso a paso / automático): ")

        # if modo == "1":
        # Modo paso a paso
        while True:

            # Esperar a que el usuario presione una tecla
            text = input("\n>  Press a key\n")

            if text == 's':
                self.bus.state()
                time.sleep(4)
                
            
            print(f"\033[{MAGENTA}\nProcessor {self.id}\033[0m")
            self.operate()

