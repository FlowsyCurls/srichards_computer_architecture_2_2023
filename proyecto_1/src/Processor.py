from Memory import Memory
import time
from Cache import Cache
from Controller import Controller
from Utils import *


class Processor:
    def __init__(self, id, bus, cache_frame):
        self.id = id
        self.cache = Cache(id)
        self.cache_frame = cache_frame
        self.bus = bus
        self.controller = Controller(running=False, bus=self.bus, cache=self.cache, cache_frame=self.cache_frame)
        self.Instruction = ""

    def operate(self):
        # Generar una dirección aleatoria entre 0 y 7
        address = random.randint(0, 7)
        # Generar una operación aleatoria (lectura o escritura)
        operation = random.choice(["read", "write"])
        # operation = "read"
        if operation == "read":
            self.Instruction = f"READ  {print_address_bin(address)}"
            self.read(address)
        elif operation == "write":
            n = random.randint(0, 65535)
            self.Instruction = (
                f"WRITE {print_address_bin(address)}; {print_data_hex(n)}"
            )
            self.write(address, n)
        elif operation == "calc":
            self.Instruction = "CALC"
            self.calc()

        print(
            f"\033[{MAGENTA}\nProcessor {self.id}\033[0m\033[{WHITE}  {self.Instruction}\033[0m",
        )
        # Actualizar la instruction en pantalla
        self.cache_frame.set_instruction(self.Instruction)

    def read(self, address):
        self.controller.read(self, address)

    def write(self, address, data):
        self.controller.write(self, address, data)

    def calc(self):
        time.sleep(random.uniform(0.001, 0.01))

    def execute(self):
        self.controller.running = True
        self.operate()
