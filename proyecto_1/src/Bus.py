from Memory import Memory
import queue
import threading
import time
from Utils import *


class Bus:
    def __init__(self, memory_frame):
        self.memory_frame = memory_frame
        self.processors = []
        self.memory = Memory()
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
        # Refrescar la interfaz
        delay = int(random.uniform(1.5, 3)*CYCLE_DURATION)
        self.memory_frame.read(
            address=print_address_bin(address), delay=delay
        )
        return self.memory.read(address=address, delay=delay)

    # Método para escribir un bloque en la memoria principal
    def write(self, address, data):
        # Refrescar la interfaz
        delay = int(random.uniform(1.5, 3)*CYCLE_DURATION)
        info = self.memory.write(address=address, data=data, delay=delay/1000)
        self.memory_frame.write(
            address=print_address_bin(address), info=info, delay=delay
        )
        time.sleep(delay)  # Espera el tiempo de espera generado

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
                    sender, message_type, address, detail
                )
        return True

    # Método para enviar un mensaje a un procesador en especific

    def _process_response(self):
        response = self.response_queue.get()
        [src_id, target, message_type, address, detail] = response
        target.controller._process_message(src_id, message_type, address, detail)

    def _process_taks(self):
        while True:
            # Procesar la solicitud aquí ...
            wait = True
            while wait:
                if not self.request_queue.empty():
                    wait = False
                    time.sleep(0.1)
            self._process_request()

            wait = True
            while wait:
                if not self.response_queue.empty():
                    wait = False
                    time.sleep(0.1)
            self._process_response()

    def run(self):
        # Iniciar hilos de procesamiento de solicitudes
        for i in range(len(self.processors)):
            t = threading.Thread(target=self._process_taks)
            t.daemon = True
            t.start()
