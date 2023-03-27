from enum import Enum
import queue
import random
import threading
import time
from Utils import *


class Block:

    def __init__(self, id):
        self.id = id  # Identificador del bloque
        self.state = State.INVALID  # Estado inicial del bloque
        self.address = 0  # Dirección de memoria del bloque
        self.data = 0  # Dato almacenado en el bloque

    def __str__(self):
        return f'Block {self.id}:   {self.state.name[0]}\t{print_address_bin(self.address)}   {print_data_hex(self.data)}'

    def set(self, data):
        self.data = data

    def set(self, data, state):
        self.state = state
        self.data = data

    def set(self, address, data, state):
        self.state = state
        self.address = address
        self.data = data


# Clase que representa la caché de un procesador


class Cache:

    def __init__(self, id):
        self.lock = Lock()
        self.id = id  # Identificador de la caché
        # Diccionario de sets y bloques de la caché
        self.sets = {0: [Block(i) for i in range(2)], 1: [
            Block(i) for i in range(2, 4)]}
        # self.locks = {i: Lock() for i in range(4)}  # Diccionario de bloqueos para cada bloque de la caché

    def __str__(self):
        cache_str = f'\n ▶  Cache {self.id}\n'
        for set, blocks in self.sets.items():
            for block in blocks:
                cache_str += f'    ●  Set {set}\t{str(block)}\n'
        return cache_str[:-1]

    def _get_block(self, address):
        set = self.sets[address % 2]  # determinar el índice del conjunto
        for block in set:
            if block.address == address and block.state in [State.SHARED, State.MODIFIED, State.EXCLUSIVE]:
                return block
        return None

    def read(self, address):
        with self.lock:
            block = self._get_block(address)
            if block:
                return [True, block]
            return [False, None]

    # Write cuando se hace despues de consultar un dato, con política de escritura
    def write(self, address, data, state):
        with self.lock:
            index = address % 2
            set = self.sets[index]  # determinar el índice del conjunto
            for block in set:
                text = f' ✅ Cache {self.id}   ● Set {index}\t'
                if block.state == State.INVALID:
                    block.set(address, data, state)
                    text += f'{str(block)}'
                    print(f"\033[{GREEN}{text}\033[0m")
                    return None

            for block in set:
                if block.state == State.SHARED:
                    block.set(address, data, state)
                    text += f'{str(block)}'
                    print(f"\033[{GREEN}{text}\033[0m")
                    return None

            for block in set:
                if block.state == State.EXCLUSIVE:
                    block.set(address, data, state)
                    text += f'{str(block)}'
                    print(f"\033[{GREEN}{text}\033[0m")
                    return None

            # If we haven't returned yet, all blocks are MODIFIED, so evict one
            block = set[0]
            return block

    def invalidate(self, address):
        with self.lock:
            set = self.sets[address % 2]  # determinar el índice del conjunto
            for block in set:
                # El bloque se invalida si su direccion coincide con la recibida
                if block.address == address:
                    block.state = State.INVALID


# Clase que representa la memoria principal
class Memory:
    def __init__(self):
        # Diccionario de bloqueos de memoria principal
        self.blocks = {i: 0 for i in range(8)}
        # Diccionario de bloqueos para cada bloque de la caché
        self.locks = {i: threading.Lock() for i in range(8)}

    def __str__(self):
        memory_str = '\n ▶  Main Memory:\n'
        for address, data in self.blocks.items():
            memory_str += f'     {print_address_bin(address)}   :   {print_data_hex(data)}\n'
        return memory_str[:-1]

    def read(self, address):
        while self.locks[address]:
            data = self.blocks[address]
            print(
                f"\033[{YELLOW} RAM  ➞   📜 \t{print_address_bin(address)}  ≻  {print_data_hex(data)}\033[0m")
            return data
        return None

    def write(self, address, data):
        while self.locks[address]:
            self.blocks[address] = data
            print(
                f"\033[{YELLOW} RAM  ➞   ✏️ \t{print_address_bin(address)}  ≻  {print_data_hex(data)}\033[0m")
            return True
        return None


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
        text = f'    ◀  N{src_id}      {message_type.name}  to\tN{target.id}   |  {print_address_bin(address)}   {detail}'
        if detail == 'miss':
            print(f"\033[{RED}{text}\033[0m")
        else:
            print(f"\033[{GREEN}{text}\033[0m")
        target.controller._process_message(
            src_id, message_type, address, detail)
        return True

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


class Controller:
    def __init__(self, cache, bus):
        self.cache = cache  # Caché a la que está asociado el controlador
        self.bus = bus
        self.processors_list = []
        self.nodes_quantity = 2

    # Metodo para leer la cache local
    def read(self, sender, address, remote=False):
        # Verificar si el bloque está en caché
        [hit, block] = self.cache.read(address)

        if hit:
            if not remote:
                text = f' ✔️  Read Hit!   Cache {sender.id}    block: {block.id}    address: {address}    data: {block.data}'
                print(f"\033[{GREEN}{text}\033[0m")
            # Si el bloque está, se envia.
            return [True, block]

        if not remote:
            text = f' ❌  Read Miss!   Cache {sender.id}   addr: {print_address_bin(address)}'
            print(f"\033[{RED}{text}\033[0m")

            # Si el bloque NO está en caché, se solicita a otro.
            self.processors_list = []
            self.bus.add_request(sender, MessageType.RdReq, address)
        return [False, None]

    # Método para procesar un mensaje recibido
    def _process_message(self, sender, message_type, address, detail=None):

        if message_type == MessageType.RdReq:
            self._process_read_request(sender, address)
        elif message_type == MessageType.RdResp:
            self._process_read_response(sender, address, detail)
        elif message_type == MessageType.WrReq:
            self._process_write_request(sender, address, detail)
        elif message_type == MessageType.Inv:
            self._process_invalidation(sender, address, detail)
        elif message_type == MessageType.WB:
            self._process_write_back(sender, address, detail)

    # Método privado para procesar una solicitud de lectura
    def _process_read_request(self, sender, address):
        text = f' ▶  N{sender.id}   Read Request  ⟶   {print_address_bin(address)}'
        print(f"\033[{BLUE}{text}\033[0m")
        # Verificar si el bloque está en caché, es una consulta desde afuera.
        [hit, block] = self.read(sender, address, remote=True)

        if hit:
            # Si hit, se envía el bloque al procesador solicitante
            self.bus.add_response(
                self.cache.id, sender, MessageType.RdResp, address, block.data)

            if block.state == State.MODIFIED:
                # Si el bloque está en M, pasa a O
                block.state = State.OWNED

            elif block.state == State.EXCLUSIVE:
                # Si el bloque está en E, pasa a S
                block.state = State.SHARED

        else:
            # Si miss, se envia respuesta negativa
            self.bus.add_response(
                self.cache.id, sender, MessageType.RdResp, address, 'miss')

    def _process_read_response(self, src_id, address, detail):

        text = f'   ❣️\tN{self.cache.id}      RdResp from\t N{src_id}   |  {print_address_bin(address)}   {detail}'

        # Si el mensaje es un miss
        if detail == 'miss':
            print(f"\033[{RED}{text}\033[0m")
            self.processors_list.append(src_id)
            if len(self.processors_list) == (self.nodes_quantity-1):
                # Si no se encuentra en ninguno de los procesadores
                # Se lee desde memoria y pasa a un estado exclusivo
                data = self.bus.read(address)
                self.cache.write(address, data, State.EXCLUSIVE)
            return

        # Si el mensaje es un hit
        print(f"\033[{GREEN}{text}\033[0m")
        # Escribo el dato consultado, con política de escritura
        block = self.cache.write(address, detail, State.SHARED)

        if block is None:
            print(f'El procesador {src_id} ha brindado el bloque.')
            return

        # Si todos los bloque están en Modified
        # Se escribe el dato en la memoria principal
        self.bus.write(block.address, block.data)
        block.state = State.INVALID  # Se invalida el bloque, luego se modifica nuevamente
        # Se guarda el nuevo bloque en estado compartido.
        block = self.cache.write(address, detail, State.SHARED)

        # Si la operacion es exitosa
        if block is None:
            print(
                f'Se escribe correctamente en el block en la primera posicion por ser todos los blocks modified')


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
        operation = random.choice(['read', 'write', 'calc'])
        operation = 'read'
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
        self.controller.write(address, data)

    def calc(self):
        time.sleep(random.uniform(0.001, 0.01))

    def run(self):
        # Establecer el modo (paso a paso o automático)
        # modo = input("¿Qué modo quieres utilizar? (paso a paso / automático): ")

        # if modo == "1":
        # Modo paso a paso
        while True:

            # Esperar a que el usuario presione una tecla
            text = input("")

            if text == 's':
                self.bus.state()
                time.sleep(4)
                
            
            print(f"\033[{MAGENTA}\nProcessor {self.id}\033[0m")
            self.operate()


# Función principal
if __name__ == '__main__':
    bus = Bus()

    # Creamos 4 instancias de Procesador
    processors = [Processor(i, bus) for i in range(2)]

    # Creamos un hilo para cada instancia de Procesador
    threads = [threading.Thread(target=p.run) for p in processors]

    # Conectamos todos los procesadores al bus
    [bus.connect(p) for p in processors]

    # Empezar el bus
    bus.run()

    # Iniciamos todos los hilos
    for t in threads:
        t.start()

    # Esperamos a que todos los hilos terminen su ejecución
    for t in threads:
        t.join()
