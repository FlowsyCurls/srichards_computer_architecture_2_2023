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
        self.rd_wb_queue = queue.Queue()
        self.read_write_lock = False

    def connect(self, processor):
        self.processors.append(processor)
        print(f"  🔄️  Conectando N{processor.id}...")

    def state(self):
        for p in self.processors:
            print(p.cache)

        print(self.memory)

    ######################################################
    #   ACCIONES SOBRE LA MEMORIA
    ######################################################

    # Método para leer un bloque de la memoria principal
    def read(self, address):
        delay = random.uniform(1.2, 2) * CYCLE_DURATION
        # Sección crítica
        self.read_write_lock = True
        # Refrescar la interfaz
        self.memory_frame.read(
            address=print_address_bin(address), delay=int(delay * 1000)
        )
        data = self.memory.read(address=address)
        time.sleep(delay)  # Espera el tiempo de espera generado
        self.read_write_lock = False
        return data

    # Método para escribir un bloque en la memoria principal
    def write(self, address, data):
        delay = random.uniform(1.2, 2.5) * CYCLE_DURATION
        # Sección crítica
        self.read_write_lock = True
        # Refrescar la interfaz
        info = self.memory.write(address=address, data=data)
        self.memory_frame.write(
            address=print_address_bin(address), info=info, delay=int(delay * 1000)
        )
        time.sleep(delay)  # Espera el tiempo de espera generado
        self.read_write_lock = False

    ######################################################
    #   PROCESAMIENTO DE MENSAJES A MEMORIA
    ######################################################

    def _process_mem_task(self):
        while True:
            # Procesar la solicitud aquí ...
            wait = True
            while wait:
                if not self.rd_wb_queue.empty():
                    if not self.read_write_lock:
                        wait = False
                    time.sleep(CYCLE_DURATION * 2)

            self._process_read_wb()

    # Metodo para agregar request a la cola de wb o lectura de memoria
    def add_mem_request(self, sender_id, message_type, address, data=None):
        request = [sender_id, message_type, address, data]
        self.rd_wb_queue.put(request)

    # Metodo para agregar request a la cola WB y lectura de memoria.
    def _process_read_wb(self):
        request = self.rd_wb_queue.get()
        [sender, message_type, address, data] = request

        # Responder al procesador que se realizó el tramite.
        if message_type == MessageType.WB:
            self.write(address, data)
            sender.mem_action_done = True

        elif message_type == MessageType.RD:
            sender.tmp = self.read(address)
            sender.mem_action_done = True

    ######################################################
    #   PROCESAMIENTO DE MENSAJES ENTRE PROCESADORES
    ######################################################

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

    def _process_task(self):
        while True:
            # Procesar la solicitud aquí ...
            wait = True
            while wait:
                if not self.request_queue.empty():
                    wait = False
                    time.sleep(0.4)
            self._process_request()

            wait = True
            while wait:
                if not self.response_queue.empty():
                    wait = False
                    time.sleep(0.1)
            self._process_response()

    ######################################################
    #   EJECUCION
    ######################################################

    def run(self):
        # Iniciar hilos de procesamiento de solicitudes
        for i in range(len(self.processors)):
            t = threading.Thread(target=self._process_task)
            t.daemon = True
            t.start()

        tmem = threading.Thread(target=self._process_mem_task)
        tmem.daemon = True
        tmem.start()
