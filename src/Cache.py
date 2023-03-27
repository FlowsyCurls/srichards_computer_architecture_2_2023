

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

    def invalidate(self):
        self.state = State.INVALID
        
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

    # Write cuando se hace local y cae encima.
    def write_local(self, address, data):
        with self.lock:
            # Se asume que se comprueba la existencia.
            block = self._get_block(address)
            block.set(data, State.MODIFIED)
            return block

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

