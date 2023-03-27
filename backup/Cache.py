from threading import Lock
from Utils import State, print_bin, print_data_hex

# Clase que representa un bloque en la caché


class Block:
    def __init__(self, id):
        self.id = id  # Identificador del bloque
        self.state = State.INVALID  # Estado inicial del bloque
        self.address = 0  # Dirección de memoria del bloque
        self.data = 0  # Dato almacenado en el bloque

    def __str__(self):
        return f'Block {self.id}:   {self.state.name[0]}\t{print_bin(self.address)}   {print_data_hex(self.data)}'

    def set(self, address, data, state):
        self.state = state
        self.address = address
        self.data = data

    def set(self, data, state):
        self.state = state
        self.data = data

    def set(self, data):
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

    def check_hit(self, address):
        with self.lock:
            set = self.sets[address % 2]  # determinar el índice del conjunto
            for block in set:
                if block.address == address and block.state in [State.SHARED, State.MODIFIED, State.EXCLUSIVE]:
                    return True
                return False

    def read(self, address):
        with self.lock:
            block = self._get_block(address)
            if block:
                print(
                    f'\n ✔️  Read Hit!   Cache {self.id}: retriving block {block.id} data from address {address}')
                return block
            print(f'\n ❌  Read Miss!   Cache {self.id}')
            return None

    # Write cuando se hace loca.
    def write(self, address, data):
        with self.lock:
            block = self._get_block(address)
            if block:
                block.set(data, State.MODIFIED)
                print(
                    f'\n ✔️  Write Hit!   Cache {self.id}: writing block {block.id} with address \"{address}\" and data \"{data}\"')
                return True
            print(f'\n ❌  Write Miss!   Cache {self.id}')
            return None

    # Write cuando se hace despues de consultar un dato, con política de escritura
    def write(self, address, data, state):
        with self.lock:
            set = self.sets[address % 2]  # determinar el índice del conjunto
            for block in set:
                if block.state == State.INVALID:
                    block.set(address, data, state)
                    return [True, None]

            for block in set:
                if block.state == State.SHARED:
                    block.set(address, data, state)
                    return [True, None]

            for block in set:
                if block.state == State.EXCLUSIVE:
                    block.set(address, data, state)
                    return [True, None]

            # If we haven't returned yet, all blocks are MODIFIED, so evict one
            block = set[0]
            return [False, block]

    def invalidate(self, address):
        with self.lock:
            set = self.sets[address % 2]  # determinar el índice del conjunto
            for block in set:
                # El bloque se invalida si su direccion coincide con la recibida
                if block.address == address:
                    block.state = State.INVALID
