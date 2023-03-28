import threading
from Processor import Processor
from Bus import Bus

import time


class System:
    def __init__(self):
        self.bus = Bus()
        # Creamos 4 instancias de Procesador
        self.processors = [Processor(i, self.bus) for i in range(2)]
        # Creamos un hilo para cada instancia de Procesador
        self.threads = [threading.Thread(target=p.execute) for p in self.processors]
        # Conectamos todos los procesadores al bus
        [self.bus.connect(p) for p in self.processors]
        # Empieza en modo manual
        self.auto_mode = False
        # Empezar el bus
        self.bus.run()


    def execute(self):
        for processor, thread in zip(self.processors, self.threads):
            if not processor.running:
                thread = threading.Thread(target=processor.execute)
                thread.start()
                self.threads[processor.id] = thread
            else:
                # Processor is still running, skip this cycle
                pass

        for thread in self.threads:
            thread.join()

    def execute_auto(self, time_interval):
        self.auto_mode = True
        while self.auto_mode:
            self.execute()
            time.sleep(time_interval)

    def execute_manual(self):
        self.auto_mode = False
        running = True
        while running:
            text = input("Press ENTER to execute one cycle of processors\n\n")
            if text == 's':
                self.bus.state()
                time.sleep(5)
            if text == 'q':
                running = False
                continue
            self.execute()


# Función principal
if __name__ == "__main__":
    system = System()
    # Execute in manual mode
    system.execute_manual()
    # Execute in automatic mode with one cycle every 2 seconds
    # system.execute_auto(2)