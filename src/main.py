import threading
from Processor import Processor
from Bus import Bus

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
