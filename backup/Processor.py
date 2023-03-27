from enum import Enum
import random
import threading
import time

from Cache import Cache
from Controller import Controller
from Utils import MessageType


class ProcessorState(Enum):
    IDLE = 0
    READ = 1
    WRITE = 2


class Processor():
    def __init__(self, id, bus):
        super().__init__()
        self.id = id
        self.cache = Cache(id)
        self.bus = bus
        self.state = ProcessorState.READ
        self.controller = Controller(self.cache, self.bus)
        self.bus.connect(self)
        self.run()

    def run(self):
        # while True:
            # if self.state == ProcessorState.READ:
            #     self._process_message()
            #     self.state = ProcessorState.IDLE
            # elif self.state == ProcessorState.WRITE:
            #     self._process_message()
            #     self.state = ProcessorState.IDLE

        # Establecer el modo (paso a paso o automático)
        modo = input("¿Qué modo quieres utilizar? (paso a paso / automático): ")

        if modo == "1":
            # Modo paso a paso
            while True:
                
                # Esperar a que el usuario presione una tecla
                input("Presiona cualquier tecla para ejecutar la siguiente instrucción...")
                self._process_message
                self.operate()

        # elif modo == "2":
        #     # Modo automático
        #     intervalo = float(input("Introduce la frecuencia (en segundos): "))
        #     while True:
        #         # Generar una dirección aleatoria entre 0 y 7
        #         address = random.randint(0, 7)

        #         # Generar una operación aleatoria (lectura o escritura)
        #         operation = random.choice(['read', 'write'])

        #         # Realizar la operación correspondiente en la caché
        #         if operation == 'read':
        #             block = cache.read(address)
        #             print(f'Read from address {address}: {block}')
        #         else:
        #             cache.write(address, f'data_{address}')
        #             print(f'Write to address {address}')

        #         # Esperar el intervalo de tiempo especificado
        #         time.sleep(intervalo)
        # else:
        #     print("Modo no válido. Saliendo...")







    # def run(self):
    #     for i in range(10):
    #         print(f"Processor {self.cache.id} read: {self.controller.read(0)}")
    #         self.controller.write(0, i)
    #         print(f"Processor {self.cache.id} wrote: {i}")

    def receive_message(self, address, message_type):
        # Si el mensaje es para mi caché, lo proceso
        if self.cache.check_hit(address):
            pass
            # self.bus.process_message(self, address, message_type)
        # Si el mensaje no es para mi caché, lo ignoro
        else:
            pass
        
    # Método para procesar un mensaje recibido
    def _process_message(self, sender, address, message_type):
        if message_type == MessageType.Read:
            self.memory.read(address, sender)
        elif message_type == MessageType.Write:
            self.memory.write(address, sender.write_data)

                    
    def _process_message(self):
        if self.bus.messages.empty:
            pass
        print(message)
        # if message == 'RdResp':
        #     self.Controller.write(message['src'], message['data'])
        # elif message['type'] == 'Inv':
        #     self.Controller.invalidate(message['src'])
        # elif message['type'] == 'WB':
        #     self.Controller.write_back(message['src'], message['data'])


          
    def operate(self):
        # Generar una dirección aleatoria entre 0 y 7
        address = random.randint(0, 7)
        # Generar una operación aleatoria (lectura o escritura)
        operation = random.choice(['read', 'write', 'calc'])
        operation = 'read'
        if operation == 'read':
            print(f'Read from address {address}: ')
            self.read(address)
            
        elif operation == 'write':
            print(f'Write to address {address}')
            self.write(address, random.randint(0, 65535))
        elif operation == 'calc':
            self.calc()

    def read(self, address):
        self.controller.read(self, address)

    def write(self, address, data):
        self.controller.write(address, data)

    def calc(self):
        time.sleep(random.uniform(0.001, 0.01))
