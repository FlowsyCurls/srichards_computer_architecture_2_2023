import threading
from Utils import print_bin, print_data_hex


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
            memory_str += f'     {print_bin(address)}   :   {print_data_hex(data)}\n'
        return memory_str[:-1]

    def read(self, address):
        while self.locks[address]:
            data = self.blocks[address]
            print(
                f' RAM  ➞   📜     reading...\tdir   \"{print_bin(address)}\"  \tdata   \"{print_data_hex(data)}\"')
            return data
        return None

    def write(self, address, data):
        while self.locks[address]:
            self.blocks[address] = data
            print(
                f' RAM  ➞   ✏️      writing...\t dir   \"{print_bin(address)}\"  \t data   \"{print_data_hex(data)}\"')
            return True
        return None
