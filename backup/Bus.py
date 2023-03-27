
from threading import Lock
from Memory import Memory
from Utils import MessageType


class Bus:
    def __init__(self):
        self.processors = []
        self.lock = Lock()
        self.memory = Memory()
    
    def connect(self, processor):
        with self.lock:
            self.processors.append(processor)

    # Método para leer un bloque de la memoria principal
    def read(self, address):
        with self.lock:
            return self.memory.read(address)

    # Método para escribir un bloque en la memoria principal
    def write(self, address, data):
        with self.lock:
            self.memory.write(address, data)
                 
    # Método para enviar un mensaje a todos los procesadores, excepto al que envió el mensaje
    
    # si se recibe un mensaje el bus lo analiza y lo envia a los demas procesadores.
    def send_request(self, sender, address, message_type):
        with self.lock:
            for processor in self.processors:
                if processor != sender:
                    processor.controller._process_message(sender, address, message_type)
    
    # Método para enviar un mensaje a un procesador en especifico
    def send_response(self, receiver, address, message_type):
        with self.lock:
            receiver.controller._process_message(receiver, address, message_type)
                             
    # # Método para procesar un mensaje recibido
    # def _process_message(self, sender, address, message_type):
    #     with self.lock:
    #         if message_type == MessageType.Read:
    #             self.memory.read(address, sender)
    #         elif message_type == MessageType.Write:
    #             self.memory.write(address, sender.write_data)
    #         elif message_type == MessageType.Inv:
    #             for processor in self.processors:
    #                 if processor != sender:
    #                     processor.controller._process_invalidation(sender, address)
    #         elif message_type == MessageType.WriteBack:
    #             self.memory.write(address, sender.write_data)
    #             sender.controller._process_write_back(
    #                 sender, sender.write_data)



