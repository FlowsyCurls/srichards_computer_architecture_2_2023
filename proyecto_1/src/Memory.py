
from Utils import *

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
                f"\033[{YELLOW} RAM  ➞  📜   reading • • •   {print_address_bin(address)}  ≻  {print_data_hex(data)}\033[0m")
            tiempo_espera = random.uniform(4, 7)
            time.sleep(tiempo_espera)             # Espera el tiempo de espera generado
            return data
        return None

    def write(self, address, data):
        while self.locks[address]:
            self.blocks[address] = data
            print(
                f"\033[{YELLOW} RAM  ➞  ✏️   writing • • •   {print_address_bin(address)}  ≻  {print_data_hex(data)}\033[0m")
            tiempo_espera = random.uniform(2, 4)
            time.sleep(tiempo_espera)             # Espera el tiempo de espera generado
            return True
        return None
