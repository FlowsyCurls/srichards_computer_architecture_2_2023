from Memory import Memory
import queue
import threading
import time
from Utils import *

class Bus:
    def __init__(self):
        self.processors = []
        self.memory = Memory()
        self.lock = Lock()
        self.request_queue = queue.Queue()
        self.response_queue = queue.Queue()

    def connect(self, processor):
        self.processors.append(processor)
        print(f"  🔄️  Conectando N{processor.id}...")
        
    def state(self):
        for p in self.processors:
            print(p.cache)
        
        print(self.memory)

    # Método para leer un bloque de la memoria principal
    def read(self, address):
        with self.lock:
            return self.memory.read(address)

    # Método para escribir un bloque en la memoria principal
    def write(self, address, data):
        with self.lock:
            self.memory.write(address, data)

    # Metodo para agregar request a la cola
    def add_request(self, sender, message_type, address, detail=None):
        request = [sender, message_type, address, detail]
        self.request_queue.put(request)

    # Metodo para agregar respuesta a la cola
    def add_response(self, src_id, target, message_type, address, detail=None):
        response = [src_id, target, message_type, address, detail]
        self.response_queue.put(response)

    # Método para enviar un mensaje a todos los procesadores, excepto al que envió el mensaje
    def _process_request(self):
        request = self.request_queue.get()
        [sender, message_type, address, detail] = request
        for processor in self.processors:
            if processor != sender:
                processor.controller._process_message(
                    sender, message_type, address, detail)
        return True

    # Método para enviar un mensaje a un procesador en especific

    def _process_response(self):
        response = self.response_queue.get()
        [src_id, target, message_type, address, detail] = response
        
        if message_type == MessageType.InvResp:
            # Then is an invalidation.
            text = f'    ◀  N{src_id}      {message_type.name}  to\tN{target.id}   |  {print_address_bin(address)}'
            print(f"\033[{CIAN}{text}\033[0m")
            target.controller._process_message(src_id, message_type, address)
            return
            
        if message_type == MessageType.RdResp:
            text = f'    ◀  N{src_id}      {message_type.name}  to\tN{target.id}   |  {print_address_bin(address)}   {detail}'
            
            color = RED if detail == "miss" else GREEN
            print(f"\033[{color}{text}\033[0m")
            target.controller._process_message(src_id, message_type, address, detail)
            return

    def _process_taks(self):
        while True:
            # Procesar la solicitud aquí ...
            wait = True
            # print(f' ∎∎∎∎∎   Espero request')

            while wait:
                if not self.request_queue.empty():
                    wait = False
                    time.sleep(2)
            self._process_request()
            # print(f' ∎∎∎∎∎   Proceso request')

            wait = True
            # print(f' ∎∎∎∎∎   Espero response')
            while wait:
                if not self.response_queue.empty():
                    wait = False
                    time.sleep(1)
            # print(f' ∎∎∎∎∎   Proceso response')
            self._process_response()

    def run(self):
        for i in range(8):
            self.write(i, i)

        # Iniciar hilos de procesamiento de solicitudes
        for i in range(len(self.processors)):
            t = threading.Thread(target=self._process_taks)
            t.daemon = True
            t.start()
