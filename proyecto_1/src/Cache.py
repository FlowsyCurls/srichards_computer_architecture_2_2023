from Utils import *


class Block:
    def __init__(self, id):
        self.id = id  # Identificador del bloque
        self.state = State.INVALID  # Estado inicial del bloque
        self.address = 0  # Dirección de memoria del bloque
        self.data = 0  # Dato almacenado en el bloque

    def __str__(self):
        return f"Block {self.id}:   {self.state.name[0]}\t{print_address_bin(self.address)}   {print_data_hex(self.data)}"

    def set(self, data):
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
        self.id = id  # Identificador de la caché
        # Diccionario de sets y bloques de la caché
        self.sets = {
            0: [Block(i) for i in range(2)],
            1: [Block(i) for i in range(2, 4)],
        }
        # self.locks = {i: Lock() for i in range(4)}  # Diccionario de bloqueos para cada bloque de la caché

    def __str__(self):
        cache_str = f"\n ▶  Cache {self.id}\n"
        for set, blocks in self.sets.items():
            for block in blocks:
                cache_str += f"    ●  Set {set}\t{str(block)}\n"
        return cache_str[:-1]

    def _get_block(self, address):
        set = self.sets[address % 2]  # determinar el índice del conjunto
        for block in set:
            if block.address == address and block.state in [
                State.SHARED,
                State.MODIFIED,
                State.EXCLUSIVE,
                State.OWNED,
            ]:
                return block
        return None

    def read(self, address):
        block = self._get_block(address)
        if block:
            return [True, block]
        return [False, None]

    # Funcion para invalidar
    def invalidate(self, address):
        # Se comprueba la existencia.
        block = self._get_block(address)
        if block is None:
            return [False, None]
        do_WB = True if block.state in [State.OWNED, State.MODIFIED] else False
        block.state = State.INVALID
        text = f" ✅ Cache {self.id}   ● Set {address % 2}\t{str(block)}"
        print(f"\033[{RED}{text}\033[0m")
        return [do_WB, block]

    def write(self, address, data, state):
        # Se comprueba la existencia.
        block = self._get_block(address)
        if block is None:
            return self._write(address, data, state)
        text = f" ✏️ Cache {self.id}   ● Set {address % 2}\t"

        # Si es owned lo modifico afuera.
        if block.state == State.OWNED:
            text += f"{str(block)}"
            print(f"\033[{GREEN}{text}\033[0m")
            return [State.OWNED, block]

        block.set(address, data, state)
        text += f"{str(block)}"
        print(f"\033[{GREEN}{text}\033[0m")
        return [State.SHARED, block]

    # Write cuando se hace despues de consultar un dato, con política de escritura
    def _write(self, address, data, state):
        index = address % 2
        set = self.sets[index]  # determinar el índice del conjunto
        do_WB = True
        text = f" ✏️ Cache {self.id}   ● Set {index}\t"
        for block in set:
            if block.state == State.INVALID:
                block.set(address, data, state)
                text += f"{str(block)}"
                print(f"\033[{GREEN}{text}\033[0m")
                return [State.INVALID, block]

        for block in set:
            if block.state == State.SHARED:
                block.set(address, data, state)
                text += f"{str(block)}"
                print(f"\033[{GREEN}{text}\033[0m")
                return [State.SHARED, block]

        for block in set:
            if block.state == State.EXCLUSIVE:
                block.set(address, data, state)
                text += f"{str(block)}"
                print(f"\033[{GREEN}{text}\033[0m")
                return [State.EXCLUSIVE, block]

        for block in set:
            if block.state == State.MODIFIED:
                block.set(address, data, state)
                text += f"{str(block)}"
                print(f"\033[{GREEN}{text}\033[0m")
                return [State.MODIFIED, block]

        # If we haven't returned yet, all blocks are OWNED, so evict one
        # Si es owned lo modifico afuera.
        block = set[0]
        text += f"{str(block)}"
        print(f"\033[{GREEN}{text}\033[0m")
        return [State.OWNED, block]
