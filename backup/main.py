import random
import time
from threading import Thread
from Bus import Bus
from Processor import Processor


# Función para generar una dirección de memoria aleatoria
def random_address():
    return random.randint(0, 7)

# Función para generar un dato aleatorio
def random_data():
    return random.randint(0, 255)

# Función que representa la ejecución de un hilo
def run_thread(processor):
    start_time = time.time()
    end_time = start_time + 5
    while time.time() < end_time:
        action = random.choice([Processor.Action.Read, Processor.Action.Write])
        address = random_address()
        if action == Processor.Action.Write:
            data = random_data()
            processor.run_action(action, address, data)
        else:
            processor.run_action(action, address)

# Función principal
if __name__ == '__main__':
    bus = Bus()
    # memory = Memory()
    # bus = Bus()
    proc1 = Processor(0, bus)
    proc2 = Processor(1, bus)
    proc1.start()
    proc2.start()
    proc1.join()
    proc2.join()
    
    # processors = [Processor(bus) for _ in range(4)]
    # threads = [Thread(target=p.run) for p in processors]
    # for t in threads:
    #     t.start()
    # for t in threads:
    #     t.join()

    # print("Estado final de la memoria principal:")
    # print(bus.memory.blocks)
    # for i, cache in enumerate(bus.caches):
    #     print(f"Estado final de la caché del procesador {i}:")
    #     print(cache.blocks)
